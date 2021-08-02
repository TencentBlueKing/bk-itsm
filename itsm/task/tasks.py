# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
import datetime
from collections import defaultdict
from operator import itemgetter
from celery.schedules import crontab
from celery.task import periodic_task

from itsm.component.constants.task import (
    NEED_UPDATE_TASK_STATUS,
    RUNNING,
    SUSPENDED,
    DELETED,
    FAILED,
    SOPS_TASK_STARTED_STATUS,
    NEED_SYNC_STATUS,
    DEVOPS_STATUS,
    DEVOPS_RUNNING_STATUS,
    DEVOPS_FAILED_STATUS,
)
from itsm.component.esb.esbclient import client_backend
from itsm.component.apigw import client as apigw_client
from itsm.component.utils.lock import share_lock
from itsm.task.models import SopsTask, Task, SubTask
from itsm.ticket.models import TicketGlobalVariable

logger = logging.getLogger('celery')


def get_tasks_status(bk_biz_id, sops_task_ids):
    """批量查询任务状态"""

    res = client_backend.sops.get_tasks_status(
        {"__raw": True, "task_id_list": list(sops_task_ids), "bk_biz_id": bk_biz_id}
    )

    if not res.get('result', False):
        logger.error('sops_task_poller failed: {}'.format(res.get('message')))
        return None

    return res.get('data')


def get_task_detail(bk_biz_id, sops_task_id):
    """查询任务详情"""

    res = client_backend.sops.get_task_detail(
        {"__raw": True, "task_id": sops_task_id, "bk_biz_id": bk_biz_id, })
    if not res.get('result', False):
        logger.warning('sops_task_poller->get_task_detail({}) failed: {}'.format(sops_task_id,
                                                                                 res.get(
                                                                                     'message')))
        return None

    return res.get('data')


def get_task_status(bk_biz_id, sops_task_id):
    """查询各节点状态"""

    res = client_backend.sops.get_task_status(
        {"__raw": True, "task_id": sops_task_id, "bk_biz_id": bk_biz_id, })
    if not res.get('result', False):
        logger.warning('sops_task_poller->get_task_status({}) failed: {}'.format(sops_task_id,
                                                                                 res.get(
                                                                                     'message')))
        return None

    return res.get('data')


@periodic_task(run_every=(crontab(minute="*/2", )), ignore_result=True)
@share_lock()
def sops_task_poller(task_ids=None):
    """sops任务轮询
    同步任务状态，任务状态为FINISHED时，统计标签数据
    """
    # 支持查询指定task的状态
    if task_ids:
        sync_ids = Task.objects.filter(id__in=task_ids, status__in=NEED_SYNC_STATUS).values_list(
            'id', flat=True)
        running_sops_tasks = SopsTask.objects.filter(task_id__in=sync_ids)
    else:
        running_sops_tasks = SopsTask.objects.filter(state__in=[RUNNING, SUSPENDED])

    # 按照业务分组
    sops_task_group = defaultdict(set)
    for sops_task in running_sops_tasks:
        sops_task_group[sops_task.bk_biz_id].add(sops_task.sops_task_id)

    for bk_biz_id, sops_task_ids in sops_task_group.items():
        tasks_status = get_tasks_status(bk_biz_id, sops_task_ids)
        if not tasks_status:
            continue

        for status in tasks_status:
            sops_task = running_sops_tasks.get(sops_task_id=status['id'])
            sops_task_state = DELETED if status["is_deleted"] else status['status']['state']
            sops_task.state = sops_task_state
            sops_task.elapsed_time = status['status']['elapsed_time']
            if sops_task_state in SOPS_TASK_STARTED_STATUS and not sops_task.executor:
                detail = get_task_detail(bk_biz_id, sops_task.sops_task_id)
                sops_task.executor = detail["executor"]
                sops_task.start_time = detail["start_time"].rstrip("+0800").strip()
            sops_task.save()

            # 执行失败或未结束
            if sops_task_state in NEED_UPDATE_TASK_STATUS:
                Task.objects.filter(id=sops_task.task_id).update(status=sops_task_state)
                continue

            if sops_task_state != 'FINISHED':
                continue

            # 执行结束
            sops_task.finish_time = status['finish_time'].rstrip("+0800").strip()

            # 查询流程详情并补充detail信息到status中
            detail = get_task_detail(bk_biz_id, sops_task.sops_task_id)
            if not detail:
                continue

            pipeline_tree = detail['pipeline_tree']
            activities = pipeline_tree['activities']
            activities.update(
                {
                    pipeline_tree['start_event']['id']: pipeline_tree['start_event'],
                    pipeline_tree['end_event']['id']: pipeline_tree['end_event'],
                }
            )
            sops_task.executor = detail["executor"]
            sops_task.start_time = detail["start_time"].rstrip("+0800").strip()
            sops_task.sops_task_info.update(detail=detail)

            # 查询各节点状态
            status = get_task_status(bk_biz_id, sops_task.sops_task_id)
            if not status:
                continue

            cleaned_status = {}

            for node_id, node_info in status['children'].items():
                if node_id not in activities:
                    continue
                node_info.update(
                    {
                        'incoming': activities[node_id]['incoming'],
                        'outgoing': activities[node_id]['outgoing'],
                        'labels': activities[node_id]['labels'],
                        'type': activities[node_id]['type'],
                        'stage_name': activities[node_id].get('stage_name', ''),
                        'component_code': activities[node_id].get('component', {}).get('code',
                                                                                       'unknown'),
                    }
                )
                cleaned_status[node_id] = node_info
            status['children'] = cleaned_status
            sops_task.sops_task_info.update(status=status)
            sops_task.save()

            # 内部定制逻辑
            do_after_sops_task_finished(sops_task.id)

            # 结束处理后的统一通知和触发器
            sops_task.task.do_after_finish_operate(operator='system')


def get_step_label_type(labels, default_label=2):
    """1：发布准备, 2：操作执行, 3：DB变更, 4：DB备份, 5：现网测试"""

    ops_types = {
        'ExecuteTask': 2,
        'PrepareTask': 1,
        'DbChange': 3,
        'DbBackup': 4,
        'TestOnline': 5,
    }

    for label in labels:
        if label['group'] == 'TimerGroup':
            return ops_types.get(label['label'], default_label)

    return default_label


def get_step_list_data(status, executor):
    """按照启动时间排序"""

    steps = [
        {
            # 节点开始执行时间
            "start_time": step['start_time'][:-6],
            # 插件code
            "tag_code": step['component_code'],
            # 插件name
            "tag_name": step['name'],
            # 执行结果：success/fail
            "result": "success",
            # 执行人
            "operator": executor,
            # 1：发布准备, 2：操作执行, 3：DB变更, 4：DB备份, 5：现网测试
            "type": get_step_label_type(step['labels']),
            # 节点结束执行时间
            "end_time": step['finish_time'][:-6],
        }
        for step_id, step in status['children'].items()
        if step['component_code'] != 'unknown'
    ]

    return sorted(steps, key=itemgetter('start_time'))


def get_tag_data(status):
    """根据标准运维的标签进行数据分析"""

    tag_data = {
        # 完全成功-1|成功但有问题-2|发布失败-1m
        "isSuccess": 1 if status['state'] == 'FINISHED' else 2,
        # 实际开始时间m
        "actualBeginTime": status['start_time'][:-6],
        # 实际结束时间m
        "actualEndTime": status['finish_time'][:-6],
        # 任务准备时长m
        "prepareTime": 0,
        # 运维执行时长m
        "executeTime": status['elapsed_time'],
        # 现网测试时长m
        "testTime": 0,
        # 停机比例：0-100
        "reviewNumerator": 1,
        # 是否停机发布m
        "reviewIsShutdown": 0,
        # 停机耗费时长
        "reviewShutdownTime": 0,
        # 是否DB发布
        "reviewIsDbChange": 1,
        # DB耗费时长
        "dbBackupTime": 1,
        "reviewDbChangeTime": 1,
        # 发布经验总结
        "conclusion": "",
    }

    is_shutdown, total_time = 0, 0
    stop_time, start_time = None, None
    for node_id, node_info in status['children'].items():
        labels = node_info['labels']
        for label in labels:
            if label['group'] == 'TimerGroup':
                elapsed_time = node_info['elapsed_time']
                if label['label'] == 'ExecuteTask':
                    tag_data['executeTime'] += elapsed_time
                elif label['label'] == 'PrepareTask':
                    tag_data['prepareTime'] += elapsed_time
                elif label['label'] == 'TestOnline':
                    tag_data['testTime'] += elapsed_time
                elif label['label'] == 'DbChange':
                    tag_data['reviewDbChangeTime'] += elapsed_time
                    tag_data['reviewIsDbChange'] = 1
                elif label['label'] == 'DbBackup':
                    tag_data['dbBackupTime'] += elapsed_time

                total_time += elapsed_time
            elif label['group'] == 'AreaOpsGroup':
                elapsed_time = node_info['elapsed_time']
                if label['label'] == 'StopService':
                    stop_time = datetime.datetime.strptime(
                        node_info['start_time'].rstrip("+0800").strip(), '%Y-%m-%d %H:%M:%S'
                    )
                    is_shutdown = 1
                elif label['label'] == 'StartService':
                    start_time = datetime.datetime.strptime(
                        node_info['start_time'].rstrip("+0800").strip(), '%Y-%m-%d %H:%M:%S'
                    )
                total_time += elapsed_time

    if stop_time and start_time:
        shutdown_time = (start_time - stop_time).seconds
        shutdown_percent = shutdown_time / total_time * 100
        tag_data.update(
            {
                'reviewIsShutdown': is_shutdown,
                'reviewShutdownTime': shutdown_time,
                'reviewNumerator': int(shutdown_percent),
            }
        )

    return tag_data


def do_after_sops_task_finished(sops_task_id):
    """统计任务数据"""

    sops_task = SopsTask.objects.get(pk=sops_task_id)
    task = sops_task.task

    status = sops_task.sops_task_info.get('status')
    tag_data = get_tag_data(status)
    logger.info("sops_task get_tag_data is {}".format(tag_data))

    # 标准运维任务退出前同步任务标签数据到总结阶段
    for tag_key, tag_value in tag_data.items():
        task.all_fields.filter(key=tag_key).update(_value=tag_value)

    # 更新sops任务信息到task.outputs
    task.outputs = {
        'tag_data': tag_data,
        'sops_step_list': get_step_list_data(status, sops_task.executor),
    }

    task.save()


@periodic_task(run_every=(crontab(minute="*/5", )), ignore_result=True)
@share_lock()
def devops_task_poller(task_ids=None):
    """蓝盾任务轮询"""
    if task_ids:
        sync_ids = Task.objects.filter(id__in=task_ids, status__in=NEED_SYNC_STATUS).values_list(
            'id', flat=True)
        devops_tasks = SubTask.objects.filter(task_id__in=sync_ids)
    else:
        devops_tasks = SubTask.objects.filter(state=RUNNING)

    for sub_task in devops_tasks:
        query_params = {
            "username": sub_task.executor,
            "project_id": sub_task.project_id,
            "pipeline_id": sub_task.sub_pipeline_id,
            "build_id": sub_task.sub_task_id,
        }
        try:
            task_status = apigw_client.devops.pipeline_build_status(query_params)
        except Exception as err:
            logger.exception(
                "[devops_task_poller] call pipeline_build_status error, msg is {}, query_params is {}".format(
                    err, query_params
                )
            )
            continue
        sub_task.elapsed_time = task_status["executeTime"]
        if task_status["status"] in DEVOPS_RUNNING_STATUS:
            sub_task.state = DEVOPS_STATUS.RUNNING
            task_state = RUNNING
        elif task_status["status"] in DEVOPS_FAILED_STATUS:
            sub_task.state = DEVOPS_STATUS.FAILED
            task_state = FAILED
        else:
            sub_task.state = task_status["status"]
            task_state = task_status["status"]
            if task_status["status"] == DEVOPS_STATUS.SUCCEED:
                task_state = None
                sub_task.finish_time = datetime.datetime.now()
                variables = task_status["variables"]
                artifact_list = task_status.get("artifactList", [])
                global_vars = []
                for key, value in variables.items():
                    global_vars.append(
                        TicketGlobalVariable(
                            ticket_id=sub_task.task.ticket_id,
                            state_id=sub_task.task.state_id,
                            key="{}.{}".format(sub_task.task.name, key),
                            name="{}[{}]".format(key, sub_task.task.name),
                            value=value,
                        )
                    )
                for artifact in artifact_list:
                    global_vars.append(
                        TicketGlobalVariable(
                            ticket_id=sub_task.task.ticket_id,
                            state_id=sub_task.task.state_id,
                            key="{}.{}".format(sub_task.task.name, artifact["path"]),
                            name="{}[{}]".format(artifact["path"], sub_task.task.name),
                            value=artifact["path"],
                        )
                    )
                TicketGlobalVariable.objects.bulk_create(global_vars)
                sub_task.task.do_after_finish_confirm(operator=sub_task.executor)
        sub_task.save()

        if task_state:
            Task.objects.filter(id=sub_task.task_id).update(status=task_state)

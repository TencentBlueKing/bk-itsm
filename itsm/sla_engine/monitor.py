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

import datetime
import json

from celery.schedules import crontab
from celery.task import periodic_task, task
from django.db import transaction

from common.redis import Cache
from itsm.sla.models import Action
from itsm.sla_engine.actions import SlaTaskAction
from itsm.sla_engine.constants import SLA_ACTION_TIME, RUNNING, REPLY_WARING, REPLY_TIMEOUT
from itsm.sla_engine.models import SlaTask
from itsm.ticket.models import Ticket


@task
def action_exclude(ac_key, ac_value, ac_time):
    ticket_id, sla_task_id, action_policy_type = [int(item) for item in ac_key.split("-")]
    sla_task = SlaTask.objects.get(id=sla_task_id)

    if sla_task.task_status != RUNNING:
        return

    action_ids = json.loads(ac_value)
    ticket = Ticket._objects.get(id=ticket_id)

    with transaction.atomic():
        for action in Action.objects.filter(id__in=action_ids):
            sla_task_action = SlaTaskAction(action, ticket, sla_task, action_policy_type, ac_time)
            sla_task_action.alert()


@periodic_task(run_every=datetime.timedelta(seconds=30))
def sla_task_metric():
    """
    1、获取redis内当前分钟的任务
    2、任务异步分发
    name: time, ac_key: {ticket_id}-{sla_task_id}-{action_policy_type}, ac_value: [action_id]
    """
    sla_redis_inst = Cache("SLA")
    # 任务更新时间
    current_time = datetime.datetime.now()
    ac_time = (current_time - datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
    ac_time_dict = sla_redis_inst.hgetall(ac_time)

    update_sla_task(ac_time_dict, current_time)

    # 任务分发
    for ac_key, ac_value in ac_time_dict.items():
        action_exclude.apply_async(args=[ac_key, ac_value, ac_time])

    sla_redis_inst.delete(ac_time)
    sla_redis_inst.srem(SLA_ACTION_TIME, ac_time)


@periodic_task(run_every=(crontab(minute="*/10", )), ignore_result=True)
def compensate_task():
    """
    补偿遗漏的提醒任务
    """
    sla_redis_inst = Cache("SLA")
    # 任务更新时间
    current_time = datetime.datetime.now()
    now = current_time.strftime("%Y-%m-%d %H:%M")
    action_times = sla_redis_inst.smembers(SLA_ACTION_TIME)
    compensate_time = []
    for item in action_times:
        if item < now:
            compensate_time.append(item)

    for ac_time in compensate_time:
        ac_time_dict = sla_redis_inst.hgetall(ac_time)
        update_sla_task(ac_time_dict, current_time)

        # 任务分发
        for ac_key, ac_value in ac_time_dict.items():
            action_exclude.apply_async(args=[ac_key, ac_value, ac_time])

        sla_redis_inst.delete(ac_time)
        sla_redis_inst.srem(SLA_ACTION_TIME, ac_time)


@periodic_task(run_every=(crontab(minute="*/10", )), ignore_result=True)
def rebuild_sla_task():
    """
    根据SlaTask表中RUNNING的任务重建入库redis失败的任务
    """
    sla_tasks = SlaTask.objects.filter(task_status=RUNNING)
    for sla_task in sla_tasks:
        action_policies = sla_task.action_policies
        if sla_task.is_reply_need and not sla_task.is_replied:
            action_policies = action_policies.exclude(type__in=[REPLY_WARING, REPLY_TIMEOUT])
        ac_keys = sla_task.get_ac_keys(action_policies)


def update_sla_task(ac_time_dict, current_time):
    sla_task_ids = []
    for ac_key, ac_value in ac_time_dict.items():
        _, sla_task_id, _ = [int(item) for item in ac_key.split("-")]
        sla_task_ids.append(sla_task_id)
    # 更新任务状态与耗时
    for sla_task in SlaTask.objects.filter(id__in=sla_task_ids):
        sla_task.update_cost_duration(current_time)
        sla_task.update_sla_status(current_time)

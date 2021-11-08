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

# celery 任务示例
# 
# 本地启动celery命令: python  manage.py  celery  worker  --settings=settings
# 周期性任务还需要启动celery调度命令：python  manage.py  celerybeat --settings=settings

import datetime
import hashlib
import json
import os

from celery import task
from django.conf import settings
from django.db import connection
from django.db.models import F
from django_bulk_update.helper import bulk_update

from common.log import logger
from itsm.component.constants import DEFAULT_STRING, REJECT_OPERATE
from itsm.component.utils.basic import dotted_name
from itsm.helper.utils import (
    build_field_kwargs,
    fix_bk_biz_id,
    fix_cmdb_snap,
    fix_default_value_for_field,
    fix_deleted_logs,
    fix_end_logs,
    fix_field_meta,
    fix_followers,
    fix_general_snap,
    fix_invite_comment,
    fix_person_snap,
    fix_role,
    fix_ticket,
    fix_ticket_eventlog,
    fix_workflow_snapshot,
    fix_workflow_states,
    fix_workflow_version_fields_json,
    migrate_processors_for_ticket,
    update_event_type_field,
    update_fault_level_field,
)
from itsm.iadmin.models import SystemSettings
from itsm.role.models import UserRole
from itsm.service.models import OldSla, Service, ServiceCatalog
from itsm.ticket.models import Ticket, TicketEventLog, TicketField
from itsm.workflow.models import DefaultField, Field, State, Workflow, WorkflowVersion


@task
def _db_fix_for_blueapps_after_2_6_0():
    """
    blueapps的数据升级
    """
    migrations = (
        ('account', '0002_init_superuser'),
        ('account', '0003_verifyinfo')
    )
    if settings.RUN_VER != "open":
        logger.Exception("当前运行环境为:{}，不支持db_fix_for_blueapps_after_2_6_0方法".format(
            settings.RUN_VER))
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT `app`, `name` FROM django_migrations;')
            rows = cursor.fetchall()
            for migration in migrations:
                if migration in rows:
                    continue
                dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                cursor.execute(
                    "INSERT INTO `django_migrations` (`app`, `name`, `applied`) VALUES (\"{}\", \"{}\", \"{}\");".format(
                        migration[0], migration[1], dt))
    except BaseException as err:
        logger.Exception(str(err))


@task
def _db_fix_for_workflow_to_2_5_9():
    """
    流程任务的数据升级
    """

    def create_task(instances):
        for workflow in instances:

            task_settings = workflow.extras.get("task_settings")
            if not task_settings or isinstance(task_settings, list):
                continue

            try:
                task_config = [
                    dict(
                        task_schema_id=schema_id,
                        create_task_state=task_settings['create_task_state'],
                        execute_task_state=task_settings['execute_task_state'],
                        execute_can_create=task_settings.get('execute_can_create', False),
                        need_task_finished=task_settings.get('need_task_finished', False),
                    )
                    for schema_id in task_settings.get('task_schema_ids', [])
                ]
                workflow.create_task(task_config)
            except BaseException as err:
                logger.Exception(str(err))
                continue

    create_task(Workflow.objects.all())
    create_task(WorkflowVersion.objects.all())


@task
def _db_fix_for_service_catalog():
    """服务目录添加前置路径"""
    print('start execute _db_fix_for_service_catalog')
    for s_c in ServiceCatalog.objects.all():
        s_c.route = list(s_c.get_ancestors(include_self=True).values("id", "name"))
        s_c.save(update_fields=("route",))
        print('fix: s_c: %s' % s_c.id)
    print('finish execute _db_fix_for_service_catalog')


@task
def _db_fix_default_value_for_field():
    fix_default_value_for_field()


@task
def _db_fix_for_ticket_processors():
    migrate_processors_for_ticket()


@task
def _db_fix_for_attachments():
    """附件升级方案"""

    def update_workflow_fields():
        fields = Field._objects.filter(type="FILE").select_related("workflow", "state")
        for field in fields:
            base_file_path = os.path.join(
                "workflow_{workflow_id}_{state_id}".format(workflow_id=field.workflow_id, state_id=field.state_id),
                field.key,
            )
            new_choice = {}
            if isinstance(field.choice, dict):
                continue
            for file in field.choice:
                unique_key = hashlib.md5("{}{}".format(datetime.datetime.now(), file["name"]).encode())
                file_path = os.path.join(base_file_path, file["name"])
                new_choice[unique_key.hexdigest()] = dict(name=file["name"], path=file_path)
            field.choice = new_choice
        bulk_update(fields, update_fields=["choice"])

    def update_version_fields():
        flows = WorkflowVersion._objects.all()
        for flow in flows:
            for field_id, field in flow.fields.items():
                if field["type"] != "FILE":
                    continue
                base_file_path = os.path.join(
                    "workflow_{workflow_id}_{state_id}".format(
                        workflow_id=field["workflow_id"], state_id=field["state_id"]
                    ),
                    field["key"],
                )
                new_choice = {}
                if isinstance(field["choice"], dict):
                    continue
                for file in field["choice"]:
                    unique_key = hashlib.md5("{}{}".format(datetime.datetime.now(), file["name"]).encode())
                    file_path = os.path.join(base_file_path, file["name"])
                    new_choice[unique_key.hexdigest()] = dict(name=file["name"], path=file_path)
                field["choice"] = new_choice
        bulk_update(flows, update_fields=["fields"])

    def update_ticket_fields():
        ticket_fields = TicketField._objects.filter(type="FILE").select_related("ticket")
        for field in ticket_fields:
            if field.choice:
                for item in WorkflowVersion._objects.get(id=field.ticket.flow_id).fields.values():
                    if item["key"] == field.key:
                        field.choice = item["choice"]
                        break

            field_value = {}
            base_file_path = os.path.join(
                "{ticket_id}_{state_id}".format(ticket_id=field.ticket_id, state_id=field.state_id), field.key,
            )
            for ticket_file in field.value.split(","):
                if not ticket_file:
                    continue

                unique_key = hashlib.md5("{}{}".format(datetime.datetime.now(), ticket_file).encode())
                file_path = os.path.join(base_file_path, ticket_file)
                field_value[unique_key.hexdigest()] = dict(path=file_path, name=ticket_file)
            field._value = json.dumps(field_value)
        bulk_update(ticket_fields, update_fields=["_value", "choice"])

    update_workflow_fields()
    update_version_fields()
    update_ticket_fields()


@task
def _db_fix_from_2_1_x_to_2_2_1():
    """
    流程引擎版本升级迁移：
        未结束单据迁移 -> 服务绑定的流程版本迁移 -> 流程迁移 （必须按顺序）
    """

    if SystemSettings.objects.filter(key="_db_fix_from_2_1_x_to_2_2_1").exists():
        return
    task_start = datetime.datetime.now()
    SystemSettings.objects.create(
        key="_db_fix_from_2_1_x_to_2_2_1", value="start: %s" % task_start, type="DATETIME",
    )

    kwargs = build_field_kwargs()
    Ticket.objects.upgrade_running_tickets(**kwargs)
    for ticket in Ticket.objects.filter(current_status="RUNNING", is_draft=False):
        ticket.node_status.filter(state_id=ticket.first_state_id).update(
            processors_type="PERSON", processors=dotted_name(ticket.creator)
        )
    Service.objects.upgrade_services_flow(**kwargs)
    Workflow.objects.upgrade_workflow(for_migrate=True, **kwargs)

    bad_states = [state.id for state in State.objects.all() if state.followers_type in ["", None, "OPEN"]]
    State.objects.filter(pk__in=bad_states).update(followers_type="EMPTY")

    Workflow._objects.filter(flow_type=DEFAULT_STRING).update(flow_type=F("service"))

    DefaultField.objects.update(related_fields={})

    end_tickets = Ticket.objects.filter(current_status__in=["FINISHED", "TERMINATED"]).values_list("id", flat=True)
    TicketField.objects.filter(ticket_id__in=end_tickets, source_type="API").update(source_type="CUSTOM")

    end_tickets = Ticket.objects.filter(current_status__in=["FINISHED", "TERMINATED"]).values_list("id", flat=True)
    TicketField.objects.filter(ticket_id__in=end_tickets, source_type="API").update(source_type="CUSTOM")

    TicketEventLog.objects.filter(message__in=["流程开始", "单据流程结束"]).update(source="SYS")

    task_end = datetime.datetime.now()
    SystemSettings.objects.filter(key="_db_fix_from_2_1_x_to_2_2_1").update(
        value="start: %s, end: %s, use: %s" % (task_start, task_end, (task_end - task_start))
    )
    logger.info("-------------------db_fix_from_2_1_x_to_2_2_1: finished ------------------------\n")


@task
def _db_fix_from_1_1_22_to_2_1_x():
    """V1.1.x到V2.1.x的数据升级接口（建议提前做好数据备份）"""

    if SystemSettings.objects.filter(key="_db_fix_from_1_1_22_to_2_1_16").exists():
        logger.info("_db_fix_from_1_1_22_to_2_1_x exists")
        return

    SystemSettings.objects.create(
        key="_db_fix_from_1_1_22_to_2_1_16", value=datetime.datetime.now(), type="DATETIME",
    )
    logger.info("_db_fix_from_1_1_22_to_2_1_x start")
    try:
        _fix_ticket_title()
        _update_logs_type()
        _db_fix_after_2_0_3()
        Ticket.objects.filter(is_draft=False, current_status="FINISHED", end_at__isnull=True).update(
            end_at=F("update_at")
        )
        for log in TicketEventLog.objects.filter(type="CLAIM", deal_time=0):
            log.update_deal_time()
        _db_fix_after_2_0_7()
        _db_fix_after_2_0_9()
        _db_fix_after_2_0_14()
        _db_fix_after_2_1_x()
        _db_fix_after_2_1_1()
        logger.info("_db_fix_from_1_1_22_to_2_1_x success")
    except Exception as e:
        logger.info("_db_fix_from_1_1_22_to_2_1_x fail: %s" % str(e))


@task
def _db_fix_after_2_0_3():
    """
    修复数据库数据：
    1、去掉中文名
    2、多人存储的字符串前后追加逗号（解决越权问题）
    """
    version = "V2.0.3"

    try:
        cnt0 = fix_ticket()
        cnt1 = fix_role()
        cnt2 = fix_workflow_states()
        cnt3 = fix_workflow_snapshot()
        cnt4 = fix_ticket_eventlog()
        cnt5 = fix_invite_comment()
        cnt6 = fix_followers()
        logger.info(
            "{}：数据库升级成功，修改数据：\n"
            "fix_ticket={}\n"
            "fix_role={}\n"
            "fix_workflow_states={}\n"
            "fix_workflow_snapshot={}\n"
            "fix_ticket_eventlog={}\n"
            "fix_invite_comment={}\n"
            "fix_followers={}\n".format(version, cnt0, cnt1, cnt2, cnt3, cnt4, cnt5, cnt6)
        )
        logger.info("db_fix_after_2_0_3 success!")
    except Exception as e:
        logger.error("db_fix_after_2_0_3 fail! error: %s" % str(e))


@task
def _db_fix_after_2_0_7():
    """
    日志新增处理人员快照
    """
    version = "V2.0.7"
    try:
        start = datetime.datetime.now()
        print(("_db_fix_after_2_0_7 start: %s" % str(start)))

        fix_person_snap()
        fix_general_snap()
        fix_cmdb_snap()
        fix_deleted_logs()
        fix_bk_biz_id()
        fix_end_logs()

        end = datetime.datetime.now()
        print(("_db_fix_after_2_0_7 end-start: %s - %s = %s" % (end, start, end - start)))
        logger.info("db_fix_after_2_0_7 success!")
    except Exception as e:
        logger.error("db_fix_after_2_0_7 fail! version: %s, error: %s" % (version, str(e)))


@task
def _db_fix_after_2_0_9():
    try:
        cnt = 0
        for ticket in Ticket.objects.filter(
            current_status__in=["DISTRIBUTING", "DISTRIBUTING-RECEIVING"], current_assignor_type="PERSON",
        ):
            flag = 0
            if not ticket.current_assignor.startswith(","):
                ticket.current_assignor = ",{}".format(ticket.current_assignor)
                flag += 1
            if not ticket.current_assignor.endswith(","):
                ticket.current_assignor = "{},".format(ticket.current_assignor)
                flag += 1

            if flag > 0:
                cnt += 1
                print(("刷新数据：%s" % ticket.sn))
                ticket.save()
        role_fix_cnt = 0
        for ticket in Ticket.objects.filter(
            current_status__in=["DISTRIBUTING", "DISTRIBUTING-RECEIVING"],
            current_assignor_type__in=["CMDB", "GENERAL"],
        ):

            if "," in ticket.current_assignor:
                ticket.current_assignor = ticket.current_assignor.replace(",", "")
                ticket.save()
                role_fix_cnt += 1
                print(("刷新数据：%s，第%s条" % (ticket.sn, role_fix_cnt)))

        logger.info("db_fix_after_2_0_9 success!")
    except Exception as e:
        logger.error("db_fix_after_2_0_9 fail! error: %s" % str(e))


@task
def _db_fix_after_2_1_x():
    """
    第二次数据迁移：
    根据当前的流程（包括软删除的）创建对应的流程最新的版本
    更新单据的类型: service->service_type
    跟新单据流程版本flow、服务目录catalog、服务条目service:
        服务条目根据最新流程版本聚合
    单据快照->单据关联流程版本
    """
    fix_field_meta()
    update_event_type_field()
    update_fault_level_field()
    Ticket.objects.update_ticket_service_type()
    Ticket.objects.update_ticket_catalog_and_service()
    Ticket.objects.update_ticket_flow_id()
    Ticket.objects.filter(current_status="RECEIVING").update(current_status="RUNNING")
    # 删除权限页面的管理员
    UserRole.objects.filter(
        role_key__in=[
            "CHANGE_MANAGER",
            "EVENT_MANAGER",
            "REQUEST_MANAGER",
            "QUESTION_MANAGER",
            "PUBLIC_MANAGER",
            "RELEASE_MANAGER",
            "DEPLOY_MANAGER",
        ]
    ).delete()


@task
def _db_fix_after_2_0_14():
    try:
        Ticket.objects.filter(current_status="FINISHED", current_processors_type="OPEN").update(
            current_processors_type=""
        )
        logger.info("db_fix_after_2_0_14 success!")
    except Exception as e:
        logger.error("db_fix_after_2_0_14 fail! error: %s" % str(e))


@task
def _db_fix_after_2_1_1():
    try:
        TicketEventLog.objects.filter(message__contains="驳回").update(type=REJECT_OPERATE)
        logger.info("db_fix_after_2_1_1 success!")
    except Exception as e:
        logger.error("db_fix_after_2_1_1 fail! error: %s" % str(e))


@task
def _fix_ticket_title():
    tickets = Ticket.objects.filter(is_deleted=False, is_draft=False)
    try:
        for ticket in tickets:
            title = ticket.fields.filter(key="title").first()
            if title:
                ticket.title = title._value
                ticket.save()
        logger.info("fix_ticket_title success!")
    except Exception as e:
        logger.error("fix_ticket_title fail! error: %s" % str(e))


@task
def _update_logs_type():
    try:
        TicketEventLog.objects.filter(message__contains="】终止，原因:【").update(type="TERMINATE", is_valid=True)
        logger.info("update_logs_type success!")
    except Exception as e:
        logger.error("update_logs_type fail! error: %s" % str(e))


@task
def _db_fix_sla():
    try:
        choices = OldSla.objects.values("name", "level", "resp_time", "deal_time", "id", "desc", "key", "is_builtin")
        need_fix_query = TicketField.objects.filter(key="fault_level", create_at__gte="2019-05-25 00:00:00")
        need_fix_query.update(choice=choices)
        choices_dict = {str(choice["id"]): choice["key"] for choice in choices}
        for field in need_fix_query:
            field._value = choices_dict.get(field._value, field._value)
            field.save()
            logger.info("fix %s, _value: %s" % (field.id, field._value))
    except Exception as e:
        logger.error("_db_fix_sla fail! error: %s" % str(e))


@task
def _db_fix_after_2_1_9():
    try:
        TicketField.objects.update(related_fields={})
        DefaultField.objects.update(related_fields={})
        Field.objects.update(related_fields={})
        fix_workflow_version_fields_json()
        logger.info("_db_fix_after_2_1_9 success")
    except Exception as e:
        logger.error("_db_fix_after_2_1_9 fail!, error: %s" % str(e))


@task
def _db_fix_ticket_end_at_after_2_0_5():
    try:
        Ticket.objects.filter(is_draft=False, current_status="FINISHED", end_at__isnull=True).update(
            end_at=F("update_at")
        )
        logger.info("_db_fix_ticket_end_at_after_2_0_5 success")
    except Exception as e:
        logger.error("_db_fix_ticket_end_at_after_2_0_5 fail!, error: %s" % str(e))


@task
def _db_fix_deal_time_after_2_0_5():
    try:
        for log in TicketEventLog.objects.filter(type="CLAIM", deal_time=0):
            log.update_deal_time()
        logger.info("_db_fix_deal_time_after_2_0_5 success")
    except Exception as e:
        logger.error("_db_fix_deal_time_after_2_0_5 fail!, error: %s" % str(e))

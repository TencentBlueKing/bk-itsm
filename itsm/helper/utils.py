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
import re
import time
from functools import wraps

import six
from django.db import connection
from django.db.models import F

from bulk_update.helper import bulk_update
from common.log import logger
from config.default import BIZ_GROUP_CONF, IS_BIZ_GROUP
from itsm.component.constants import DEFAULT_BK_BIZ_ID
from itsm.component.esb.esbclient import client_backend
from itsm.component.utils.basic import dotted_name
from itsm.postman.models import RemoteApi, RemoteApiInstance
from itsm.role.models import UserRole
from itsm.ticket.models import (
    Ticket,
    TicketComment,
    TicketEventLog,
    TicketField,
    TicketFollowerNotifyLog,
)
from itsm.workflow.models import Field, State, WorkflowSnap, WorkflowVersion


def fix_default_value_for_field():
    # TODO 进行default_value的迁移
    print("fix_default_value_for_field:start to migrate default value for 2.3")
    move_default_value_sql = 'UPDATE {table_name} SET {table_name}.default = {table_name}.default_value'
    drop_default_value = "ALTER table {table_name} DROP default_value"
    tables = ["workflow_templatefield", "workflow_field"]
    with connection.cursor() as cursor:
        for table_name in tables:
            print("fix_default_value_for_field:start to migrate table %s" % table_name)
            try:
                cursor.execute("select default_value from {}".format(table_name))
            except Exception as error:
                logger.info("error info : %s" % str(error))
                break
            cursor.execute(move_default_value_sql.format(table_name=table_name))
            cursor.execute(drop_default_value.format(table_name=table_name))
        print("fix_default_value_for_field: end migrate default value for 2.3")

        versions = WorkflowVersion.objects.all()
        for version in versions:
            for field in version.fields.values():
                field['default'] = field.pop('default_value', None) or field['default']
                field['source'] = field.get('source', 'CUSTOM')
            for field in version.table.get('fields', {}):
                field['default'] = field.pop('default_value', None) or field['default']
        bulk_update(versions, update_fields=["fields", "table"])


def migrate_processors_for_ticket():
    print("start migrate for ticket")
    history_processors_sql = (
        'update ticket_ticket '
        'left join (select ticket_id, GROUP_CONCAT(operator) as operator '
        'from ticket_ticketeventlog group by ticket_id ) as event_logs '
        'on event_logs.ticket_id = ticket_ticket.id '
        'set ticket_ticket.updated_by = concat(",", IFNULL(event_logs.operator, ""), ",")'
    )

    current_processors_sql = (
        'update ticket_ticket '
        'left join (select ticket_id, '
        'group_concat( processors) '
        'as processors from ticket_status '
        'where is_deleted = 0 and status not in ("TERMINATED","FAILED","FINISHED") '
        'group by ticket_id) as state '
        'on state.ticket_id = ticket_ticket.id '
        'set ticket_ticket.current_processors = concat(",", IFNULL(state.processors , ""), ",")'
    )
    with connection.cursor() as cursor:
        print("start execute current_processors_migrate_sql for ticket")
        cursor.execute(current_processors_sql)
        print("start execute history_processors_migrate_sql for ticket")
        cursor.execute(history_processors_sql)
        print("Task 'migrate_processors_for_ticket' is finished ")


def remove_bracket_content(name, add_extra=True):
    """
    字符串转换
    """

    # .*? -> 非贪婪匹配
    name = re.sub(r'\((.*?)\)', '', name)
    if name and add_extra:
        if not name.startswith(','):
            name = ',{}'.format(name)
        if not name.endswith(','):
            name = '{},'.format(name)
    return name


def time_this_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        result = func(*args, **kwargs)
        end = datetime.datetime.now()
        print((func.__name__, (end - start).seconds))
        return result

    return wrapper


def fix_workflow_version_fields_json():
    for version in WorkflowVersion.objects.all():
        fields = version.fields
        for value in list(fields.values()):
            if 'meta' in value and not isinstance(value['meta'], dict):
                value['meta'] = json.loads(value['meta'])
            if 'choice' in value and not isinstance(value['choice'], list):
                value['choice'] = json.loads(value['choice'])
            if 'related_fields' in value:
                value['related_fields'] = {}
        version.save()


@time_this_function
def fix_field_meta():
    wf_count = Field._objects.filter(meta="{}").update(meta={})
    print("fix_workflow_field_meta count: %s" % wf_count)
    tf_count = TicketField._objects.filter(meta="{}").update(meta={})
    print("fix_ticket_field_meta count: %s" % tf_count)


@time_this_function
def update_event_type_field():
    count = Field._objects.filter(key='event_type').update(source_type='DATADICT',
                                                           source_uri='EVENT_TYPE')
    print("update_event_type_field count: %s" % count)


@time_this_function
def update_fault_level_field():
    count = Field._objects.filter(key='fault_level').update(source_uri='service/slas')
    print("update_fault_level_field count: %s" % count)


def fix_ticket():
    print("fix_ticket's users")
    connection.close()
    print("connection close")

    start = time.time()
    change_flag = 0
    migrate_count = 0
    tickets = Ticket._objects.all()
    for ticket in tickets:
        # 建单人
        ticket.creator = remove_bracket_content(ticket.creator, False)

        if ticket.current_processors_type == 'PERSON':
            # if '(' in ticket.current_processors:
            change_flag += 1
            ticket.current_processors = remove_bracket_content(ticket.current_processors)

        if ticket.current_assignor_type == 'PERSON':
            # if '(' in ticket.current_assignor:
            change_flag += 1
            ticket.current_assignor = remove_bracket_content(ticket.current_assignor)

        if ticket.supervise_type == 'PERSON':
            change_flag += 1
            ticket.supervisor = remove_bracket_content(ticket.supervisor)

        if change_flag > 0:
            migrate_count += 1

        ticket.save()

    msg = "fix_ticket's users end, count: {}/{}, elapsed: {}s".format(
        migrate_count, tickets.count(), time.time() - start
    )

    logger.warning(msg)
    print(msg)

    return migrate_count


def fix_role():
    print("fix_user_role's members list")
    connection.close()
    print("connection close")

    for user_role in UserRole.objects.all():
        user_role.members = remove_bracket_content(user_role.members)
        user_role.save()

    return UserRole.objects.count()


def fix_invite_comment():
    print("fix_invite_comment's creator list")
    connection.close()
    print("connect.close")

    change_flag = 0
    for comment in TicketComment.objects.filter(source="WEB"):
        if '(' in comment.creator:
            comment.creator = remove_bracket_content(comment.creator, add_extra=False)
            comment.save()
            change_flag += 1

    return change_flag


def fix_followers():
    print("fix_followers's followers")
    connection.close()
    print("connection close")

    change_flag = 0
    for log in TicketFollowerNotifyLog.objects.filter(followers_type="PERSON"):
        log.followers = remove_bracket_content(log.followers)
        log.save()
        change_flag += 1
    return change_flag


def fix_ticket_eventlog():
    print("fix_ticket_eventlog start")
    connection.close()
    print("connection close")

    start = time.time()
    migrate_count = 0
    for event_log in TicketEventLog.objects.all():
        change_flag = 0
        # 当前处理人字段数据迁移
        # and '(' in event_log.processors:
        if event_log.processors_type == 'PERSON':
            change_flag += 1
            event_log.processors = remove_bracket_content(event_log.processors)

        # 操作人字段数据迁移
        if '(' in event_log.operator:
            change_flag += 1
            # 只有一个操作人的只需要纯英文
            event_log.operator = remove_bracket_content(event_log.operator, add_extra=False)

        if change_flag > 0:
            migrate_count += 1
            event_log.save()

            msg = 'migrate_event_log[{}]: {}'.format(migrate_count, event_log.id)
            logger.warning(msg)
            print(msg)

    msg = "fix_ticket_eventlog's processors end, count: {}, elapsed: {}s".format(migrate_count,
                                                                                 time.time() - start)

    logger.warning(msg)
    print(msg)

    return migrate_count


def fix_workflow_states():
    print("fix_workflow_state's processors and followers start")
    connection.close()
    print("connection close")

    start = time.time()
    migrate_state_count = 0
    for state in State._objects.all():

        change_flag = 0
        extra_change_flag = 0

        # 处理人字段数据迁移
        # and '(' in state.processors:
        if state.processors_type in ['PERSON', 'STARTER']:
            if state.processors_type == 'STARTER':
                try:
                    _ = int(state.processors)
                except ValueError:
                    change_flag += 1
                    state.processors = remove_bracket_content(state.processors)

            else:
                change_flag += 1
                state.processors = remove_bracket_content(state.processors)

        # 关注人字段数据迁移
        if state.followers_type == 'PERSON':  # and '(' in state.followers:
            change_flag += 1
            state.followers = remove_bracket_content(state.followers)

        # 分派人
        extras = state.extras
        # and '(' in extras.get('assignor'):
        if extras.get('assignor_type') == 'PERSON':
            extra_change_flag += 1
            extras.update(assignor=remove_bracket_content(extras.get('assignor')))

        # 转单人
        if extras.get('can_deliver'):  # and '(' in extras.get('deliver_to'):
            extra_change_flag += 1
            extras.update(deliver_to=remove_bracket_content(extras.get('deliver_to')))

        if extra_change_flag > 0:
            state.extras = extras

        if change_flag > 0 or extra_change_flag > 0:
            migrate_state_count += 1
            state.save()

            msg = 'migrate_state[{}]: {}'.format(migrate_state_count, state.id)
            logger.warning(msg)
            print(msg)

    msg = "fix_workflow_state's processors and followers end, count: {}, elapsed: {}s".format(
        migrate_state_count, time.time() - start
    )

    logger.warning(msg)
    print(msg)

    return migrate_state_count


def fix_workflow_snapshot():
    print("fix_workflow_snapshot start")
    connection.close()
    print("connection close")

    start = time.time()
    migrate_state_count = 0
    migrate_snap_count = 0
    extra_change_flag = 0

    for snap in WorkflowSnap.objects.all():
        snap_changed = False
        for state_id, state in six.iteritems(snap.states):
            change_flag = 0
            extra_change_flag = 0

            # 处理人字段数据迁移
            # and '(' in state.get('processors'):
            if state.get('processors_type') in ['PERSON', 'STARTER']:
                change_flag += 1
                state.update(processors=remove_bracket_content(state.get('processors')))

            # 关注人字段数据迁移
            # and '(' in state.get('followers'):
            if state.get('followers_type') == 'PERSON':
                change_flag += 1
                state.update(followers=remove_bracket_content(state.get('followers')))

            # 转单人
            extras = json.loads(state.get('extras'))
            # and '(' in extras.get('assignor'):
            if extras.get('assignor_type') == 'PERSON':
                extra_change_flag += 1
                extras.update(assignor=remove_bracket_content(extras.get('assignor')))

            # 分派人
            # and '(' in extras.get('deliver_to'):
            if extras.get('can_deliver'):
                extra_change_flag += 1
                extras.update(deliver_to=remove_bracket_content(extras.get('deliver_to')))

            if extra_change_flag > 0:
                state.update(extras=json.dumps(extras))

            if change_flag > 0 or extra_change_flag > 0:
                snap_changed = True
                migrate_state_count += 1
                # msg = 'migrate_snap_state[{}]: state_id = {}'.format(migrate_state_count, state_id)
                # logger.warning(msg)
                # print msg

        if snap_changed:
            migrate_snap_count += 1
            snap.save()

            msg = 'snap_changed[{}]: migrate_state_count = {}, extra_change_flag= {}'.format(
                snap.id, migrate_state_count, extra_change_flag
            )

            logger.warning(msg)
            print(msg)

    msg = "fix_workflow_snapshot end, count: {}, elapsed: {}s".format(migrate_snap_count,
                                                                      time.time() - start)

    logger.warning(msg)
    print(msg)

    return migrate_snap_count


def fix_open_snap():
    print("fix_open_snap start")

    start = datetime.datetime.now()
    print("start: %s" % start)

    connection.close()
    print("connection close")

    cnt = 0
    logs = TicketEventLog.objects.filter(processors_type="OPEN")
    for log in logs:
        log.processors_snap = dotted_name(log.operator)
        log.save()
        cnt += 1
        print(
            "更新日志成功：cnt={},log.id={},processors_snap={},operator={}".format(
                cnt, log.id, log.processors_snap, log.operator
            )
        )
    end = datetime.datetime.now()
    print("end-start: {} - {} = {}".format(end, start, end - start))

    print("fix_open_snap end")


def fix_person_snap():
    print("fix_person_snap start")

    start = datetime.datetime.now()
    print("start: %s" % start)

    connection.close()
    print("connection close")

    cnt = TicketEventLog.objects.filter(processors_type="PERSON").update(
        processors_snap=F("processors"))

    end = datetime.datetime.now()
    print("end-start: {} - {} = {}".format(end, start, end - start))

    print("fix_person_snap end: cnt=%s" % cnt)


def fix_general_snap():
    print("fix_general_snap start")
    start = datetime.datetime.now()
    print("start: %s" % start)

    connection.close()
    print("connection close")

    processors = (
        TicketEventLog.objects.filter(processors_type="GENERAL").order_by(
            "processors").distinct().values("processors")
    )
    cnt = 0
    for processor in processors:
        try:
            if not processor["processors"].isdigit():
                print(
                    'ignore illegal processors: {}({})'.format(
                        processor["processors"],
                        TicketEventLog.objects.filter(processors=processor["processors"]).values(
                            'id'),
                    )
                )
                continue

            members = UserRole._objects.get(id=processor["processors"]).members
            TicketEventLog.objects.filter(processors_type="GENERAL",
                                          processors=processor["processors"]).update(
                processors_snap=members
            )
        except UserRole.DoesNotExist:
            print("UserRole DoesNotExist: GENERAL %s" % processor["processors"])
            continue
        cnt += 1
        print(
            "更新日志成功：cnt={}, processors_type={}, processors={}, processors_snap={}".format(
                cnt, "GENERAL", processor["processors"], members
            )
        )

    end = datetime.datetime.now()
    print("end-start: {} - {} = {}".format(end, start, end - start))

    print("fix_general_snap end")


def fix_cmdb_snap():
    print("fix_cmdb_snap start")
    start = datetime.datetime.now()
    print("start: %s" % start)

    connection.close()
    print("connection close")

    def get_users(cmdb_role_key, bk_biz_id):
        info = client_backend.cc.search_business(
            {
                "bk_supplier_id": 0,
                "fields": [cmdb_role_key],
                "condition": {"bk_biz_id": bk_biz_id},
                "page": {"start": 0, "limit": 1000, "sort": ""},
            }
        ).get("info")
        if info:
            return info[0][cmdb_role_key]
        else:
            return ""

    processors = TicketEventLog.objects.filter(processors_type="CMDB").values("id", "processors",
                                                                              "ticket_id")
    cnt = 0
    for processor in processors:

        bk_biz_id = int(Ticket._objects.get(id=processor["ticket_id"]).get_field_value('bk_biz_id',
                                                                                       DEFAULT_BK_BIZ_ID))

        cmdb_role_key = None
        try:
            cmdb_role_key = UserRole._objects.get(id=processor["processors"]).role_key
        except UserRole.DoesNotExist:
            print("UserRole DoesNotExist: CMDB %s" % processor["processors"])

        if cmdb_role_key is None:
            continue

        users = dotted_name(get_users(cmdb_role_key, bk_biz_id))
        TicketEventLog.objects.filter(id=processor["id"]).update(processors_snap=users)
        cnt += 1
        print(
            "更新日志成功：cnt={}, processors_type={}, processors={}, ticket_id={}, processors_snap={}".format(
                cnt, "CMDB", processor["processors"], processor["ticket_id"], users
            )
        )
    end = datetime.datetime.now()
    print("end-start: {} - {} = {}".format(end, start, end - start))

    print("fix_general_snap end")


def fix_deleted_logs():
    print("fix_deleted_logs start")
    start = datetime.datetime.now()
    print("start: %s" % start)

    connection.close()
    print("connection close")

    deleted_tickets = Ticket._objects.filter(is_deleted=True).values_list("id", flat=True)
    cnt = TicketEventLog._objects.filter(ticket_id__in=deleted_tickets).update(is_deleted=True)

    end = datetime.datetime.now()
    print("end-start: {} - {} = {}".format(end, start, end - start))

    print("fix_deleted_logs end: cnt=%s" % cnt)


def fix_bk_biz_id():
    print("fix_bk_biz_id start")
    start = datetime.datetime.now()
    print("start: %s" % start)

    connection.close()
    print("connection close")

    values = TicketField.objects.filter(key="bk_biz_id", _value__isnull=False).values("id",
                                                                                      "_value",
                                                                                      "ticket_id")
    cnt = 0
    for value in values:
        try:
            Ticket._objects.filter(id=value["ticket_id"]).update(bk_biz_id=value["_value"])
            cnt += 1
            print(
                "更新单据成功：cnt={}, ticket_id={}, bk_biz_id={}, field_id={}".format(
                    cnt, value["ticket_id"], value["_value"], value["id"]
                )
            )
        except Exception as e:
            print(
                "更新出错：ticket_id={}, bk_biz_id={}, field_id={}, error={}".format(
                    value["ticket_id"], value["_value"], value["id"], e
                )
            )
    end = datetime.datetime.now()
    print("end-start: {} - {} = {}".format(end, start, end - start))

    print("fix_deleted_logs end")


def fix_end_logs():
    """
    修复正常结束单据的类型
    "TERMINATE" ——》 "TRANSITION"
    """
    print("fix_end_logs start")
    start = datetime.datetime.now()
    print("start: %s" % start)

    connection.close()
    print("connection close")

    TicketEventLog.objects.filter(message="单据流程结束", type="TERMINATE").update(type="TRANSITION")

    end = datetime.datetime.now()
    print("end-start: {} - {} = {}".format(end, start, end - start))

    print("fix_end_logs end")


def build_field_kwargs():
    """构建迁移所需的字段元素：api_instance, 数据字典"""
    from itsm.service.models import SysDict, DictData

    kwargs = {"is_biz_group": IS_BIZ_GROUP}
    if IS_BIZ_GROUP:
        search_inst_api = RemoteApi.objects.get(is_builtin=True, func_name='search_inst')
        group_instance = RemoteApiInstance.objects.create(
            remote_api=search_inst_api,
            req_params={},
            req_body={'bk_obj_id': BIZ_GROUP_CONF['biz_obj_id'], 'bk_supplier_account': '0'},
            rsp_data='data.info',
        )
        biz_instance = RemoteApiInstance.create_default_api_instance(
            func_name='search_business',
            req_params={},
            req_body={
                'fields': ['bk_biz_id', 'bk_biz_name'],
                'condition': {BIZ_GROUP_CONF['biz_property_id']: '${params_%s}' % BIZ_GROUP_CONF[
                    'biz_obj_id']},
            },
            rsp_data='data.info',
        )
        kwargs.update({'group_instance': group_instance, 'biz_instance': biz_instance})
    else:
        biz_instance = RemoteApiInstance.create_default_api_instance(
            func_name='search_business',
            req_params={},
            req_body={'fields': ['bk_biz_id', 'bk_biz_name']},
            rsp_data='data.info',
        )
        kwargs.update({'biz_instance': biz_instance})

    fault_level_init = {
        'level_1': '一级故障',
        'level_2': '二级故障',
        'level_3': '三级故障',
        'level_4': '四级故障',
    }
    builtin_dict = {
        'key': 'FAULT_LEVEL_INIT',
        'name': '故障级别',
    }
    obj, created = SysDict.objects.get_or_create(
        defaults={'is_builtin': True, 'name': builtin_dict['name'], 'updated_by': 'system',
                  'creator': 'system', },
        **{'key': builtin_dict['key'], }
    )
    DictData.create_builtin_dicts_data(obj, fault_level_init)
    return kwargs

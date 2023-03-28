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

import copy
import json
import operator
import time
from functools import reduce
from itertools import chain

from django.utils.functional import partition
from six.moves import zip

from django.db import models, connections, NotSupportedError
from django.db.models import F, Q, QuerySet, AutoField
from django.forms import model_to_dict
from django.utils.translation import ugettext as _

from common.log import logger
from itsm.component.constants import (
    CUSTOM_ACTION_OPERATE,
    DEFAULT_BK_BIZ_ID,
    DEFAULT_ENGINE_VERSION,
    DEFAULT_STRING,
    EMPTY_DICT,
    EMPTY_INT,
    FIELD_BACK_MSG,
    FIELD_TERM_MSG,
    FOLLOW_OPERATE,
    REJECT_OPERATE,
    SYS,
    SYSTEM_OPERATE,
    TRANSITION_OPERATE,
    WEB,
    SIGN_OPERATE,
    APPROVE_RESULT,
    FAILED,
    TASK_STATE,
    APPROVAL_STATE,
    RUNNING,
)
from itsm.component.db import managers
from itsm.component.utils.basic import create_version_number, dotted_name
from itsm.auth_iam.utils import IamRequest
from itsm.role.models import BKUserRole, UserRole
from itsm.service.models import ServiceCatalog
from itsm.ticket_status.models import TicketStatus
from itsm.workflow.backend import PipelineWrapper


class Manager(managers.Manager):
    """支持软删除"""

    pass


class StatusManager(Manager):
    """状态管理器"""

    def get_running_status(self, ticket_id=None):
        """查看执行中的状态"""

        running_status = self.filter(
            Q(status__in=self.model.CAN_OPERATE_STATUS)
            | Q(status=FAILED, type=TASK_STATE)
        )

        if ticket_id:
            running_status = running_status.filter(ticket_id=ticket_id)

        return running_status

    @staticmethod
    def build_role_filter(username):
        """暂未用到"""

        dotted_username = dotted_name(username)

        # PERSON
        filters = [
            Q(processors_type="PERSON") & Q(processors__contains=dotted_username),
        ]

        # GENERAL
        for role in UserRole.get_general_role_by_user(dotted_username):
            filters.append(
                Q(processors_type=role["role_type"])
                & Q(processors__contains=role["id"])
            )

        bk_user_roles = BKUserRole.get_or_update_user_roles(username)
        cmdb_roles, organization_ids = (
            bk_user_roles["cmdb"],
            bk_user_roles["organization"],
        )

        # CMDB
        for role, role_info in cmdb_roles.items():
            if not role_info["bizs"]:
                continue
            filters.append(
                Q(bk_biz_id__in=role_info["bizs"])
                & Q(processors_type="CMDB")
                & Q(processors__contains=role_info["role_id"])
            )

        # ORGANIZATION
        for organization_id in organization_ids:
            filters.append(
                Q(processors_type="ORGANIZATION")
                & Q(processors__contains=organization_id)
            )

        return reduce(operator.or_, filters)


class SignTaskManager(Manager):
    """会签任务表级操作"""

    pass


class TicketManager(Manager):
    """
    Ticket表级操作
    """

    @staticmethod
    def get_overall_statuses_tickets(queryset, current_statuses):
        """全局视图单据状态筛选
        current_statuses: "新,处理中,"
        """
        con = Q()
        key_list = current_statuses.split(",")
        ticket_statuses = TicketStatus.objects.filter(key__in=key_list).values(
            "service_type", "key"
        )
        for status in ticket_statuses:
            key_filter = Q()
            key_filter.connector = "AND"
            key_filter.children.append(("service_type", status["service_type"]))
            key_filter.children.append(("current_status", status["key"]))
            con.add(key_filter, "OR")

        return queryset.filter(con)

    @staticmethod
    def get_exclude_ticket_ids_tickets(queryset, exclude_ticket_ids):
        """排除指定单据"""
        exclude_ticket_id_list = exclude_ticket_ids.split(",")
        return queryset.exclude(id__in=exclude_ticket_id_list)

    def get_todo_tickets(self, queryset, username):
        """我的待办（包括任务）
        思路：我的待办节点->我的待办单据
        我的待办节点1：节点处理角色和处理人中包含我
        我的待办节点2 任务处理人中包含我
        """
        if not username:
            return queryset

        role_filter = self.build_todo_role_filter(username)
        closed_status = set(
            TicketStatus.objects.filter(is_over=True).values_list("key", flat=True)
        )
        return queryset.filter(role_filter).exclude(current_status__in=closed_status)

    def get_approval_tickets(self, queryset, username):
        from itsm.ticket.models.ticket import Status

        todo_ids = self.get_todo_tickets(queryset, username).values_list(
            "id", flat=True
        )

        running_node = Status.objects.filter(
            ticket_id__in=todo_ids, type=APPROVAL_STATE, status=RUNNING
        )
        closed_status = set(
            TicketStatus.objects.filter(is_over=True).values_list("key", flat=True)
        )

        # 如果run_node 是审批节点就算待我审批，不再细查
        my_approval_ticket = set(
            [
                node.ticket_id
                for node in running_node
                # if username in node.get_processor_in_sign_state().split(",")
            ]
        )
        return queryset.filter(id__in=my_approval_ticket).exclude(
            current_status__in=closed_status
        )

    def build_todo_role_filter(self, username):
        """current_processors的列表为混合内容，比如
        node1: GENERAL 1,2,3
        node2: PERSON zhangsan,lisi
        node3: CMDB 4,5 (与GENERAL位于同一张表, id不重复）
        node4: Organization 1,2,3
        -> ,1,2,3,zhangsan,lisi,4,5,O_1,O_2,O_3,
        """
        dotted_username = dotted_name(username)

        # PERSON
        # filters = [Q(current_processors__contains=dotted_username),
        # Q(id__in=list(self.get_followed_ticket(username)))]
        filters = [Q(current_processors__contains=dotted_username)]

        # GENERAL
        general_roles = UserRole.get_general_role_by_user(dotted_username)
        for role in general_roles:
            filters.append(Q(current_processors__contains=dotted_name(role["id"])))

        # CMDB
        bk_user_roles = BKUserRole.get_or_update_user_roles(username)
        cmdb_roles, organization_ids = (
            bk_user_roles["cmdb"],
            bk_user_roles["organization"],
        )

        for role, role_info in cmdb_roles.items():
            if not role_info["bizs"]:
                continue

            filters.append(
                Q(bk_biz_id__in=role_info["bizs"])
                & Q(current_processors__contains=dotted_name(role_info["role_id"]))
            )

        # ORGANIZATION
        for organization_id in organization_ids:
            filters.append(
                Q(
                    current_processors__contains=dotted_name(
                        "O_{}".format(organization_id)
                    )
                )
            )

        # 当前任务处理人
        filters.append(Q(current_task_processors__contains=dotted_username))
        # 任务处理人支持角色
        for role in general_roles:
            filters.append(Q(current_task_processors__contains=dotted_name(role["id"])))

        return reduce(operator.or_, filters)

    def get_history_tickets(self, queryset, username):
        """我处理过的单据（包括任务）"""

        dotted_username = dotted_name(username)
        return queryset.filter(
            Q(updated_by__contains=dotted_username)
            | Q(history_task_processors=dotted_username)
        )

    def get_iam_auth_tickets(self, queryset, username):
        iam_client = IamRequest(username=username)

        data = queryset.values("service_id", "project_key")
        service_project_key_map = {}
        service_ids = set()
        for item in data:
            service_ids.add(item["service_id"])
            service_project_key_map[item["service_id"]] = item["project_key"]

        resources = [
            {
                "resource_id": service_id,
                "resource_type": "service",
                "project_key": service_project_key_map.get(service_id),
            }
            for service_id in service_ids
        ]

        apply_actions = ["ticket_view"]
        auth_actions = iam_client.batch_resource_multi_actions_allowed(
            apply_actions, resources
        )
        return queryset.filter(
            service_id__in=[
                service_id
                for service_id, perm in auth_actions.items()
                if perm.get("ticket_view")
            ]
        )

    def get_created_tickets(self, queryset, username):
        """我创建的"""
        return queryset.filter(creator=username)

    def get_my_dealt_tickets(self, queryset, username):
        # TODO 需要确认该函数是什么意思？？

        operate_queryset = queryset.filter(logs__operator=username)
        values = operate_queryset.order_by("-logs__operate_at").values(
            "id", "logs__operate_at"
        )
        ids = []
        for value in values:
            if value["id"] not in ids:
                ids.append(value["id"])

        clauses = " ".join(
            ["WHEN id={} THEN {}".format(pk, i) for i, pk in enumerate(ids)]
        )
        ordering = "CASE %s END" % clauses

        queryset = queryset.filter(id__in=ids).extra(
            select={"ordering": ordering}, order_by=("ordering",)
        )

        return queryset

    def get_attention_tickets(self, queryset, username):
        """我关注的"""
        return queryset.filter(id__in=list(self.get_followed_ticket(username)))

    def get_tickets(self, username, queryset, **kwargs):
        """查询单据"""

        # 过滤非草稿单
        queryset = queryset.filter(is_draft=False)

        # 通用参数过滤

        keyword = kwargs.get("keyword")
        if keyword:
            queryset = queryset.filter(
                Q(sn__icontains=keyword) | Q(title__icontains=keyword)
            )

        filter_conditions = {
            key: value
            for key, value in dict(
                bk_biz_id=kwargs.get("bk_biz_id"),
                service_id=kwargs.get("service_id"),
                flow_id=kwargs.get("flow_id"),
                catalog_id__in=ServiceCatalog.get_descendant_ids(
                    kwargs.get("catalog_id")
                ),
                project_key=kwargs.get("project_key"),
                service_type=kwargs.get("service_type"),
            ).items()
            if value
        }

        queryset = queryset.filter(**filter_conditions)

        if kwargs.get("creator__in"):
            queryset = queryset.filter(creator__contains=kwargs.get("creator__in"))

        start_time = kwargs.get("create_at__gte")
        end_time = kwargs.get("create_at__lte")
        if start_time and end_time:
            # 同时有开始和结束时间才进行过滤？？
            queryset = queryset.filter(create_at__range=(start_time, end_time))

        current_processor = kwargs.get("current_processor")
        if current_processor:
            queryset = self.get_todo_tickets(queryset, current_processor)

        # 全局视图单据状态筛选
        if kwargs.get("overall_current_status__in"):
            return self.get_overall_statuses_tickets(
                queryset, kwargs.get("overall_current_status__in")
            )

        if kwargs.get("exclude_ticket_id__in"):
            return self.get_exclude_ticket_ids_tickets(
                queryset, kwargs.get("exclude_ticket_id__in")
            )

        view_type = kwargs.get("view_type", "")

        view_type_method = getattr(
            self, "get_{}_tickets".format(view_type.split("_")[-1]), None
        )
        if view_type_method is not None:
            return view_type_method(queryset, username)

        # 开放超级管理员/统计管理员视角
        # if not ignore_superuser and (UserRole.is_itsm_superuser(username) or UserRole.is_statics_manager(username)):
        #     return queryset

        # 统一通过权限管理来控制是否有单据查看权限

        myself_queryset = self.get_todo_tickets(
            queryset, username
        ) | self.get_history_tickets(queryset, username)
        iam_auth_queryset = self.get_iam_auth_tickets(queryset, username)
        return myself_queryset | iam_auth_queryset

    @staticmethod
    def get_followed_ticket(username):
        from itsm.ticket.models import AttentionUsers

        # Follower
        follow_tickets = AttentionUsers.objects.filter(follower=username).values_list(
            "ticket_id", flat=True
        )
        return list(follow_tickets)

    # ======================================数据迁移================================================

    def update_ticket_service_type(self):
        self.model._objects.filter(service_type=DEFAULT_STRING).update(
            service_type=F("service")
        )

    def update_ticket_flow_id(self):
        from itsm.workflow.models import WorkflowSnap, Workflow

        bad_ticket_cnt = 0
        for ticket in self.model._objects.all():
            try:
                workflow_snap = WorkflowSnap.objects.get(id=ticket.workflow_snap_id)
                workflow = Workflow._objects.get(id=workflow_snap.workflow_id)
                version = self.create_version_by_ticket_workflowsnap(
                    workflow, workflow_snap
                )
                ticket.flow_id = version.id
                ticket.save()
                print("%s: update flow_id for" % ticket.sn)
            except (WorkflowSnap.DoesNotExist, Workflow.DoesNotExist):
                print("%s: bad flow_id ticket" % ticket.sn)
        print("bad_ticket_cnt = %s" % bad_ticket_cnt)

    def update_ticket_catalog_and_service(self, *args, **kwargs):
        """
        根据服务及目录特性更新ticket
        """

        from itsm.workflow.models import WorkflowVersion
        from itsm.service.models import Service

        print("Ticket.update_ticket_catalog_and_service")

        ver_to_snaps = WorkflowVersion.objects.get_or_create_version_from_workflow()
        # print 'ver_for_snaps: %s' % ver_to_snaps

        ver_to_catalog_service = (
            Service.objects.get_or_create_service_and_catalog_from_version()
        )
        # print 'ver_for_service: %s' % ver_for_catalog_service

        # 外键到ticket
        for ver_pk, snaps in list(ver_to_snaps.items()):
            # service_catalog = CatalogService.objects.get(service_id=ver_for_service.get(ver_pk))
            service_catalog = ver_to_catalog_service.get(ver_pk)
            if not service_catalog:
                print("skip empty service_catalog: %s" % ver_pk)
                continue

            self.model._objects.filter(workflow_snap_id__in=snaps).update(
                catalog_id=service_catalog.catalog.id,
                service_id=service_catalog.service.id,
            )

            print("update ticket workflow: {}, cnt={}".format(ver_pk, len(snaps)))

    def create_version_by_ticket_workflowsnap(self, workflow, workflow_snap):
        """根据单据的流程快照创建流程版本，默认删除"""

        from itsm.workflow.models import WorkflowVersion

        data = model_to_dict(workflow)
        # remove and update some fields
        for field in [
            "id",
            "creator",
            "create_at",
            "end_at",
            "update_at",
            "notify",
            "updated_by",
            "service",
            "service_property",
            "_state",
        ]:
            data.pop(field, None)

        data.update(
            master=workflow_snap.master,
            creator="system",
            updated_by="system",
            workflow_id=workflow_snap.id,
            version_number=create_version_number(),
            version_message="version created.",
            states=workflow_snap.states,
            transitions=workflow_snap.transitions,
            fields=workflow_snap.fields,
            notify=list(workflow.notify.values_list("id", flat=True)),
            is_deleted=True,
        )
        notify = data.pop("notify", [])
        version = WorkflowVersion.objects.create(**data)
        version.notify = notify
        version.save()
        return version

    def upgrade_running_tickets(self, ticket_id=None, **kwargs):
        """迁移执行中的单据"""
        import os
        import datetime

        from distutils.dir_util import copy_tree
        from itsm.workflow.models import WorkflowVersion
        from itsm.ticket.models import TicketField
        from itsm.iadmin.models import SystemSettings

        upgrade_start = datetime.datetime.now()
        logger.info(
            "-------------------upgrade_running_tickets start: %s------------------------\n"
            % upgrade_start
        )

        old_flows = list(
            WorkflowVersion._objects.exclude(engine_version="PIPELINE_V1").values_list(
                "id", flat=True
            )
        )
        # old_flows = WorkflowVersion._objects.all()
        # 找到旧流程版本未结束的单据，并过滤掉草稿单、结束的单据
        running_tickets = self.filter(flow_id__in=old_flows, is_draft=False).exclude(
            current_status__in=["FINISHED", "TERMINATED"]
        )

        if ticket_id:
            running_tickets = running_tickets.filter(id=ticket_id)

        logger.info("total ticket: {}\n".format(running_tickets.count()))

        for ticket in running_tickets:
            start = datetime.datetime.now()
            # # avoid repetitive migrate
            if ticket.flow.engine_version == DEFAULT_ENGINE_VERSION:
                continue
            try:
                old_flow_id = ticket.flow_id
                # upgrade old flow version to pipeline version
                # logger.info('upgrade running ticket: {} version: {}'.format(ticket.id, old_flow_id))
                # print('upgrade running ticket: {} version: {}'.format(ticket.id, old_flow_id))
                (
                    new_flow,
                    states_map,
                    transition_map,
                ) = WorkflowVersion.objects.upgrade_version(
                    old_flow_id, for_migrate=True, ticket=ticket, **kwargs
                )
                # 刷新单据附件目录
                system_file_path = SystemSettings.objects.get(key="SYS_FILE_PATH").value

                for old_state_id, new_state_id in list(states_map.items()):
                    old_path = os.path.join(
                        system_file_path, "{}_{}".format(ticket.id, old_state_id)
                    )
                    if os.path.exists(old_path):
                        new_path = os.path.join(
                            system_file_path, "{}_{}".format(ticket.id, new_state_id)
                        )
                        copy_tree(old_path, new_path)

                old_ticket_status = ticket.current_status
                ticket.current_status = "RUNNING"
                ticket.current_state_id = str(
                    states_map.get(
                        int(ticket.current_state_id), ticket.current_state_id
                    )
                )
                ticket.flow_id = new_flow.id
                ticket.save()

                ticket.logs.update(workflow_id=new_flow.id)
                for old_state_id, new_state_id in list(states_map.items()):
                    ticket.logs.filter(from_state_id=old_state_id).update(
                        from_state_id=new_state_id
                    )
                    ticket.logs.filter(to_state_id=old_state_id).update(
                        to_state_id=new_state_id
                    )
                for o_t, n_t in list(transition_map.items()):
                    ticket.logs.filter(transition_id=o_t).update(transition_id=n_t)

                logger.info("create ticket fields")
                exists_fields = ticket.fields.exclude(
                    key__in=[FIELD_BACK_MSG, FIELD_TERM_MSG]
                )
                exists_fields_values = {
                    field["key"]: {
                        "choice": json.loads(field["choice"]),
                        "_value": field["_value"],
                        "meta": json.loads(field["meta"]),
                    }
                    for field in exists_fields.values("key", "choice", "_value", "meta")
                }
                exists_fields.delete()
                fields = []
                for state_id, state in list(new_flow.states.items()):
                    for field_id in state["fields"]:
                        field = copy.deepcopy(new_flow.get_field(field_id))
                        if not field:
                            continue
                        if (
                            field["key"] == "bk_biz_id"
                            and ticket.bk_biz_id == DEFAULT_BK_BIZ_ID
                        ):
                            continue
                        field.update(state_id=state_id)
                        field.update(ticket_id=ticket.id)
                        field.pop("id", None)
                        field.pop("workflow_id", None)
                        fields.append(TicketField(**field))
                TicketField.objects.bulk_create(fields)
                for field in ticket.fields.all():
                    values = exists_fields_values.get(field.key, None)
                    if values:
                        field._value = values["_value"]
                        field.choice = values["choice"]
                        field.meta = values["meta"]
                        field.save()
                ticket.save()

                # build migrate pipeline and start
                pipeline_wrapper = PipelineWrapper(
                    new_flow, ticket.id, for_migrate=True
                )
                pipeline_data = pipeline_wrapper.create_pipeline(
                    ticket.id,
                    root_pipeline_data={
                        "ticket_id": ticket.id,
                        "old_ticket_status": old_ticket_status,
                    },
                    need_start=True,
                    use_cache=True,
                )

                ticket.pipeline_data = pipeline_data
                ticket.save()

                # 自动回调
                virtual_states = (
                    ticket.logs.all()
                    .exclude(type=REJECT_OPERATE)
                    .values_list("from_state_id", flat=True)
                )
                virtual_states = list(set(list(virtual_states)))
                master_states = [
                    state["id"]
                    for state in WorkflowVersion._objects.get(id=old_flow_id).master
                ]
                re_map = dict(
                    list(zip(list(states_map.values()), list(states_map.keys())))
                )
                virtual_states.sort(key=lambda x: master_states.index(re_map.get(x)))
                try:
                    virtual_states.remove(int(ticket.current_state_id))
                except ValueError:
                    pass
                flag = True
                for state_id in virtual_states:
                    operator = (
                        ticket.logs.filter(from_state_id=state_id).last().operator
                    )
                    # 当前节点是提单节点
                    if str(new_flow.first_state["id"]) == ticket.current_state_id:
                        break
                    n = 20
                    while n > 0:
                        try:
                            ticket.activity_callback(
                                state_id=state_id,
                                operator=operator,
                            )
                            logger.info(
                                "activity_callback : ticket_id={}, state_id={}, operator={}".format(
                                    ticket.id, state_id, operator
                                )
                            )
                            break
                        except Exception:
                            time.sleep(0.5)
                            n -= 1
                            continue
                    # 当某个节点处理失败，则停止回调
                    if n <= 0:
                        flag = False
                        break
                end = datetime.datetime.now()
                if flag:
                    logger.info(
                        "migrate old flows running ticket_id: %s success, use: %s"
                        % (ticket.id, (end - start).seconds)
                    )
                else:
                    logger.error(
                        "migrate old flows running ticket_id: %s fail, use: %s"
                        % (ticket.id, (end - start).seconds)
                    )

            except Exception as e:
                end = datetime.datetime.now()
                logger.error(
                    "migrate error ticket_id: {}, error: {}, use: {}".format(
                        ticket.id, str(e), (end - start).seconds
                    )
                )

        upgrade_end = datetime.datetime.now()
        logger.info(
            "-------------------upgrade_running_tickets end: %s use %s------------------------\n"
            % (upgrade_end, upgrade_end - upgrade_start)
        )

    def get_master_ticket(self, ticket_id):
        """通过id获取到母单信息"""
        try:
            cur_instance = self.get(id=ticket_id)
        except self.model.DoesNotExist:
            return None

        if cur_instance.is_slave:
            # 子单返回母单信息
            return cur_instance.get_master_ticket()

        return cur_instance


class LogsSoftDeletQuerySet(QuerySet):
    """支持软删除"""

    def delete(self):
        return super(LogsSoftDeletQuerySet, self).update(is_deleted=True)


class LogsManager(models.Manager):
    """支持软删除"""

    def get_queryset(self):
        return LogsSoftDeletQuerySet(self.model).filter(is_deleted=False)


class TicketLogManager(LogsManager):
    """
    TicketLog表级操作
    """

    def create_start_log(self, ticket, source=WEB):
        """创建启动日志"""

        state_id = ticket.start_state["id"]
        transition_id = ticket.first_transition["id"]
        to_state_id = ticket.flow.transition_to_state(transition_id)

        # 创建开始流转日志
        return self.create_log(
            ticket,
            state_id,
            ticket.creator,
            operate_type=FOLLOW_OPERATE,
            message="流程开始.",
            transition_id=transition_id,
            to_state_id=to_state_id,
            source=source,
        )

    def create_end_log(self, ticket, message, end_operator="system", detail_message=""):
        """创建结束日志"""

        state_id = ticket.end_state["id"]

        # 创建结束流转日志
        return self.create_log(
            ticket,
            state_id,
            end_operator,
            message=message,
            detail_message=detail_message,
        )

    def create_log(
        self,
        ticket,
        state_id,
        log_operator,
        operate_type=TRANSITION_OPERATE,
        message="",
        action="",
        detail_message="",
        from_state_name="",
        transition_id=None,
        to_state_id=None,
        source=SYS,
        fields=None,
    ):
        """创建操作日志"""

        if operate_type == SYSTEM_OPERATE or str(state_id) == ticket.first_state_id:
            processors_snap = log_operator
        else:
            processors_snap = ",".join(
                set(
                    chain(
                        ticket.real_current_processors,
                        ticket.real_assignors,
                        ticket.real_supervisors,
                    )
                )
            )

        status = ticket.status(state_id)

        log = self.create(
            ticket=ticket,
            from_state_id=state_id,
            type=operate_type,
            operator=log_operator,
            message="%s..." % message[0:500]
            if len(message) > 500
            else message,  # 防止消息太长
            workflow_id=ticket.flow.id,
            processors_type=getattr(status, "processors_type", ""),
            processors=getattr(status, "processors", ""),
            processors_snap=dotted_name(processors_snap),
            source=source,
            action=action,
            detail_message=detail_message,
            from_state_name=from_state_name,
            status=getattr(status, "id", EMPTY_INT),
            form_data=fields or getattr(status, "fields", EMPTY_DICT),
            transition_id=transition_id,
            to_state_id=to_state_id,
        )

        ticket.set_history_operators(log_operator)

        return log

    def create_sign_state_log(
        self, ticket, node_status, log_operator, source, task_field_list
    ):
        processors_snap = ",".join(
            set(
                chain(
                    ticket.real_current_processors,
                    ticket.real_assignors,
                    ticket.real_supervisors,
                )
            )
        )
        # 获取会签任务处理结果
        result = ""
        for task_field in task_field_list:
            if task_field.get("meta", {}).get("code") == APPROVE_RESULT:
                result = task_field["display_value"]

        log = self.create(
            ticket=ticket,
            from_state_id=node_status.state_id,
            type=SIGN_OPERATE,
            operator=log_operator,
            message=_("{operator} {action}【{name}】(%s)") % result,
            workflow_id=ticket.flow.id,
            processors_type=getattr(node_status, "processors_type", ""),
            processors=getattr(node_status, "processors", ""),
            processors_snap=dotted_name(processors_snap),
            source=source,
            action=_("已处理"),
            detail_message="",
            from_state_name=node_status.name,
            status=node_status.id,
            form_data=task_field_list,
            transition_id=None,
            to_state_id=None,
        )
        return log

    def create_trigger_action_log(
        self, ticket, status, log_operator, component_cls, component_input_data
    ):
        """Record trigger action event log"""
        message = "{operator} {action}【{name}】."
        processors_snap = ",".join(
            set(
                chain(
                    ticket.real_current_processors,
                    ticket.real_assignors,
                    ticket.real_supervisors,
                )
            )
        )

        # Component inputs -> Event log form data
        component_inputs = component_cls.get_inputs()
        form_data = [
            {
                "name": item.get("label"),
                "display_value": component_input_data.get(item.get("name")),
                "show_result": True,
            }
            for item in component_inputs
        ]

        log = self.create(
            ticket=ticket,
            from_state_id=status.state_id,
            type=CUSTOM_ACTION_OPERATE,
            operator=log_operator,
            message=message,
            workflow_id=ticket.flow.id,
            processors_type=getattr(status, "processors_type", ""),
            processors=getattr(status, "processors", ""),
            processors_snap=dotted_name(processors_snap),
            source=WEB,
            action=component_cls.name,
            detail_message="",
            from_state_name=status.name,
            status=status.id,
            form_data=form_data,
            transition_id=None,
            to_state_id=None,
        )
        return log

    def get_latest_back_record(self, ticket_id, from_state_id):
        objs = self.filter(ticket_id=ticket_id, from_state_id=from_state_id).order_by(
            "-operate_at"
        )
        return objs[0] if objs.exists() else None

    def get_last_operator(self, ticket_id, from_state_id):
        """根据起始状态获取最近的单据操作人"""
        objects = self.filter(
            ticket_id=ticket_id, from_state_id=from_state_id
        ).order_by("-operate_at")
        if objects:
            return objects[0].operator
        return ""

    def is_state_operator(self, username, ticket_id, state_id):
        """是否处理过某个节点"""
        return self.filter(
            ticket_id=ticket_id, from_state_id=state_id, operator=username
        ).exists()

    def is_ticket_operator(self, username, ticket_id):
        """是否处理过某个单据"""
        return self.filter(ticket_id=ticket_id, operator=username).exists()


class TicketGlobalVariableManager(models.Manager):
    """
    全局变量表表级操作
    """

    def get_global_variables(self, ticket_id, state_id):
        """获取节点的全局变量列表"""

        return self.filter(ticket_id=ticket_id, state_id=state_id)


class TicketFieldManager(models.Manager):
    """
    TicketField表级操作
    """

    def _batched_insert(self, objs, fields, batch_size, ignore_conflicts=False):
        """
        Helper method for bulk_create() to insert objs one batch at a time.
        """
        if (
            ignore_conflicts
            and not connections[self.db].features.supports_ignore_conflicts
        ):
            raise NotSupportedError(
                "This database backend does not support ignoring conflicts."
            )
        ops = connections[self.db].ops
        max_batch_size = max(ops.bulk_batch_size(fields, objs), 1)
        batch_size = min(batch_size, max_batch_size) if batch_size else max_batch_size
        inserted_rows = []
        bulk_return = connections[self.db].features.can_return_rows_from_bulk_insert
        for item in [objs[i : i + batch_size] for i in range(0, len(objs), batch_size)]:
            if bulk_return and not ignore_conflicts:
                inserted_rows.extend(
                    self._insert(
                        item,
                        fields=fields,
                        using=self.db,
                        returning_fields=self.model._meta.db_returning_fields,
                        ignore_conflicts=ignore_conflicts,
                    )
                )
            else:
                self._insert(
                    item,
                    fields=fields,
                    using=self.db,
                    ignore_conflicts=ignore_conflicts,
                )
        return inserted_rows

    def _prepare_for_bulk_create(self, objs):
        for obj in objs:
            if obj.pk is None:
                # Populate new PK values.
                obj.pk = obj._meta.pk.get_pk_value_on_save(obj)
            obj._prepare_related_fields_for_save(operation_name="bulk_create")

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        """
        重写bulk_create方法，去除事务锁
        """
        assert batch_size is None or batch_size > 0
        for parent in self.model._meta.get_parent_list():
            if parent._meta.concrete_model is not self.model._meta.concrete_model:
                raise ValueError("Can't bulk create a multi-table inherited model")
        if not objs:
            return objs
        self._for_write = True
        connection = connections[self.db]
        opts = self.model._meta
        fields = opts.concrete_fields
        objs = list(objs)
        self._prepare_for_bulk_create(objs)
        objs_with_pk, objs_without_pk = partition(lambda o: o.pk is None, objs)
        if objs_with_pk:
            returned_columns = self._batched_insert(
                objs_with_pk,
                fields,
                batch_size,
                ignore_conflicts=ignore_conflicts,
            )
            for obj_with_pk, results in zip(objs_with_pk, returned_columns):
                for result, field in zip(results, opts.db_returning_fields):
                    if field != opts.pk:
                        setattr(obj_with_pk, field.attname, result)
            for obj_with_pk in objs_with_pk:
                obj_with_pk._state.adding = False
                obj_with_pk._state.db = self.db
        if objs_without_pk:
            fields = [f for f in fields if not isinstance(f, AutoField)]
            returned_columns = self._batched_insert(
                objs_without_pk,
                fields,
                batch_size,
                ignore_conflicts=ignore_conflicts,
            )
            if (
                connection.features.can_return_rows_from_bulk_insert
                and not ignore_conflicts
            ):
                assert len(returned_columns) == len(objs_without_pk)
            for obj_without_pk, results in zip(objs_without_pk, returned_columns):
                for result, field in zip(results, opts.db_returning_fields):
                    setattr(obj_without_pk, field.attname, result)
                obj_without_pk._state.adding = False
                obj_without_pk._state.db = self.db

        return objs

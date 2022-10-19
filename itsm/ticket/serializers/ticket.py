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

from collections import OrderedDict
from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.fields import JSONField, empty

from common.log import logger
from itsm.auth_iam.utils import IamRequest
from itsm.component.drf.serializers import AuthModelSerializer
from itsm.component.utils.client_backend_query import get_bk_users
from itsm.component.constants import (
    ACTION_CHOICES,
    ALL_ACTION_CHOICES,
    CLAIM_OPERATE,
    DEFAULT_BK_BIZ_ID,
    DEFAULT_ENGINE_VERSION,
    FIELD_BACK_MSG,
    FIELD_TERM_MSG,
    FINISHED,
    LEN_LONG,
    LEN_NORMAL,
    MASTER_SLAVE,
    PERSON,
    PROCESSOR_CHOICES,
    QUEUEING,
    RELATE_CHOICES,
    RUNNING,
    STATUS_CHOICES,
    TABLE,
    TASK_SOPS_STATE,
    TASK_DEVOPS_STATE,
    TASK_STATE,
    TASK_STATUS_DICT,
    SIGN_STATE,
    APPROVAL_STATE,
    STATE_BUTTON,
    DISTRIBUTING,
    RECEIVING,
    LEN_SHORT,
    REVOKE_TYPE,
    START_STATE,
    STARTER,
    LEN_XXX_LONG,
    EXCEPTION_DISTRIBUTE_OPERATE,
    WEBHOOK_STATE,
)
from itsm.component.dlls.component import ComponentLibrary
from itsm.component.exceptions import TriggerValidateError
from itsm.component.utils.basic import (
    better_time_or_none,
    dotted_name,
    generate_random_sn,
)
from itsm.component.utils.client_backend_query import get_biz_names, get_template_list
from itsm.component.utils.misc import transform_single_username, transform_username
from common.utils import html_escape
from itsm.postman.serializers import TaskStateApiInfoSerializer
from itsm.service.validators import service_validate
from itsm.sla_engine.constants import HANDLE_TIMEOUT, RUNNING as SLA_RUNNING, PAUSED
from itsm.ticket.models import (
    Service,
    Status,
    Ticket,
    TicketEventLog,
    TicketToTicket,
    UserRole,
    SignTask,
    TaskField,
    AttentionUsers,
    TicketCommentInvite,
    TicketComment,
    SlaTask,
    Sla,
    SlaTicketHighlight,
    TicketRemark,
)
from itsm.ticket.tasks import remark_notify
from itsm.ticket.utils import compute_list_difference
from itsm.workflow.models import WorkflowVersion
from itsm.ticket.serializers.field import (
    FieldSerializer,
    FieldSimpleSerializer,
    TableFieldSerializer,
    TaskFieldSerializer,
)
from itsm.ticket.validators import CreateTicketValidator, StateOperateValidator
from itsm.ticket_status.models import TicketStatus

BkUser = get_user_model()


class StatusSerializer(serializers.ModelSerializer):
    """节点状态序列化"""

    state_id = serializers.IntegerField()
    name = serializers.CharField(required=True, max_length=LEN_NORMAL)
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    tag = serializers.CharField(required=False, max_length=LEN_LONG)
    action_type = serializers.ChoiceField(choices=ACTION_CHOICES)
    processors = serializers.CharField(max_length=LEN_LONG)
    processors_type = serializers.ChoiceField(choices=PROCESSOR_CHOICES)
    assignors = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    assignors_type = serializers.ChoiceField(choices=PROCESSOR_CHOICES, required=False)
    delivers = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    delivers_type = serializers.ChoiceField(choices=PROCESSOR_CHOICES, required=False)
    can_deliver = serializers.BooleanField(required=False)
    can_terminate = serializers.BooleanField(required=False)

    contexts = JSONField(initial={})
    query_params = JSONField(initial={})

    class Meta:
        model = Status
        fields = (
            "id",
            "name",
            "ticket_id",
            "state_id",
            "status",
            "action_type",
            "can_terminate",
            "is_sequential",
            "tag",
            "processors_type",
            "processors",
            "assignors_type",
            "assignors",
            "origin_assignors",
            "origin_processors",
            "origin_delivers",
            "delivers_type",
            "delivers",
            "can_deliver",
            "contexts",
            "terminate_message",
            "from_transition_id",
            "is_schedule_ready",
            "query_params",
            "task_schemas",
        ) + model.FIELDS

        read_only_fields = fields

    def to_representation(self, inst):
        """节点详情"""

        username = self.context["username"]
        data = super(StatusSerializer, self).to_representation(inst)

        # 审批|派单|认领 + 转单 + 终止 + 恢复
        # 是否为母单代理
        is_master_proxy = self.context.get("is_master_proxy", False)
        can_operate = (
            inst.can_operate(username)
            and not is_master_proxy
            and inst.ticket.current_status != "SUSPENDED"
        )
        operations = inst.get_operations(username, can_operate)

        # 可否查看：表示可以操作或许操作过的节点
        can_view = inst.can_view(username)
        # 开放额外权限
        if can_view is False:
            # 开放额外权限一：我处理过任何一个节点，我就能查看所有节点的详情
            if TicketEventLog.objects.is_ticket_operator(username, inst.ticket_id):
                can_view = True
            # 开放额外权限二：我能处理并行节点中的一个，就可以查看所有并行节点的详情
            elif inst.ticket.can_operate(username):
                can_view = True

        if inst.status in [RUNNING, FINISHED, QUEUEING]:
            # Only state in hand, Display fields and trigger button
            serializer_fields = FieldSerializer(
                inst.ticket_fields,
                many=True,
                context={
                    "show_all_fields": self.context.get("show_all_fields", True),
                },
            ).data
            fields = [
                field for field in serializer_fields if field["show_result"] is True
            ]

            # Filter button type trigger
            buttons = list(filter(lambda x: x["type"] == STATE_BUTTON, inst.trigger))
            data.update(fields=fields, buttons=buttons)
        else:
            data.update(fields=[])

        data.update(type=inst.state["type"])
        status = (
            RUNNING
            if inst.status in [RUNNING, RECEIVING, DISTRIBUTING]
            else inst.status
        )
        if status == FINISHED:
            last_log = TicketEventLog.objects.filter(
                ticket_id=inst.ticket_id, from_state_id=inst.state_id
            ).last()
            operator = getattr(last_log, "operator", "")
            processors = transform_single_username(operator)
            delivers, assignors = "", ""
            members = ""
        else:
            processors, members = self.get_processors_and_members(inst)
            delivers = transform_username(inst.get_delivers())
            assignors = transform_username(inst.get_assignors())

        if inst.state["type"] == TASK_STATE:
            remote_info = TaskStateApiInfoSerializer(
                inst.api_instance, many=False, context={"status": inst}
            ).data
            if inst.query_params:
                if remote_info["method"] == "GET":
                    remote_info["req_params"] = inst.query_params
                else:
                    remote_info["req_body"] = inst.query_params
            data["api_info"] = remote_info
        elif inst.state["type"] == TASK_SOPS_STATE:
            remote_info = {
                "sops_info": self.build_sops_info(
                    inst.state["extras"]["sops_info"],
                    data["contexts"].get("task_params", {}),
                ),
                "sops_result": TASK_STATUS_DICT.get(data["status"], _("执行中")),
                "sops_task_url": data["contexts"].get("task_url", ""),
                "error_message": inst.error_message,
            }
            data["api_info"] = remote_info
        elif inst.state["type"] == TASK_DEVOPS_STATE:
            remote_info = {
                "devops_info": self.build_devops_info(
                    inst.state["extras"]["devops_info"],
                    data["contexts"].get("build_params", {}),
                ),
                "devops_result": TASK_STATUS_DICT.get(data["status"], _("执行中")),
                "devops_build_url": data["contexts"].get("build_url", ""),
                "error_message": inst.error_message,
            }
            data["api_info"] = remote_info
        elif inst.state["type"] == WEBHOOK_STATE:
            data["api_info"] = {
                "webhook_info": data["contexts"].get("build_params", {}),
                "variables": data["contexts"].get("variables", {}),
            }
        elif inst.state["type"] in [SIGN_STATE, APPROVAL_STATE]:
            # Get sign task progress
            sign_tasks = SignTask.objects.filter(status_id=inst.id)
            sign_tasks_list = list(
                sign_tasks.values("id", "processor", "status", "create_at")
            )
            # 获取任务处理人和任务ID的映射关系
            processor_task_id_map = OrderedDict(
                {
                    sign_task["processor"]: {
                        "id": sign_task["id"],
                        "status": sign_task["status"],
                        "create_at": sign_task["create_at"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                    for sign_task in sign_tasks_list
                }
            )
            # 获取节点上的任务处理人
            sign_tasks_processor_list = [task["processor"] for task in sign_tasks_list]
            # 获取当前任务的处理人列表
            user_list = UserRole.get_users_by_type(
                inst.bk_biz_id, inst.processors_type, inst.processors, inst.ticket
            )
            # 得到节点当前任务的已处理人
            current_tasks_processors = list(
                set(sign_tasks_processor_list).intersection(set(user_list))
            )
            tasks = []
            for user in user_list[0:30]:
                task_can_view = False
                task_field_list = []
                # 已处理完成的任务, 处理人具有权限查看
                if user in processor_task_id_map:
                    task_can_view = True
                    task_fields = TaskField.objects.filter(
                        task_id=processor_task_id_map[user]["id"]
                    )
                    task_field_list = TaskFieldSerializer(
                        instance=task_fields, many=True
                    ).data

                task_info = {
                    "processor": transform_single_username(user),
                    "status": processor_task_id_map.get(user, {}).get("status", "WAIT"),
                    "can_view": task_can_view,
                    "fields": task_field_list,
                    "create_at": processor_task_id_map.get(user, {}).get(
                        "create_at", ""
                    ),
                }
                tasks.append(task_info)

            data["tasks"] = tasks
            # Format sign state processors
            processors = inst.get_sign_display_processors()
            processors = _("%s (共%d人, 已处理%d人)") % (
                processors,
                len(user_list),
                len(current_tasks_processors),
            )

            # 会签节点: QUEUEING -> RUNNING
            status = RUNNING if status == QUEUEING else status
            if inst.state["type"] == APPROVAL_STATE:
                data["is_multi"] = inst.state["is_multi"]

        data.update(
            operations=operations,
            can_operate=can_operate,
            status=status,
            can_view=can_view,
            processors=processors,
            delivers=delivers,
            assignors=assignors,
            can_create_task=inst.can_create_task(username),
            can_execute_task=inst.can_execute_task(username),
            members=members,
            desc=inst.state["desc"],
        )
        for index, item in enumerate(data["operations"]):
            data["operations"][index]["name"] = _(data["operations"][index]["name"])

        # SLA “预计完成时间”显示的是“约定处理时长”
        sla_task_info = inst.nearest_sla_task_info()

        data.update(
            is_reply_need=inst.is_reply_need,
            is_replied=inst.is_replied,
            sla_timeout=sla_task_info["sla_timeout"],
            sla_status=sla_task_info["sla_status"],
            sla_task_status=sla_task_info["task_status"],
            sla_deadline=sla_task_info["deadline"].strftime("%Y-%m-%d %H:%M:%S")
            if sla_task_info["deadline"]
            else "--",
        )

        return data

    @staticmethod
    def build_sops_info(sops_info, task_params):
        info = []
        if not task_params:
            return info
        apps = get_biz_names()
        info.append(
            {
                "key": "bk_biz_id",
                "name": sops_info["bk_biz_id"]["name"],
                "value": apps.get(str(task_params["bk_biz_id"])),
                "params_value": task_params["bk_biz_id"],
            }
        )
        info.append(
            {
                "key": "template_id",
                "name": _("流程模板"),
                "value": {
                    str(item["id"]): item["name"] for item in get_template_list()
                }.get(task_params["template_id"], "--"),
                "params_value": task_params["template_id"],
            }
        )
        info.extend(
            [
                {
                    "key": constant["key"],
                    "name": constant["name"],
                    "value": task_params["constants"].get(constant["key"], ""),
                    "params_value": task_params["constants"].get(constant["key"], ""),
                }
                for constant in sops_info["constants"]
            ]
        )

        return info

    @staticmethod
    def build_devops_info(devops_info, task_params):
        if not task_params:
            return []
        info = [
            {
                "key": "project_id",
                "name": devops_info["project_id"]["name"],
                "value": devops_info["project_id"]["value"],
                "params_value": task_params["project_id"],
            },
            {
                "key": "pipeline_id",
                "name": devops_info["pipeline_id"]["name"],
                "value": devops_info["pipeline_id"]["value"],
                "params_value": task_params["pipeline_id"],
            },
        ]
        if devops_info["constants"]:
            info.extend(
                [
                    {
                        "key": constant["key"],
                        "name": constant["name"],
                        "value": constant["value"],
                        "params_value": constant["value"],
                    }
                    for constant in devops_info["constants"]
                ]
            )
        return info

    @staticmethod
    def get_processors_and_members(inst):
        all_processors = inst.get_processors()
        if inst.processors_type == "ORGANIZATION":
            processors = inst.get_organization_name(inst.processors.strip(","))
            members = (
                all_processors[0:30] if len(all_processors) > 30 else all_processors
            )
            members = transform_username(members)
        else:
            processors = transform_username(all_processors)
            members = ""
        return processors, members


class SimpleStatusSerializer(serializers.ModelSerializer):
    """节点状态简单序列化"""

    state_id = serializers.IntegerField()
    tag = serializers.CharField(required=False, max_length=LEN_LONG)
    name = serializers.CharField(required=True, max_length=LEN_NORMAL)
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    action_type = serializers.ChoiceField(choices=ACTION_CHOICES)
    processors = serializers.CharField(max_length=LEN_LONG)
    processors_type = serializers.ChoiceField(choices=PROCESSOR_CHOICES)

    class Meta:
        model = Status
        fields = (
            "name",
            "state_id",
            "status",
            "action_type",
            "tag",
            "processors_type",
            "processors",
        )

        read_only_fields = fields

    def to_representation(self, inst):
        """节点详情"""
        data = super(SimpleStatusSerializer, self).to_representation(inst)
        data.update(
            processors=",".join(inst.get_processors()),
        )

        return data


class TicketList(object):
    def __init__(self, instances, username, token):
        self.instances = instances
        self.username = username
        self.token = token

    @staticmethod
    def get_attention_users(ticket_ids):
        followers = AttentionUsers.objects.filter(ticket_id__in=ticket_ids).values(
            "ticket_id", "follower"
        )
        ticket_follower_map = {}
        for follower in followers:
            ticket_follower_map.setdefault(follower["ticket_id"], []).append(
                follower["follower"]
            )
        return ticket_follower_map

    def can_comment(self, inst, comments, is_email_invite_token):
        one = self.username in [inst["creator"], inst["meta"].get("ticket_agent")]
        two = inst["current_status"] == FINISHED
        three = comments.get(inst["id"], {}).get("stars", 0) > 0
        return all([one, two, not three]) or is_email_invite_token

    @staticmethod
    def get_service_info(service_ids):
        service_info = Service._objects.filter(id__in=service_ids).values("id", "name")
        return {service["id"]: service["name"] for service in service_info}

    @staticmethod
    def get_supervisor():
        supervisors_info = UserRole.objects.filter(role_type="GENERAL").values(
            "id", "members"
        )
        return {
            supervisor["id"]: supervisor["members"] for supervisor in supervisors_info
        }

    @staticmethod
    def can_withdraw(flow, node_status, is_over):
        # {"123": {"status": "running", "type": "start"}
        if not flow.is_revocable or is_over:
            # 不可撤销或者已经结束的单，直接返回
            return False
        status_info = node_status.values()
        if flow.revoke_config["type"] == REVOKE_TYPE.FIRST:
            finish_count = [
                status["status"]
                for status in status_info
                if status["status"] == FINISHED
            ]
            if len(finish_count) == 1:
                return True

            # 打回到提单环节
            for status in status_info:
                if status["type"] == START_STATE and status["status"] == RUNNING:
                    return True
            return False
        elif flow.revoke_config["type"] == REVOKE_TYPE.ASSIGN:
            state_id = flow.revoke_config["state"]
            return state_id in node_status
        return True

    @staticmethod
    def get_ticket_node_status(ticket_ids):
        node_status = Status.objects.filter(ticket_id__in=ticket_ids)
        ticket_status = {}
        for status in node_status:
            ticket_status.setdefault(status.ticket_id, {})[status.id] = {
                "status": status.status,
                "type": status.type,
            }
        return ticket_status

    @staticmethod
    def get_workflow_version(flow_ids):
        flows = WorkflowVersion._objects.filter(id__in=flow_ids).only(
            "id", "is_revocable", "revoke_config"
        )
        return {flow.id: flow for flow in flows}

    @staticmethod
    def get_sla_tasks(ticket_ids):
        sla_task_info = {}
        sla_ids = SlaTask.objects.filter(ticket_id__in=ticket_ids).values(
            "ticket_id", "sla_id", "sla_status", "task_status"
        )

        sla_info = {}
        sla_objs = Sla.objects.filter(
            id__in=set([sla["sla_id"] for sla in sla_ids])
        ).values("id", "name")
        for sla_obj in sla_objs:
            sla_info[sla_obj["id"]] = sla_obj["name"]

        color = SlaTicketHighlight.objects.first()

        for sla in sla_ids:
            name = sla_info[sla["sla_id"]]
            is_timeout = sla["sla_status"] == HANDLE_TIMEOUT and sla["task_status"] in [
                SLA_RUNNING,
                PAUSED,
            ]
            sla_color = color.handle_timeout_color if is_timeout else ""
            if sla["ticket_id"] not in sla_task_info:
                sla_task_info[sla["ticket_id"]] = {"name": [name], "color": sla_color}
                continue
            if name not in sla_task_info[sla["ticket_id"]]["name"]:
                sla_task_info[sla["ticket_id"]]["name"].append(name)
            if not sla_task_info[sla["ticket_id"]]["color"]:
                sla_task_info[sla["ticket_id"]]["color"] = sla_color

        return sla_task_info

    def to_client_representation(self):
        ticket_list = list(
            Ticket.objects.filter(pk__in=[x.pk for x in self.instances]).values(
                "sn",
                "id",
                "title",
                "service_id",
                "service_type",
                "meta",
                "bk_biz_id",
                "current_status",
                "create_at",
                "creator",
                "is_supervise_needed",
                "flow_id",
                "supervise_type",
                "supervisor",
                "project_key",
            )
        )
        ticket_ids = [ticket["id"] for ticket in ticket_list]
        ticket_followers = self.get_attention_users(ticket_ids)
        email_invite = TicketCommentInvite.get_user_comments_invites(self.username)
        master_tickets = Ticket.get_batch_master_ticket(ticket_ids)
        waiting_approve = Ticket.batch_waiting_approve(ticket_ids, self.username)
        steps = Ticket.ticket_current_steps(ticket_ids)
        all_status = TicketStatus.all_status_info()
        comments = TicketComment.ticket_comments(ticket_ids)
        supervisors_info = self.get_supervisor()
        service_info = self.get_service_info(
            [ticket["service_id"] for ticket in ticket_list]
        )
        ticket_status = self.get_ticket_node_status(ticket_ids)
        workflow_version = self.get_workflow_version(
            [ticket["flow_id"] for ticket in ticket_list]
        )
        sla_task_info = self.get_sla_tasks(ticket_ids)
        for inst in ticket_list:
            comment_id = comments.get(inst["id"], {}).get("id")
            invites = email_invite.get(comment_id, []) if comment_id else []
            is_email_invite_token = self.token in invites

            # 当前步骤、单据状态、优先级来源母单
            master_ticket = master_tickets.get(inst["id"])
            real_ticket = master_ticket if master_ticket else inst
            status_key = "{}_{}".format(
                real_ticket["service_type"], real_ticket["current_status"]
            )
            is_over = all_status.get(status_key, {}).get("over", False)
            supervisors = (
                supervisors_info.get(int(inst["supervisor"]), inst["supervisor"])
                if inst["supervise_type"] == "GENERAL"
                else inst["supervisor"]
            )
            supervisors = supervisors.split(",") if supervisors else []
            real_supervisors = supervisors + [inst["creator"]]
            inst["meta"] = real_ticket["meta"]
            try:
                inst.update(
                    service_name=service_info[inst["service_id"]],
                    current_status=real_ticket["current_status"],
                    current_status_display=all_status.get(status_key, {}).get(
                        "name", "--"
                    ),
                    current_steps=steps.get(real_ticket["id"], []),
                    priority_name=inst["meta"]["priority"]["name"]
                    if "priority" in inst["meta"]
                    else "--",
                    create_at=inst["create_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    current_processors="",  # ",".join(self.ticket_processors.get(inst.id, "")),
                    can_comment=self.can_comment(inst, comments, is_email_invite_token),
                    can_operate=False,
                    waiting_approve=waiting_approve.get(inst["id"], False),
                    followers=ticket_followers.get(inst["id"], []),
                    comment_id=comments.get(inst["id"], {}).get("id", ""),
                    can_supervise=all(
                        [
                            inst["is_supervise_needed"],
                            not is_over,
                            self.username in real_supervisors,
                        ]
                    ),
                    can_withdraw=self.can_withdraw(
                        workflow_version[inst["flow_id"]],
                        ticket_status[inst["id"]],
                        is_over,
                    ),
                    sla=sla_task_info.get(inst["id"], {}).get("name", []),
                    sla_color=sla_task_info.get(inst["id"], {}).get("color", ""),
                    project_key=inst["project_key"],
                )
            except Exception as e:
                logger.info("单据序列化计算失败, error = {}".format(e))
                pass

            # 提单人、代提单人才有权限看评价，无权查看评论信息则置设置comment_id为-1
            if not (
                self.username in [inst["creator"], inst["meta"].get("ticket_agent")]
                or is_email_invite_token
            ):
                inst.update(comment_id="-1")

        return ticket_list


class TicketSerializer(AuthModelSerializer):
    """单据序列化"""

    title = serializers.CharField(required=False, max_length=LEN_NORMAL)
    catalog_id = serializers.CharField(required=False)
    service_id = serializers.CharField(required=True)
    service_type = serializers.CharField(
        required=False, allow_blank=True, max_length=LEN_NORMAL
    )
    current_status = serializers.CharField(default="CREATED")
    project_key = serializers.CharField(required=False, max_length=32)

    meta = JSONField(required=False, initial={})

    class Meta:
        model = Ticket
        fields = (
            "id",
            "catalog_id",
            "catalog_name",
            "catalog_fullname",
            "service_id",
            "service_name",
            "flow_id",
            "sn",
            "title",
            "service_type",
            "service_type_name",
            "is_draft",
            "current_status",
            "current_status_display",
            "comment_id",
            "is_commented",
            "is_over",
            "related_type",
            "has_relationships",
            "priority_name",
            "meta",
            "bk_biz_id",
            "project_key",
            "task_schemas",
        ) + model.FIELDS
        read_only_fields = ("sn",) + model.FIELDS

    def __init__(self, instance=None, data=empty, **kwargs):
        super(TicketSerializer, self).__init__(instance, data, **kwargs)
        # 针对批量获取的内容，可以在init的时候进行处理，避免每个数据的序列化都要去拉取接口
        self.related_users = self.get_related_users()
        self.ticket_followers = self.get_attention_users()

    def get_related_users(self):
        """
        获取到所有相关的用户，避免多次访问API接口
        :return:
        """
        all_related_users = []
        tickets = (
            [self.instance]
            if isinstance(self.instance, Ticket)
            else []
            if self.instance is None
            else self.instance
        )

        for inst in tickets:
            all_related_users.extend(inst.real_current_processors)
            all_related_users.append(inst.creator)
        return get_bk_users(format="dict", users=list(set(all_related_users)))

    def get_attention_users(self):
        tickets = (
            [self.instance]
            if isinstance(self.instance, Ticket)
            else []
            if self.instance is None
            else self.instance
        )
        ticket_ids = [ticket.id for ticket in tickets]
        followers = AttentionUsers.objects.filter(ticket_id__in=ticket_ids).values(
            "ticket_id", "follower"
        )
        ticket_follower_map = {}
        for follower in followers:
            ticket_follower_map.setdefault(follower["ticket_id"], []).append(
                follower["follower"]
            )
        return ticket_follower_map

    def to_internal_value(self, data):
        """验证参数和组装创建单据逻辑"""
        ret = super(TicketSerializer, self).to_internal_value(data)
        catalog_services = data["catalog_services"]
        current_status = data["current_status"]
        fields_kv = {field["key"]: field["value"] for field in data.get("fields", [])}

        # 创建单
        if "creator" in data:
            ret.update(creator=data["creator"])
        ret.update(
            {
                "service": data["service"],
                "service_type": data["service"].key,
                "flow_id": data["service"].workflow.id,
                "is_supervise_needed": data["service"].workflow.is_supervise_needed,
                "supervisor": data["service"].workflow.supervisor,
                "supervise_type": data["service"].workflow.supervise_type,
                "catalog_id": catalog_services.catalog_id,
                "is_draft": False,
                "current_status": current_status,
                "updated_by": data.get(
                    "creator", self.context["request"].user.username
                ),
                "title": fields_kv["title"],
                "bk_biz_id": fields_kv.get("bk_biz_id", DEFAULT_BK_BIZ_ID),
                "attention": data.get("attention", False),
            }
        )
        return ret

    def get_remark_root_id(self, ticket_id):
        node = TicketRemark.init_root_node(ticket_id=ticket_id)
        return node.id

    def to_representation(self, inst):
        """单据详情
        add extra property: can_operate, can_comment, comment_id
        """
        data = super(TicketSerializer, self).to_representation(inst)
        username = self.context["request"].user.username
        token = self.context["request"].query_params.get("token", "")
        # 用户全量信息
        is_email_invite_token = inst.is_email_invite_token(username, token)

        # 当前步骤、单据状态、优先级来源母单
        master_ticket = inst.get_master_ticket()
        master_or_self_ticket = master_ticket if master_ticket else inst

        if "headers" in master_or_self_ticket.meta:
            master_or_self_ticket.meta.pop("headers")

        data.update(
            current_status=master_or_self_ticket.current_status,
            current_status_display=master_or_self_ticket.current_status_display,
            current_steps=master_or_self_ticket.brief_current_steps,
            priority_name=master_or_self_ticket.priority_name,
            meta=master_or_self_ticket.meta,
        )

        can_comment = inst.can_comment(username) or is_email_invite_token
        can_operate = inst.can_operate(username)

        can_view = (
            username in self.ticket_followers.get(inst.id, [])
            or can_operate
            or inst.can_view(username)
        )

        data.update(
            creator=transform_single_username(inst.creator, self.related_users),
            current_processors=transform_username(
                list(inst.display_current_processors), self.related_users
            ),
            can_comment=can_comment,
            can_operate=can_operate,
            can_view=can_view,
            remark_root_id=self.get_remark_root_id(inst.id),
        )

        # 提单人、代提单人才有权限看评价，无权查看评论信息则置设置comment_id为-1
        if not (
            username in [inst.creator, inst.meta.get("ticket_agent")]
            or is_email_invite_token
        ):
            data.update(comment_id="-1")

        # 是否等待审批
        data.update(waiting_approve=inst.waiting_approve(username))

        # 关注人
        data.update(followers=self.ticket_followers.get(inst.id, []))

        # 自动过单相关的配置
        data.update(is_auto_approve=inst.flow.is_auto_approve)

        # SLA
        data.update(
            sla=list(inst.slas.values_list("name", flat=True)), sla_color=inst.sla_color
        )

        return self.update_auth_actions(inst, data)

    def update_auth_actions(self, instance, data):
        request = self.context["request"]
        iam_client = IamRequest(request)
        resource_info = {
            "resource_id": str(instance.service_id),
            "resource_name": instance.service_name,
            "resource_type": "service",
        }

        apply_actions = ["ticket_management", "ticket_view"]
        auth_actions = iam_client.resource_multi_actions_allowed(
            apply_actions, [resource_info], project_key=instance.project_key
        )
        actions = [key for key, value in auth_actions.items() if value]
        data["auth_actions"] = actions

        return data

    def run_validation(self, data):
        if self.instance is None:
            service, catalog_services = service_validate(data.get("service_id"))

            # 设置初始工单状态
            try:
                current_status = TicketStatus.objects.get(
                    service_type=service.key, is_start=True
                ).key
            except TicketStatus.DoesNotExist:
                raise serializers.ValidationError({_("工单状态"): _("工单状态不存在，请检查")})

            # 创建单据时，若没有传入creator参数，则采用request的当前用户
            creator = data.get("creator", self.context["request"].user.username)
            data.update(
                {
                    "service": service,
                    "current_status": current_status,
                    "catalog_services": catalog_services,
                    "creator": creator,
                }
            )
            self.validators += [CreateTicketValidator(self.context["request"])]
        return super(TicketSerializer, self).run_validation(data)

    def create(self, validated_data):
        attention = validated_data.pop("attention")
        validated_data.update(
            {"sn": generate_random_sn(validated_data.get("service_type"))}
        )
        validated_data["project_key"] = Service.objects.get(
            id=validated_data["service_id"]
        ).project_key
        validated_data.pop("service")
        ticket = super(TicketSerializer, self).create(validated_data)
        if attention:
            AttentionUsers.objects.create(ticket_id=ticket.id, follower=ticket.creator)
        ticket.update_organization_ticket()
        # 初始化一条根评论出来
        TicketRemark.create_root(ticket_id=ticket.id)
        return ticket


class TicketRetrieveSerializer(TicketSerializer):
    """单据详情序列化"""

    class Meta:
        model = Ticket
        fields = (
            "first_state_id",
            "pre_status",
            "pre_status_display",
            "pipeline_message",
            "is_schedule_ready",
            "last_transition_id",
            "project_key",
        ) + copy.deepcopy(TicketSerializer.Meta.fields)
        read_only_fields = copy.deepcopy(TicketSerializer.Meta.read_only_fields)

    def to_representation(self, inst):
        """单据详情"""

        data = super(TicketRetrieveSerializer, self).to_representation(inst)

        # 查看单据详情时，补充户身份资料信息
        try:
            creator = BkUser.objects.get(username=inst.creator)
            profile = json.loads(creator.get_property("profile"))
        except Exception:
            profile = {"name": "", "phone": "", "departments": []}

        username = self.context["request"].user.username
        is_itsm_superuser = UserRole.is_itsm_superuser(username)
        is_service_owner = Service.is_service_owner(inst.service_id, username)
        # ITSM超级管理员和服务负责人
        is_ticket_admin = any([is_itsm_superuser, is_service_owner])

        can_edit_field_keys = []
        if not is_ticket_admin:
            # 获取当前用户拥有操作权限的节点下可编辑字段
            statuses = Status.objects.get_running_status(inst.id)
            can_operate_state_ids = [
                status.state_id for status in statuses if status.can_operate(username)
            ]

            # 获取可操作节点下的所有流程字段ID
            workflow_field_ids = []
            for state_id in can_operate_state_ids:
                workflow_field_ids.extend(inst.flow.states.get(str(state_id))["fields"])
            can_edit_field_keys = inst.fields.filter(
                workflow_field_id__in=list(set(workflow_field_ids)),
                source=TABLE,
                is_readonly=False,
            ).values_list("key", flat=True)

        data.update(
            is_ticket_admin=is_ticket_admin,
            can_derive=inst.can_derive(username),
            can_invite_followers=inst.can_invite_followers(username),
            profile=profile,
            is_biz_need=inst.bk_biz_id != DEFAULT_BK_BIZ_ID,
            can_withdraw=inst.can_withdraw(username),
            can_close=inst.can_close(username),
            can_supervise=inst.can_supervise(username),
            # can_create_task=inst.can_create_task(username),
            # can_execute_task=inst.can_execute_task(username),
            table_fields=TableFieldSerializer(
                inst.table_fields(),
                context={
                    "is_ticket_admin": is_ticket_admin,
                    "can_edit_field_keys": can_edit_field_keys,
                },
                many=True,
            ).data,
        )

        return data


class MasterProxyTicketSerializer(TicketRetrieveSerializer):
    """母单代理的单据详情序列化"""

    def to_representation(self, inst):
        data = super(MasterProxyTicketSerializer, self).to_representation(inst)

        username = self.context["request"].user.username
        token = self.context["request"].query_params.get("token", "")
        view = self.context["view"]
        lookup_url_kwarg = view.lookup_url_kwarg or view.lookup_field
        pk = view.kwargs.get(lookup_url_kwarg)
        slave_ticket = Ticket.objects.get(id=pk)

        # 查看单据详情时，补充户身份资料信息
        try:
            creator = BkUser.objects.get(username=slave_ticket.creator)
            profile = json.loads(creator.get_property("profile"))
        except Exception:
            profile = {"name": "", "phone": "", "departments": []}

        # 母单代理单据中的所有公共字段都是只读状态
        for table_field in data["table_fields"]:
            table_field["can_edit"] = False

        data.update(
            id=int(pk),
            sn=slave_ticket.sn,
            title=slave_ticket.title,
            creator=transform_single_username(slave_ticket.creator),
            create_at=better_time_or_none(slave_ticket.create_at),
            profile=profile,
            can_view=slave_ticket.current_status_can_view(username),
            can_withdraw=False,
            can_supervise=False,
            can_derive=False,
            can_operate=False,
            can_comment=slave_ticket.can_comment(username)
            or slave_ticket.is_email_invite_token(username, token),
            is_commented=slave_ticket.is_commented,
            comment_id=slave_ticket.comment_id,
            table_fields=data["table_fields"],
            master_id=inst.id,
            related_type="slave",
        )

        return data


class RelatedTicketSerializer(serializers.Serializer):
    """母子单或者关联单序列化"""

    id = serializers.IntegerField(read_only=True)
    service_name = serializers.CharField(read_only=True)
    sn = serializers.CharField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        username = self.context.get("username")

        if username:
            can_view = instance.current_status_can_view(username)
            ret.update(can_view=can_view)

        return ret


class UnmergeTicketsSerializer(serializers.Serializer):
    master_ticket_id = serializers.IntegerField(required=True)
    slave_ticket_ids = serializers.ListField(required=True, allow_empty=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def run_validation(self, data=empty):
        value = super(UnmergeTicketsSerializer, self).run_validation(data=data)
        for slave_ticket_id in value["slave_ticket_ids"]:
            try:
                ticket_to_ticket = TicketToTicket.objects.get(
                    related_type=MASTER_SLAVE,
                    from_ticket_id=slave_ticket_id,
                    to_ticket_id=value["master_ticket_id"],
                )
            except TicketToTicket.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        _("母子单"): _("子单ID(%s)->母单ID(%s)的绑定关系不存在")
                        % (slave_ticket_id, value["master_ticket_id"])
                    }
                )

            if ticket_to_ticket.related_status == "RUNNING":
                raise serializers.ValidationError({_("母子单"): _("正在解绑中... 请勿重复执行")})
        return value


class UnbindHistorySerializer(serializers.Serializer):
    related_type = serializers.ChoiceField(choices=RELATE_CHOICES, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class TriggerStateButtonSerializer(serializers.Serializer):
    state_id = serializers.IntegerField(required=True)
    component_key = serializers.CharField(required=True)
    inputs = serializers.JSONField(required=False, initial={})

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def run_validation(self, data=empty):
        value = super(TriggerStateButtonSerializer, self).run_validation(data)

        # Does it have permission operate current state
        username = self.context.get("username")
        status = Status.objects.filter(id=value["state_id"]).first()

        if status is None:
            raise TriggerValidateError(_("该节点不存在"))

        if not status.can_operate(username):
            raise TriggerValidateError(_("抱歉, 你不具有操作当前节点的权限"))

        # Event log record status name
        value.update(status=status)
        ComponentLibrary.get_component_class("trigger", value["component_key"])
        return value


class BaseFilterSerializer(serializers.Serializer):
    create_at__gte = serializers.DateField(required=False, format="%Y-%m-%d")
    create_at__lte = serializers.DateField(required=False, format="%Y-%m-%d")


class TicketFilterSerializer(BaseFilterSerializer):
    """单据节点操作序列化"""

    bk_biz_id = serializers.IntegerField(required=False)
    catalog_id = serializers.IntegerField(required=False)
    service_id = serializers.IntegerField(required=False)
    flow_id = serializers.IntegerField(required=False)
    keyword = serializers.CharField(required=False, max_length=LEN_LONG)
    project_key = serializers.CharField(required=False, max_length=32)
    view_type = serializers.ChoiceField(
        required=False,
        choices=[
            ("my_todo", "my_todo"),
            ("my_created", "my_created"),
            ("my_history", "my_history"),
            ("my_dealt", "my_dealt"),
            ("my_attention", "my_attention"),
            ("my_approval", "my_approval"),
        ],
    )
    create_at__gte = serializers.DateTimeField(
        required=False, format="%Y-%m-%d %H:%M:%S"
    )
    create_at__lte = serializers.DateTimeField(
        required=False, format="%Y-%m-%d %H:%M:%S"
    )
    overall_current_status__in = serializers.CharField(required=False)
    exclude_ticket_id__in = serializers.CharField(required=False)
    current_processor = serializers.CharField(required=False)
    service_type = serializers.ChoiceField(
        required=False,
        choices=[
            ("request", "request"),
            ("change", "change"),
            ("event", "event"),
            ("question", "question"),
        ],
    )
    creator__in = serializers.CharField(required=False)


class StatisticsSerializer(BaseFilterSerializer):
    order_by = serializers.CharField(
        required=False, max_length=LEN_SHORT, default="-count"
    )
    service_name = serializers.CharField(required=False, max_length=LEN_LONG)
    biz_id = serializers.CharField(required=False, max_length=LEN_LONG)


class StatisticsFilterSerializer(BaseFilterSerializer):
    timedelta = serializers.CharField(
        required=False, max_length=LEN_SHORT, default="days"
    )
    resource_type = serializers.ChoiceField(
        required=True, choices=["creator", "ticket", "user", "service"]
    )


class ServiceStatisticsFilterSerializer(StatisticsFilterSerializer):
    service_id = serializers.IntegerField(required=False)
    resource_type = serializers.ChoiceField(required=False, choices=["ticket", "biz"])


class TicketOrganizationSerializer(BaseFilterSerializer):
    level = serializers.IntegerField(required=False, default=1)


class RecentlyTicketFilterSerializer(serializers.Serializer):
    """最近工单序列化"""

    create_at__gte = serializers.DateTimeField(
        required=True, format="%Y-%m-%d %H:%M:%S"
    )
    create_at__lte = serializers.DateTimeField(
        required=True, format="%Y-%m-%d %H:%M:%S"
    )


class TicketStateOperateSerializer(serializers.Serializer):
    """单据节点操作序列化"""

    state_id = serializers.IntegerField(required=True)
    action_type = serializers.ChoiceField(choices=ALL_ACTION_CHOICES)
    processors = serializers.CharField(max_length=LEN_LONG, allow_blank=True)
    processors_type = serializers.ChoiceField(choices=PROCESSOR_CHOICES)
    action_message = serializers.CharField(required=False, max_length=LEN_LONG)

    def __init__(self, *args, **kwargs):
        self.ticket = kwargs.pop("ticket", None)
        self.request = kwargs.pop("request", None)
        self.operator = kwargs.pop("operator", None)

        kwargs["data"] = self.request.data
        super(TicketStateOperateSerializer, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        data = super(TicketStateOperateSerializer, self).to_internal_value(data)

        if data["action_type"] == CLAIM_OPERATE:
            data["processors"] = self.operator
            data["processors_type"] = PERSON

        if data["processors_type"] == PERSON:
            data["processors"] = dotted_name(data["processors"])

        if data["processors_type"] == STARTER:
            data["processors_type"] = PERSON
            data["processors"] = self.ticket.creator
        if "action_message" in data:
            data["action_message"] = html_escape(data["action_message"])

        data.update(source=self.request.source, ticket=self.ticket)

        return data

    def run_validation(self, data):
        validated_data = super(TicketStateOperateSerializer, self).run_validation(data)

        try:
            validated_data["current_node"] = self.ticket.node_status.get(
                state_id=validated_data["state_id"]
            )
        except Status.DoesNotExist:
            raise serializers.ValidationError(_("操作的任务不存在，请确认后再提交"))

        # 校验节点操作的合法性
        self.validators = [
            StateOperateValidator(
                validated_data["current_node"], bk_biz_id=self.ticket.bk_biz_id
            )
        ]

        self.run_validators(data)

        return validated_data

    def to_representation(self, instance):
        return self.validated_data


class TicketStateOperateExceptionSerializer(serializers.Serializer):
    choices = [(EXCEPTION_DISTRIBUTE_OPERATE, "异常分派")]
    # 只支持异常分派
    action_type = serializers.ChoiceField(choices=choices)
    state_id = serializers.IntegerField(required=True)
    processors = serializers.CharField(max_length=LEN_LONG, allow_blank=True)
    processors_type = serializers.ChoiceField(choices=PROCESSOR_CHOICES)
    action_message = serializers.CharField(required=False, max_length=LEN_LONG)

    def __init__(self, *args, **kwargs):
        self.ticket = kwargs.pop("ticket", None)
        self.request = kwargs.pop("request", None)
        self.operator = kwargs.pop("operator", None)

        kwargs["data"] = self.request.data
        super(TicketStateOperateExceptionSerializer, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        data = super(TicketStateOperateExceptionSerializer, self).to_internal_value(
            data
        )

        if "action_message" in data:
            data["action_message"] = html_escape(data["action_message"])

        data.update(source=self.request.source, ticket=self.ticket)

        return data

    def run_validation(self, data):
        validated_data = super(
            TicketStateOperateExceptionSerializer, self
        ).run_validation(data)

        try:
            validated_data["current_node"] = self.ticket.node_status.get(
                state_id=validated_data["state_id"]
            )
        except Status.DoesNotExist:
            raise serializers.ValidationError(_("操作的任务不存在，请确认后再提交"))

        # 校验节点操作的合法性
        self.validators = [
            StateOperateValidator(
                validated_data["current_node"], bk_biz_id=self.ticket.bk_biz_id
            )
        ]

        self.run_validators(data)
        return validated_data

    def to_representation(self, instance):
        return self.validated_data


class TicketExportSerializer(serializers.Serializer):
    """导出工单用"""

    id = serializers.IntegerField()
    sn = serializers.CharField()
    title = serializers.CharField()
    bk_biz_id = serializers.CharField()
    service_type_name = serializers.CharField()
    catalog_fullname = serializers.CharField()
    current_status_display = serializers.CharField()
    current_steps = serializers.JSONField()
    creator = serializers.CharField()
    create_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    service_name = serializers.CharField()
    stars = serializers.IntegerField()
    comment = serializers.CharField()

    def to_representation(self, instance):
        data = super(TicketExportSerializer, self).to_representation(instance)
        if instance.flow.engine_version == DEFAULT_ENGINE_VERSION:
            data.update(
                {
                    "current_steps": ";".join(
                        [
                            _("[步骤：{}，处理人：{}]").format(
                                item.get("name", ""), item.get("processors", "")
                            )
                            for item in data["current_steps"]
                        ]
                    )
                }
            )
        else:
            data.update(
                {
                    "creator": transform_single_username(instance.creator),
                    "current_status": instance.get_current_status_display(),
                    "current_steps": instance.get_current_state_name(),
                    "current_processors_type": instance.get_current_role_display(),
                    "current_processors": transform_username(
                        instance.get_current_processors()
                    )
                    if instance.get_current_processors()
                    else "--",
                }
            )

        return data


class SimpleLogsSerializer(serializers.Serializer):
    operator = serializers.CharField(read_only=True)
    operate_at = serializers.DateTimeField(read_only=True)
    message = serializers.CharField(read_only=True)


class TicketLogSerializer(serializers.ModelSerializer):
    sn = serializers.CharField(read_only=True)
    catalog_fullname = serializers.CharField(read_only=True)

    class Meta:
        model = Ticket
        fields = ("sn", "catalog_fullname")
        read_only_fields = fields

    def to_representation(self, instance):
        data = super(TicketLogSerializer, self).to_representation(instance)
        data["logs"] = SimpleLogsSerializer(instance.logs, many=True).data
        field_key = self.context["field_key"]
        if field_key:
            data["fields"] = FieldSimpleSerializer(
                instance.fields.filter(key__in=field_key.split(",")), many=True
            ).data
        else:
            data["fields"] = FieldSimpleSerializer(instance.fields, many=True).data
        return data


class OldTicketStateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        ticket = self.context["ticket"]
        state = super(OldTicketStateSerializer, self).to_representation(instance)
        state["state_id"] = state["id"]
        state["fields"] = FieldSerializer(
            ticket.fields.filter(state_id=state["id"]).exclude(
                key__in=[FIELD_BACK_MSG, FIELD_TERM_MSG]
            ),
            many=True,
        ).data
        state["can_view"] = True
        log = TicketEventLog.objects.filter(
            ticket_id=ticket.id, from_state_id=state["id"]
        ).last()
        state["processors"] = transform_single_username(log.operator) if log else ""
        state["status"] = "FINISHED"
        state["update_at"] = log.operate_at if log else ""
        if state["type"] == "ROUTER":
            state["type"] = "NORMAL"
        return state


class TicketRemarkSerializer(serializers.ModelSerializer):
    """服务目录关联序列化"""

    """服务目录序列化"""

    REMARK_TYPE = [
        ("PUBLIC", "公开评论"),
        ("INSIDE", "内部评论"),
    ]

    level = serializers.IntegerField(required=False, min_value=0)
    # allow_blank -> 允许字段为空字符串
    content = serializers.CharField(
        required=False, max_length=LEN_XXX_LONG, allow_blank=True
    )
    parent__id = serializers.IntegerField(required=False, source="parent.id")
    parent_key = serializers.CharField(required=False, allow_blank=True)
    update_log = serializers.JSONField(required=False)
    users = serializers.ListField(required=True, initial=[])
    remark_type = serializers.ChoiceField(required=True, choices=REMARK_TYPE)

    def update(self, instance, validated_data):
        update_by = validated_data["updated_by"]
        receivers = ",".join(
            compute_list_difference(instance.users, validated_data["users"])
        )
        instance.update_log.append(
            "{}于{}更新了该评论".format(
                update_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        instance = super(TicketRemarkSerializer, self).update(instance, validated_data)
        remark_notify.apply_async(
            args=[
                instance.ticket_id,
                instance.creator,
                validated_data["content"],
                receivers,
            ]
        )
        return instance

    def create(self, validated_data):
        parent_id = validated_data["parent"]["id"]
        parent_node = TicketRemark.objects.get(id=parent_id)
        validated_data["parent_id"] = parent_id
        validated_data["ticket_id"] = parent_node.ticket_id
        validated_data.pop("parent")
        instance = super(TicketRemarkSerializer, self).create(validated_data)

        remark_notify.apply_async(
            args=[
                instance.ticket_id,
                instance.creator,
                instance.content,
                ",".join(instance.users),
            ]
        )
        return instance

    class Meta:
        model = TicketRemark
        fields = (
            "id",
            "key",
            "level",
            "parent",
            "parent_key",
            "parent__id",
            "content",
            "update_log",
            "users",
            "remark_type",
            "creator",
            "create_at",
            "update_at",
            "updated_by",
        )
        # 只读字段在创建和更新时均被忽略
        read_only_fields = (
            "id",
            "key",
            "parent_name",
            "parent_key",
            "parent__id",
            "parent__name",
            "ticket_id",
            "update_log",
            "creator",
            "create_at",
            "update_at",
            "updated_by",
        )

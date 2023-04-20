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
import functools
import json
import time
from datetime import datetime
from itertools import chain

import requests
import jsonfield
from bulk_update.helper import bulk_update
from django.conf import settings
from django.db import models, transaction
from django.core.cache import cache
from django.db.models import Q, Count
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from common.log import logger
from common.cipher import AESVerification
from common.redis import Cache
from dateutil.relativedelta import relativedelta
from itsm.component.constants import (
    ACTION_CHOICES,
    ACTION_DICT,
    BASE_MODEL,
    NOTIFY_GLOBAL_VARIABLES,
    CLAIM_OPERATE,
    DEFAULT_BK_BIZ_ID,
    DEFAULT_ENGINE_VERSION,
    DEFAULT_ORDER,
    DEFAULT_STRING,
    DELIVER_OPERATE,
    DERIVE,
    DISTRIBUTE_OPERATE,
    DISTRIBUTE_TYPE_ACTION_DICT,
    DISTRIBUTE_TYPE_CHOICES,
    DISTRIBUTING,
    EXCEPTION_DISTRIBUTE_OPERATE,
    EMPTY_DICT,
    EMPTY_INT,
    EMPTY_LIST,
    EMPTY_STRING,
    FAILED,
    FIELD_PRIORITY,
    FIELD_PX_URGENCY,
    FIELD_PY_IMPACT,
    FIELD_STATUS,
    FINISHED,
    FOLLOW_OPERATE,
    LEN_LONG,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_SHORT,
    MASTER_SLAVE,
    NORMAL_STATE,
    OPERATE_TYPE,
    PERSON,
    PRIORITY,
    PROCESSOR_CHOICES,
    QUEUEING,
    RECEIVING,
    RELATE_CHOICES,
    RUNNING,
    SERVICE_CATEGORY,
    STARTER,
    STARTER_LEADER,
    STATE_TYPE_CHOICES,
    STATUS_CHOICES,
    SUSPEND,
    SUSPEND_OPERATE,
    SYS,
    SYSTEM_OPERATE,
    TASK_SOPS_STATE,
    TASK_STATE,
    TERMINATE_OPERATE,
    TERMINATED,
    UNSUSPEND_OPERATE,
    VARIABLE,
    VIRTUAL_TRANSITION_ID,
    WEB,
    WITHDRAW_OPERATE,
    TABLE,
    SIGN_STATE,
    APPROVAL_STATE,
    APPROVE_RESULT,
    NODE_APPROVE_RESULT,
    PROCESS_COUNT,
    PASS_COUNT,
    REJECT_COUNT,
    PASS_RATE,
    REJECT_RATE,
    ORGANIZATION,
    TICKET_GLOBAL_VARIABLES,
    REL_SUMMARY_FIELDS,
    TIME_DURATION_SUMMARY_FIELDS,
    GENERAL,
    SOPS_TASK,
    NOTIFY_FOLLOWER_OPERATE,
    TICKET_STATUS_DICT,
    INVITE_OPERATE,
    CACHE_1H,
    RETRY,
    IGNORE,
    API_DICT,
    PROCESS_FINISHED,
    END_TASK_STATUS,
    TICKET_END_STATUS,
    QUEUE,
    VERSION,
    REVOKE_TYPE,
    ASSIGN_LEADER,
    TIME_DELTA,
    LEN_XX_LONG,
    TASK_DEVOPS_STATE,
    WEBHOOK_STATE,
    BK_PLUGIN_STATE,
)
from itsm.component.constants.trigger import (
    CREATE_TICKET,
    CLOSE_TICKET,
    CREATE_RELATE_TICKET,
    TERMINATE_TICKET,
    SUSPEND_TICKET,
    RECOVERY_TICKET,
    DELETE_TICKET,
    ENTER_STATE,
    LEAVE_STATE,
    THROUGH_TRANSITION,
    SOURCE_TICKET,
    GLOBAL_LEAVE_STATE,
    GLOBAL_ENTER_STATE,
)
from common.shortuuid import uuid as _uu
from itsm.component.utils.client_backend_query import (
    get_user_leader,
    get_user_departments,
    get_bk_users,
    get_bk_business,
)
from itsm.sla_engine.constants import (
    RUNNING as SLA_RUNNING,
    PAUSED as SLA_PAUSED,
    STOPPED as SLA_STOPPED,
)
from itsm.component.exceptions import (
    CallPipelineError,
    RevokePipelineError,
    ObjectNotExist,
    DeliverOperateError,
)
from itsm.component.utils.basic import dotted_name, list_by_separator
from itsm.component.utils.bk_bunch import bunchify
from itsm.component.utils.conversion import (
    format_exp_value,
    conditions_conversion,
    rsp_conversion,
    build_conditions_by_mako_template,
)
from itsm.component.utils.graph import dfs_paths
from itsm.component.utils.misc import transform_single_username, transform_username
from itsm.component.utils.dimensions import fill_time_dimension
from itsm.iadmin.contants import (
    TRANSITION_OPERATE,
    WAITING_FOR_OPERATE,
    WAITING_FOR_CONFIRM,
)
from itsm.postman.models import RemoteApiInstance
from itsm.role.models import RoleType, UserRole
from itsm.service.api import get_catalog_fullname, get_service_name
from itsm.service.models import Service, ServiceSla, SysDict
from itsm.sla.models import PriorityMatrix, Sla, SlaTicketHighlight
from itsm.sla_engine.constants import HANDLE_TIMEOUT, REPLY_TIMEOUT
from itsm.sla_engine.models import SlaTask
from itsm.task.models import Task
from itsm.ticket import managers
from itsm.ticket.models import (
    TicketComment,
    TicketEventLog,
    TicketField,
    TicketGlobalVariable,
    TaskField,
    TicketFollowerNotifyLog,
)
from itsm.ticket_status.models import StatusTransit, TicketStatus
from itsm.ticket_status.serializers import TicketStatusOptionSerializer
from itsm.trigger.signal import trigger_signal
from itsm.workflow.api import get_first_state, get_ticket_flow
from itsm.workflow.backend import PipelineWrapper
from itsm.workflow.models import TaskSchema, GlobalVariable, TaskConfig
from pipeline.engine import api as pipeline_api
from pipeline.service import task_service
from pipeline.utils.boolrule import BoolRule
from itsm.component.utils.client_backend_query import (
    get_department_info,
    list_departments_info,
)
from platform_config import BaseTicket

from .basic import Model
from ...auth_iam.utils import IamRequest


class SignTask(Model):
    """会签任务表"""

    TASK_STATUS_CHOICES = [
        ("WAIT", "未激活"),
        ("RUNNING", "执行中"),
        ("EXECUTED", "已执行"),
        ("FINISHED", "已完成"),
    ]

    status_id = models.IntegerField(_("状态ID"))
    order = models.IntegerField(_("顺序"), default=DEFAULT_ORDER)
    status = models.CharField(
        _("任务状态"), max_length=LEN_SHORT, choices=TASK_STATUS_CHOICES, default="WAIT"
    )
    processor = models.CharField(_("处理人"), max_length=LEN_LONG)
    is_passed = models.NullBooleanField(_("是否审批通过"), null=True)

    objects = managers.SignTaskManager()

    class Meta:
        verbose_name = _("会签任务")
        verbose_name_plural = _("会签任务")
        ordering = ("-id",)

    def __unicode__(self):
        return "{}-{}({})".format(self.status_id, self.order, self.status)


class Status(Model):
    """节点处理状态
    meta:
        meta.ticket_status 进入节点的单据状态
        ticket_status.type 单据状态类型: "keep": 保持, "custom": 自定义
        ticket_status.key 单据状态key
    """

    STOPPED_STATUS = [FINISHED, TERMINATED, FAILED]
    PAUSED_STATUS = [SUSPEND]
    RUNNING_STATUS = [RUNNING, RECEIVING, DISTRIBUTING, QUEUEING]
    CAN_OPERATE_STATUS = RUNNING_STATUS + PAUSED_STATUS

    ticket_id = models.IntegerField(_("单据ID"), db_index=True)
    by_flow = models.CharField(_("进入节点的线条ID"), max_length=64, default="")
    state_id = models.IntegerField(_("节点ID"))
    bk_biz_id = models.IntegerField(_("业务ID"), default=DEFAULT_BK_BIZ_ID)
    name = models.CharField(_("节点名"), max_length=LEN_NORMAL, default=EMPTY_STRING)
    type = models.CharField(
        _("节点类型类型"),
        max_length=LEN_SHORT,
        choices=STATE_TYPE_CHOICES,
        default=NORMAL_STATE,
        db_index=True,
    )
    is_sequential = models.BooleanField(_("是否是串行任务"), default=False)
    status = models.CharField(
        _("节点状态"),
        max_length=LEN_SHORT,
        choices=STATUS_CHOICES,
        default="WAIT",
        db_index=True,
    )
    tag = models.CharField(_("节点标签"), max_length=LEN_LONG, default=DEFAULT_STRING)
    action_type = models.CharField(
        _("节点内部操作类型"),
        max_length=LEN_SHORT,
        choices=ACTION_CHOICES,
        default=TRANSITION_OPERATE,
    )
    distribute_type = models.CharField(
        _("分配方式"),
        max_length=LEN_SHORT,
        choices=DISTRIBUTE_TYPE_CHOICES,
        default="PROCESS",
    )
    # 当前环节处理人
    processors_type = models.CharField(
        _("处理人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )
    processors = models.CharField(
        _("处理人列表"), max_length=LEN_XX_LONG, default=EMPTY_STRING, null=True, blank=True
    )
    # 被转单人
    delivers_type = models.CharField(
        _("转单人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )
    delivers = models.TextField(_("转单人列表"), default=EMPTY_STRING, null=True, blank=True)
    can_deliver = models.BooleanField(_("能否转单"), default=False)

    # 被分派人
    # TODO assignors_type/assignors是被分派人
    assignors_type = models.CharField(
        _("派单人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )
    assignors = models.TextField(
        _("派单人列表"), default=EMPTY_STRING, null=True, blank=True
    )
    can_terminate = models.BooleanField(_("能否强制终止"), default=False)
    terminate_message = models.TextField(
        _("终止原因"), default=EMPTY_STRING, null=True, blank=True
    )

    fields = jsonfield.JSONField(_("字段列表"), default=EMPTY_LIST)
    api_instance_id = models.IntegerField(
        _("api实例主键"), default=0, null=True, blank=True
    )
    error_message = models.TextField(_("失败信息"), blank=True, null=True)

    # contexts: 目前存储了标准运维节点的请求参数
    contexts = jsonfield.JSONField(_("状态上下文"), default=EMPTY_DICT)
    meta = jsonfield.JSONField(_("配置信息"), default=EMPTY_DICT)
    query_params = jsonfield.JSONField(_("表单输入信息"), default=EMPTY_DICT)
    ignore_params = jsonfield.JSONField(_("忽略结果参数"), default=EMPTY_DICT)
    objects = managers.StatusManager()

    class Meta:
        verbose_name = _("节点处理状态")
        verbose_name_plural = _("节点处理状态")
        ordering = ("-id",)

    def __unicode__(self):
        return "{}({})".format(self.state_id, self.status)

    def set_processors(self, processors_type, processors):
        """设置处理人及角色"""
        self.processors_type = processors_type
        self.processors = processors
        self.save(update_fields=("processors_type", "processors"))
        self.ticket.set_current_processors()

    def get_processor_in_sign_state(self):
        """获取会签节点的当前处理人
        依次会签当前处理人: 去掉所有已处理人-> 按照依次会签顺序排序的首个待处理人
        随机会签当前处理人: 所有待处理人
        """
        tasks = SignTask.objects.filter(
            status_id=self.id, status__in=["RUNNING", "EXECUTED", "FINISHED"]
        )
        processed_user_list = tasks.values_list("processor", flat=True)
        user_list = UserRole.get_users_by_type(
            self.bk_biz_id, self.processors_type, self.processors, self.ticket
        )
        # Filter unprocessed user
        processor_list = list(set(user_list).difference(processed_user_list))

        def custom_cmp(x, y):
            keep = -1
            reverse = 1
            if user_list.index(x) < user_list.index(y):
                return keep
            else:
                return reverse

        processor_list.sort(key=functools.cmp_to_key(custom_cmp))

        if self.is_sequential and processor_list:
            processor = processor_list[0]
        else:
            processor = ",".join(processor_list)

        return processor

    def set_history_operators(self, current_operator):
        """设置历史处理人"""
        if self.updated_by is None:
            self.updated_by = current_operator
        else:
            history_operators = [user for user in self.updated_by.split(",") if user]
            if current_operator not in history_operators:
                history_operators.append(current_operator)
            self.updated_by = dotted_name(",".join(set(history_operators)))
        self.save(update_fields=("updated_by",))

    def get_user_list(self):
        user_list = UserRole.get_users_by_type(
            self.bk_biz_id, self.processors_type, self.processors, self.ticket
        )
        return user_list

    def sign_is_finished(self, finish_condition, key_value):
        """
        Determine whether sign node finished
        """
        if not finish_condition:
            finish_condition = {"expressions": [], "type": "or"}
        conditions = conditions_conversion(finish_condition)
        # 如果未配置条件就不需要进行规则判断，直接判定is_finished为False
        if conditions:
            key_value_copy = copy.deepcopy(key_value)
            rsp_conversion(key_value_copy)
            b_result, b_conditions = build_conditions_by_mako_template(
                conditions, key_value_copy
            )
            is_finished = BoolRule(b_conditions).test()
        else:
            is_finished = False

        # 即使未满足结束条件 但节点没有处理人 节点仍然继续流转
        if not is_finished and not self.get_processor_in_sign_state():
            return True

        return is_finished

    def set_status(self, status, operator="system", **kwargs):
        """设置状态"""

        self.status = status
        self.updated_by = operator

        if status == TERMINATED:
            self.terminate_message = kwargs.get("terminate_message", "")

        if status in self.STOPPED_STATUS:
            # 挂起操作并未结束
            self.end_at = datetime.now()

        self.save()

    def set_failed_status(self, operator="system", **kwargs):
        """设置失败状态和失败日记"""
        self.error_message = kwargs.get("message", "")
        self.set_status(FAILED, operator, **kwargs)
        self.create_action_log(
            operator,
            self.error_message,
            detail_message=kwargs.get("detail_message", ""),
            action_type=SYSTEM_OPERATE,
            source=SYSTEM_OPERATE,
        )
        self.update_contexts()

    def update_contexts(self, **kwargs):
        self.contexts.update(**kwargs)
        self.save()

    def run_auto_approve(self, state_id):
        from itsm.pipeline_plugins.components.collections.tasks import auto_approve

        if not state_id:
            return

        msg = "检测到当前处理人包含提单人，系统自动过单"
        callback_data = {
            "fields": self.ticket.get_approve_fields(state_id, msg),
            "ticket_id": self.ticket.id,
            "source": "SYS",
            "operator": self.ticket.creator,
            "state_id": state_id,
        }
        logger.info(
            "检测到当前单据开启了自动过单，即将准备自动过单, ticket_id={}, state_id={}, callback_data={}".format(
                self.ticket.id, state_id, callback_data
            )
        )
        activity_id = self.ticket.activity_for_state(state_id)
        auto_approve.apply_async(
            (self.id, self.ticket.creator, activity_id, callback_data),
            countdown=settings.AUTO_APPROVE_TIME,
        )  # 20秒之后自动回调

    def set_next_action(self, operator="system", **kwargs):
        """
        设置节点的操作动作和状态
        :param operator: 操作人
        """

        message, detail_message = self.get_log_message(**kwargs)
        action_type = kwargs["action_type"]
        ticket = kwargs.pop("ticket", None)
        real_processors = UserRole.get_users_by_type(
            ticket.bk_biz_id,
            kwargs.get("processors_type", "PERSON"),
            kwargs.get("processors"),
            ticket,
        )

        with transaction.atomic():
            if action_type in [
                CLAIM_OPERATE,
                DISTRIBUTE_OPERATE,
                DELIVER_OPERATE,
                EXCEPTION_DISTRIBUTE_OPERATE,
            ]:

                finished_processor_list = list(
                    SignTask.objects.filter(
                        status_id=self.id, status=FINISHED
                    ).values_list("processor", flat=True)
                )
                new_processor_list = UserRole.get_users_by_type(
                    self.bk_biz_id,
                    kwargs.get("processors_type"),
                    kwargs.get("processors"),
                    self.ticket,
                )
                if set(finished_processor_list) & set(new_processor_list):
                    raise DeliverOperateError("不允许向已经处理的人转单")

                self.set_processors(
                    kwargs.get("processors_type", "PERSON"), kwargs.get("processors")
                )
                if (
                    self.ticket.creator in new_processor_list
                    and self.ticket.flow.is_auto_approve
                    and self.type == "APPROVAL"
                ):
                    # 提单人异常分派给自己的情况，并且开启了自动过单

                    if "state_id" in kwargs:
                        self.run_auto_approve(kwargs.get("state_id"))

            if action_type in [CLAIM_OPERATE, DISTRIBUTE_OPERATE]:
                # 操作流状态机：派单->认领->处理
                valid_actions = DISTRIBUTE_TYPE_ACTION_DICT.get(self.distribute_type)

                for index, action in enumerate(valid_actions):
                    # 找到当前状态
                    if action[0] != self.action_type:
                        continue

                    if index == len(valid_actions) - 1:
                        self.set_status(FINISHED, operator)
                        return

                    next_action = valid_actions[index + 1]
                    if next_action[0] == "CLAIM" and len(real_processors) == 1:
                        self.status = RUNNING
                        self.action_type = TRANSITION_OPERATE
                    else:
                        self.action_type = next_action[0]
                        self.status = next_action[1]
                    self.updated_by = operator
                    self.save()

                    break
            tlog = self.create_action_log(operator, message, detail_message, **kwargs)

        self.ticket.send_trigger_signal("%s_STATE" % action_type, self.state_id)

        # 通知可以考虑去掉
        self.notify(action_type, tlog.translated_message)

    def notify(self, action_type, message):
        # 节点通知发送
        retry = True

        if action_type in [SUSPEND_OPERATE, UNSUSPEND_OPERATE, TERMINATED]:
            receivers = self.ticket.creator
            notify_action = action_type
            retry = False
        else:
            receivers = ",".join(self.get_processors())
            notify_action = TRANSITION_OPERATE

        # 撤单/认领不通知
        if action_type in [WITHDRAW_OPERATE, CLAIM_OPERATE]:
            return

        self.ticket.notify(
            state_id=self.state_id,
            receivers=receivers,
            message=message,
            action=notify_action,
            retry=retry,
        )

    def create_action_log(self, operator, message, detail_message="", **kwargs):
        return TicketEventLog.objects.create_log(
            ticket=self.ticket,
            state_id=self.state_id,
            log_operator=operator,
            operate_type=kwargs.get("action_type"),
            message=message,
            detail_message=detail_message,
            from_state_name=self.name,
            action=ACTION_DICT.get(kwargs.get("action_type")),
            transition_id=VIRTUAL_TRANSITION_ID,
            to_state_id=self.state_id,
            source=kwargs["source"],
            fields=kwargs.get("fields"),
        )

    def get_log_message(self, **kwargs):
        detail_message = kwargs.get("action_message")
        action_type = kwargs.get("action_type", "")
        processors_type = kwargs.get("processors_type", PERSON)
        processors = kwargs.get("processors")

        if action_type in [DISTRIBUTE_OPERATE, EXCEPTION_DISTRIBUTE_OPERATE]:
            distribute_message = self.log_detail(processors_type, processors)
            detail_message = (
                distribute_message + " (%s)" % detail_message
                if detail_message
                else distribute_message
            )
            log_message = "{operator} 分配【{name}】给：{detail_message}."

        elif detail_message:
            if action_type == DELIVER_OPERATE:
                processor_name = self.log_detail(processors_type, processors)
                detail_message = "{}({})".format(processor_name, detail_message)
                log_message = "{operator} {action}【{name}】给 {detail_message}."
            else:
                log_message = "{operator} {action}【{name}】（{detail_message}）."

        else:
            log_message = "{operator} {action}【{name}】."

        return log_message, detail_message

    def log_detail(self, processors_type, processors):
        if processors_type == PERSON:
            detail_message = transform_username(processors)
        elif processors_type == ORGANIZATION:
            organization = get_department_info(processors).get("name", "")
            detail_message = "{} -> {}".format(_("组织架构"), organization)
        else:
            detail_message = "{} -> {}".format(
                _(RoleType.objects.get(type=processors_type).name),
                ",".join(
                    [
                        _(role.name)
                        for role in UserRole.objects.filter(
                            id__in=processors.split(",")
                        )
                    ]
                ),
            )
        return detail_message

    def is_action_permit(self, action_type):
        """校验操作是否合法"""
        if self.status == RUNNING:
            return action_type in [
                TRANSITION_OPERATE,
                DELIVER_OPERATE,
                SUSPEND_OPERATE,
                TERMINATE_OPERATE,
            ]
        elif self.status == RECEIVING:
            return action_type in [CLAIM_OPERATE]
        elif self.status == DISTRIBUTING:
            return action_type in [DISTRIBUTE_OPERATE]
        elif self.status == SUSPEND:
            return action_type == UNSUSPEND_OPERATE
        else:
            return False

    def can_first_state_operate(self, username, bk_biz_id):
        """能否提单"""

        if self.processors_type == "OPEN":
            return True

        return username in UserRole.get_users_by_type(
            bk_biz_id, self.processors_type, self.processors, self.ticket
        )

    def can_sign_state_operate(self, username):
        """Sign state operate permission"""
        processor = self.get_processor_in_sign_state()
        processor_list = list_by_separator(processor)
        return username in processor_list

    def can_operate(self, username, action_type=None):
        """能否审批/派单/认领节点"""
        if self.type in [SIGN_STATE, APPROVAL_STATE]:
            return self.can_sign_state_operate(username)

        if self.processors_type == "OPEN":
            return True

        rules = [not self.is_stopped, self.is_operator(username)]

        if action_type:
            rules.append(self.is_action_permit(action_type))

        return all(rules)

    def can_view(self, username, request=None):
        """能否查看节点"""

        # 判断用户是否工单统计管理员，工单统计管理员无条件可以查看
        if UserRole.is_statics_manager(username):
            return True

        # 超级管理员放这里，can_operate里带有工单是否结束的判断，无法过滤
        if UserRole.is_itsm_superuser(username):
            return True

        # 我是当前处理人或历史处理人或过渡态的处理人
        return self.is_operator(username)

    def can_derive(self, username, action_type=None):
        if UserRole.is_itsm_superuser(username):
            return True

        if self.processors_type == "OPEN":
            return True

        rules = [self.is_operator(username)]

        if action_type:
            rules.append(self.is_action_permit(action_type))

        return all(rules)

    def can_create_task(self, username="", is_system=False):
        if self.ticket.current_status == "SUSPENDED" or self.ticket.is_over:
            return False

        rules = [True] if is_system else [self.can_operate(username)]
        can_create = TaskConfig.objects.filter(
            Q(workflow_id=self.ticket.flow_id, workflow_type=VERSION)
            & Q(
                Q(create_task_state=self.state_id)
                | Q(execute_task_state=self.state_id, execute_can_create=True)
            )
        ).exists()
        rules.append(can_create)

        return all(rules)

    def can_execute_task(self, username="", is_system=False):
        if self.ticket.current_status == "SUSPENDED" or self.ticket.is_over:
            return False

        rules = []
        can_execute = TaskConfig.objects.filter(
            workflow_id=self.ticket.flow_id,
            execute_task_state=self.state_id,
            workflow_type=VERSION,
        ).exists()
        rules.append(can_execute)

        return all(rules)

    @property
    def task_schemas(self):
        task_schema_ids = self.ticket.flow.task_schema_ids(self.state_id)
        return [
            {"id": item.id, "name": item.name}
            for item in TaskSchema.objects.filter(id__in=task_schema_ids)
        ]

    def update_execute_state_id(self):
        """
        更新某个单据下所有任务的执行节点
        """

        tasks = Task.objects.filter(ticket_id=self.ticket_id)
        for task in tasks:
            task.execute_state_id = self.state_id
            task.save()

    def start_task(self, **kwargs):
        """启动单据下的任务"""
        from itsm.task.backend import TaskPipelineWrapper

        self.update_execute_state_id()

        order_obj = Task.objects.filter(
            ticket_id=self.ticket_id, execute_state_id=self.state_id
        ).values_list("order")
        if order_obj:
            sorted_id = sorted(set([obj[0] for obj in order_obj]))

            task_objs = Task.objects.filter(
                ticket_id=self.ticket_id,
                execute_state_id=self.state_id,
                order=sorted_id[0],
            )
            for obj in task_objs:
                task_pipeline_wrapper = TaskPipelineWrapper(self.ticket_id, obj.id)
                task_pipeline_wrapper.start_pipeline(obj.pipeline_data)

    def is_operator(self, username):
        """是否在审批/派单/认领列表中"""
        return username in self.get_processors()

    def get_sign_display_processors(self):
        """获取会签节点处理人/角色显示名称"""
        display_name = ""
        if self.processors_type in ["GENERAL", "CMDB"]:
            role_ids = list_by_separator(self.processors)
            roles = UserRole.objects.filter(id__in=role_ids)
            role_name_list = list(roles.values_list("name", "members"))
            if self.processors_type == "CMDB":
                if self.bk_biz_id == DEFAULT_BK_BIZ_ID:
                    return []

                cmdb_users = get_bk_business(
                    self.bk_biz_id, role_type=[role.role_key for role in roles]
                )
                display_name = "{}({})".format(
                    "CMDB业务公用角色", ",".join(list_by_separator(cmdb_users))
                )

            if self.processors_type == "GENERAL":
                role_name_members_list = [
                    "{}({})".format(role_name[0], role_name[1].strip(","))
                    for role_name in role_name_list
                ]
                display_name = ",".join(role_name_members_list)

        if self.processors_type == "PERSON":
            users = self.get_processor_in_sign_state()
            if self.is_sequential:
                display_name = transform_username(users)
            else:
                user_list = [user for user in users.split(",") if user]
                display_name = transform_username(user_list)

        if self.processors_type == "ORGANIZATION":
            display_name = get_department_info(self.processors.strip(",")).get(
                "name", ""
            )

        return display_name

    @staticmethod
    def get_organization_name(department_id):
        return get_department_info(department_id).get("name", "")

    def get_appover_key_value(self, code_key):
        code = code_key.get("NODE_APPROVER", None)
        key_value = {}
        if code is None:
            return key_value
        sign_tasks = SignTask.objects.filter(status_id=self.id)
        processors = []
        for sign_task in sign_tasks:
            processors.append(sign_task.processor)
        key_value[code] = ",".join(processors)
        return key_value

    def get_sign_key_value(self, ticket, code_key):
        """
        获取会签节点output的键值对
        :param ticket 单据对象
        :param code_key 输出变量code和key的映射关系
        """
        key_value = {}
        code_list = [PROCESS_COUNT, PASS_COUNT, REJECT_COUNT, PASS_RATE, REJECT_RATE]
        user_list = UserRole.get_users_by_type(
            ticket.bk_biz_id, self.processors_type, self.processors, ticket
        )
        context = {"total_count": len(user_list)}

        for code in code_list:
            method_name = "sign_" + code.lower()
            method = getattr(self, method_name)
            value = method(**context)
            if code in code_key:
                key_value[code_key[code]] = value

        return key_value

    def sign_process_count(self, **kwargs):
        """会签节点完成数"""
        return SignTask.objects.filter(
            status_id=self.id, status__in=["EXECUTED", "FINISHED"]
        ).count()

    def sign_pass_count(self, **kwargs):
        """会签节点通过数"""
        return SignTask.objects.filter(
            status_id=self.id, status__in=["EXECUTED", "FINISHED"], is_passed=True
        ).count()

    def sign_reject_count(self, **kwargs):
        """会签节点拒绝数"""
        return SignTask.objects.filter(
            status_id=self.id, status__in=["EXECUTED", "FINISHED"], is_passed=False
        ).count()

    def sign_pass_rate(self, total_count, **kwargs):
        """会签节点通过率"""
        return (self.sign_pass_count() / total_count) * 100

    def sign_reject_rate(self, total_count, **kwargs):
        """会签节点拒绝率"""
        return (self.sign_reject_count() / total_count) * 100

    def get_processors(self):
        if self.action_type == SYSTEM_OPERATE:
            return [_("系统自动处理")]

        return UserRole.get_users_by_type(
            self.ticket.bk_biz_id, self.processors_type, self.processors, self.ticket
        )

    def get_delivers(self):
        return UserRole.get_users_by_type(
            self.ticket.bk_biz_id, self.delivers_type, self.delivers, self.ticket
        )

    def get_assignors(self):
        return UserRole.get_users_by_type(
            self.ticket.bk_biz_id, self.assignors_type, self.assignors, self.ticket
        )

    @property
    def is_schedule_ready(self):
        """是否结束需要通过节点属性来控制"""

        schema_ids = TaskConfig.objects.filter(
            workflow_id=self.ticket.flow_id,
            workflow_type=VERSION,
            execute_task_state=self.state_id,
            need_task_finished=True,
        ).values_list("task_schema_id", flat=True)
        is_exists = (
            Task.objects.filter(
                ticket_id=self.ticket.pk,
                execute_state_id=self.state_id,
                task_schema_id__in=schema_ids,
            )
            .exclude(status__in=END_TASK_STATUS)
            .exists()
        )

        return not is_exists

    @property
    def from_transition_id(self):
        return self.ticket.pipeline_data.get("transitions_map", {}).get(self.by_flow)

    @property
    def origin_assignors(self):
        return self.assignors

    @property
    def origin_delivers(self):
        return self.delivers

    @property
    def origin_processors(self):
        return self.processors

    def _build_actions(self, operate_key, can_operate=True):
        return {
            "key": operate_key,
            "name": ACTION_DICT.get(operate_key),
            "can_operate": can_operate,
        }

    def get_ticket_status_setting(self, service_type):
        """获取单据状态设置项"""
        setting = self.meta.get("ticket_status")

        # 是否配置自定义设置单据状态
        if setting and isinstance(setting, dict) and setting.get("type") == "custom":
            # 剔除`筛选单据状态`的无效属性
            pop_attrs = ["type"]
            for i in pop_attrs:
                setting.pop(i, None)

            from_ticket_status = TicketStatus.objects.get(
                service_type=service_type, key=self.ticket.current_status
            )

            if setting.get("name") in TICKET_STATUS_DICT.keys():
                to_ticket_status = (
                    TicketStatus.objects.filter(service_type=service_type)
                    .filter(key=setting.get("name"))
                    .first()
                )
            else:
                to_ticket_status = (
                    TicketStatus.objects.filter(service_type=service_type)
                    .filter(name=setting.get("name"))
                    .first()
                )

            # 是否满足单据状态流转设置
            if (
                to_ticket_status
                and to_ticket_status.id in from_ticket_status.to_status_id_set
            ):
                return to_ticket_status

            to_ticket_status_name = to_ticket_status.name if to_ticket_status else None
            logger.error(
                "流程设计的设置单据状态不存在或者不满足单据状态流转设置, 详情: 单号(%s) 源单据状态(%s)->目标单据状态(%s)"
                % (self.ticket.sn, from_ticket_status.name, to_ticket_status_name)
            )

    def get_operations(self, username, can_operate=None):
        """获取节点操作列表"""

        operations = []

        # 自动节点暂不支持手动干预
        if self.action_type == SYSTEM_OPERATE:
            return operations

        if can_operate is None:
            can_operate = self.can_operate(username)

        # 审批/派单/认领 + 挂起 + 转单 + 终止
        if can_operate:
            operations = self.operations

        return operations

    @property
    def operations(self):

        # sla响应
        # if self.is_reply_need and not self.is_replied:
        #     return [{"key": REPLY, "name": REPLY_NAME, "can_operate": True}]

        operations = []

        # 被挂起后必须先解挂
        if self.is_paused:
            operations.append(self._build_actions(UNSUSPEND_OPERATE))
            return operations

        # 审批/派单/认领
        operations.append(self._build_actions(self.action_type))

        # 非审批状态下（转单/认领），不支持其他操作
        if self.action_type != TRANSITION_OPERATE:
            return operations

        # 挂起
        operations.append(self._build_actions(SUSPEND_OPERATE))
        # 转单
        if self.can_deliver:
            operations.append(self._build_actions(DELIVER_OPERATE))
        # 终止
        if self.can_terminate:
            operations.append(self._build_actions(TERMINATE_OPERATE))

        return operations

    @property
    def ticket(self):
        return Ticket._objects.get(id=self.ticket_id)

    @property
    def state(self):
        return self.ticket.flow.states.get(str(self.state_id))

    @property
    def trigger(self):
        return []

    @property
    def ticket_fields(self):
        """从单据字段中获取节点字段信息"""
        workflow_field_order = self.ticket.flow.states.get(str(self.state_id))["fields"]

        if not workflow_field_order:
            return self.ticket.fields.filter(state_id=self.state_id)
        clauses = " ".join(
            [
                "WHEN workflow_field_id=%s THEN %s" % (pk, index)
                for index, pk in enumerate(workflow_field_order)
            ]
        )
        ordering = "CASE %s END" % clauses

        filter_experssion = Q(state_id=self.state_id) | Q(
            workflow_field_id__in=workflow_field_order
        )

        if self.is_first_status:
            filter_experssion = filter_experssion | Q(workflow_field_id=0)

        return (
            self.ticket.fields.filter(filter_experssion)
            .exclude(source=BASE_MODEL)
            .extra(
                select={"ordering": ordering},
                order_by=(
                    "ordering",
                    "id",
                ),
            )
        )

    def approval_result(self, result, opinion):
        fields = []
        node_fields = self.ticket_fields.only("id", "key", "meta")
        for field in node_fields:
            value = result if field.meta.get("code") == APPROVE_RESULT else opinion
            fields.append({"id": field.id, "key": field.key, "value": value})
        return fields

    @property
    def can_suspend(self):
        return self.ticket.current_status in self.RUNNING_STATUS

    @property
    def is_paused(self):
        return self.ticket.current_status in self.PAUSED_STATUS

    @property
    def is_running(self):
        """待审批/派单/认领"""
        return self.status in self.RUNNING_STATUS

    @property
    def is_stopped(self):
        """结束/终止/失败"""
        stop_status = copy.deepcopy(self.STOPPED_STATUS)
        if self.type in [
            TASK_STATE,
            TASK_SOPS_STATE,
            TASK_DEVOPS_STATE,
            WEBHOOK_STATE,
            BK_PLUGIN_STATE,
        ]:
            stop_status.pop()
        return self.status in stop_status

    @property
    def is_first_status(self):
        """提单节点"""
        return str(self.state_id) == self.ticket.first_state_id

    @property
    def api_instance(self):
        """API实例"""
        try:
            return RemoteApiInstance._objects.get(id=self.api_instance_id)
        except RemoteApiInstance.DoesNotExist:
            return None

    @property
    def global_variables(self):
        """API实例产出的变量"""
        return TicketGlobalVariable.objects.get_global_variables(
            self.ticket_id, self.state_id
        )

    @property
    def processed_user(self):
        processed = self.ticket.logs.filter(from_state_id=self.state_id).values_list(
            "operator", flat=True
        )
        return ",".join(
            set(self.processors.strip(",").split(",")) & set(list(processed))
        )

    # ======================================= SLA功能接口 =====================================

    @property
    def is_reply_need(self):
        """
        是否需要响应
        响应只在SLA任务开始节点执行
        开始节点相同的SLA任务，若需要响
        """
        return SlaTask.objects.filter(
            ticket_id=self.ticket_id,
            start_node_id=self.state_id,
            is_reply_need=True,
            is_replied=False,
        ).exists()

    @property
    def is_replied(self):
        """是否已响应"""
        return SlaTask.objects.filter(
            ticket_id=self.ticket_id,
            start_node_id=self.state_id,
            is_reply_need=True,
            is_replied=True,
        ).exists()

    @property
    def sla_tasks(self):
        """返回该节点所处的SLA任务集合"""

        tasks = SlaTask.objects.filter(ticket_id=self.ticket_id)

        service_sla_objs = ServiceSla.objects.filter(
            service_id=self.ticket.service_id,
            sla_id__in=tasks.values_list("sla_id", flat=True),
        ).values("sla_id", "states")

        sla_ids = []
        for obj in service_sla_objs:
            if self.state_id in obj["states"]:
                sla_ids.append(obj["sla_id"])

        state_tasks = tasks.filter(sla_id__in=sla_ids)

        return state_tasks

    def nearest_sla_task_info(self):
        """
        当前节点所挂载的SLA任务中，返回时间最近的任务
        return dict(sla_status, task_status, deadline, end_at, sla_timeout)
        """

        from itsm.sla_engine.constants import NORMAL, RUNNING, UNACTIVATED

        sla_tasks = self.sla_tasks.filter(task_status=RUNNING)
        if not sla_tasks.exists():
            return dict(
                sla_status=NORMAL,
                task_status=UNACTIVATED,
                deadline=None,
                end_at=None,
                sla_timeout=[0] * 6,
            )

        task = sla_tasks.order_by("deadline").first()

        task_info = dict(
            sla_status=task.sla_status,
            task_status=task.task_status,
            deadline=task.deadline,
            end_at=task.end_at,
        )
        task_info.update(
            sla_timeout=self.sla_timeout(task_info["deadline"], task_info["end_at"])
        )

        return task_info

    @staticmethod
    def sla_timeout(deadline, stop_time):

        if not deadline:
            return [0] * 6
        else:
            if not stop_time:
                delta = relativedelta(deadline, datetime.now())
            else:
                delta = relativedelta(deadline, stop_time)
            return [
                int(getattr(delta, attr))
                for attr in ["years", "months", "days", "hours", "minutes", "seconds"]
            ]


class Ticket(Model, BaseTicket):
    """工单表"""

    def __init__(self, *args, **kwargs):
        super(Ticket, self).__init__(*args, **kwargs)
        self.notify_url = ""

    sn = models.CharField(_("单据号"), max_length=LEN_NORMAL, db_index=True)
    title = models.CharField(_("单据名称"), max_length=LEN_MIDDLE)
    is_draft = models.BooleanField(_("是否为草稿"), default=True)

    # 服务目录ID
    catalog_id = models.IntegerField(_("服务目录ID"), default=EMPTY_INT)
    # 服务项ID
    service_id = models.IntegerField(_("服务项ID"), default=EMPTY_INT)
    # 服务类型 change,event,request,question
    service_type = models.CharField(
        _("服务编码"), default=DEFAULT_STRING, max_length=LEN_NORMAL, db_index=True
    )
    # 流程版本ID
    flow_id = models.IntegerField(_("流程版本ID"), default=EMPTY_INT)
    # 蓝鲸业务ID，默认为-1，即不绑定业务
    bk_biz_id = models.IntegerField(
        _("业务id"), default=DEFAULT_BK_BIZ_ID, blank=True, null=True
    )
    priority_key = models.CharField(
        _("优先级编码"), max_length=LEN_LONG, blank=True, null=True
    )
    # 单据对应的：pipeline_tree/states_map
    pipeline_data = jsonfield.JSONField(_("Pipeline流程树元数据"), default=EMPTY_DICT)

    node_status = models.ManyToManyField(Status, help_text=_("节点状态"))

    # 单据当前状态
    current_status = models.CharField(_("单据状态"), max_length=LEN_SHORT)
    # 单据前一状态
    pre_status = models.CharField(
        _("单据前一状态"), max_length=LEN_SHORT, default=EMPTY_STRING
    )

    is_supervise_needed = models.BooleanField(_("是否需要督办"), default=False)
    supervise_type = models.CharField(
        _("督办人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )
    supervisor = models.CharField(
        _("督办列表"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )

    current_task_processors = models.CharField(
        _("任务处理者列表"), max_length=LEN_LONG, default=EMPTY_STRING
    )
    history_task_processors = models.CharField(
        _("任务历史处理者列表"), max_length=LEN_LONG, default=EMPTY_STRING
    )

    # Deprecated Fields
    # 针对节点的字段需要迁移到新的表中
    current_state_id = models.CharField(_("当前状态ID"), null=True, max_length=LEN_NORMAL)
    current_assignor = models.CharField(
        _("分派人列表"), max_length=LEN_LONG, default=EMPTY_STRING
    )
    current_processors = models.CharField(
        _("处理者列表"), max_length=LEN_LONG, default=EMPTY_STRING
    )
    current_assignor_type = models.CharField(
        _("分派人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )
    current_processors_type = models.CharField(
        _("处理者类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )

    updated_by = models.CharField(_("修改人"), default=EMPTY_STRING, max_length=LEN_LONG)

    service = models.CharField(_("对应服务主键"), default="custom", max_length=LEN_NORMAL)
    service_property = jsonfield.JSONCharField(
        _("业务特性json字段"), max_length=LEN_LONG, default=EMPTY_DICT, null=True, blank=True
    )
    workflow_snap_id = models.IntegerField(_("对应的快照信息"), default=0)
    """
    meta.priority 优先级
         priority.key 优先级编码
         priority.name 优先级名称
         priority.order 优先级排序
    ---      
    meta.ticket_agent 代提单人
    meta.task_pipeline_id 任务流水线ID
    """
    meta = jsonfield.JSONField(_("扩展描述信息"), default=EMPTY_DICT)
    # 单据对应的业务信息
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    tag = models.CharField(
        _("单据标签"), max_length=LEN_SHORT, null=True, blank=True, db_index=True
    )

    objects = managers.TicketManager()

    auth_resource = {"resource_type": "ticket", "resource_type_name": "单据"}
    resource_operations = ["ticket_view", "ticket_management"]

    class Meta:
        verbose_name = _("工单")
        verbose_name_plural = _("工单")
        ordering = ("-id",)
        index_together = (
            ("create_at", "bk_biz_id", "service_id", "current_status", "service_type"),
            ("service_id", "create_at"),
            ("bk_biz_id", "service_id"),
            ("creator", "create_at"),
            ("current_status", "create_at"),
        )

    def __unicode__(self):
        return "{}({})".format(self.title, self.sn)

    @property
    def task_schemas(self):
        # todo 测试后删除
        task_schema_ids = [8]
        return [
            {"id": item.id, "name": item.name}
            for item in TaskSchema.objects.filter(id__in=task_schema_ids)
        ]

    @property
    def pipeline_message(self):
        """
        pipeline的错误信息
        """
        try:
            pipeline_info = pipeline_api.get_status_tree(str(self.id))
        except Exception as error:
            logger.warning("get pipeline status error {}".format(error))
            pipeline_info = {}
        for node_id, child in list(pipeline_info.get("children", {}).items()):
            if child["state"] == "FAILED":
                child["error_message"] = pipeline_api.get_outputs(node_id)
                return child
        return {}

    def waiting_approve(self, username):
        approval_status = self.node_status.filter(status=RUNNING, type=APPROVAL_STATE)
        for status in approval_status:
            if username in status.get_processor_in_sign_state():
                is_running = cache.get(
                    "approval_status_{}_{}_{}".format(
                        username, status.ticket_id, status.state_id
                    )
                )
                if not is_running:
                    return True
        return False

    @classmethod
    def batch_waiting_approve(cls, ticket_ids, username):
        all_status = Status.objects.filter(
            ticket_id__in=ticket_ids, status=RUNNING, type=APPROVAL_STATE
        )
        ticket_status = {}
        for status in all_status:
            ticket_status.setdefault(status.ticket_id, []).append(status)
        waiting_approve = {}
        for ticket_id, approval_status in ticket_status.items():
            for status in approval_status:
                if username in status.get_processor_in_sign_state():
                    is_running = cache.get(
                        "approval_status_{}_{}_{}".format(
                            username, status.ticket_id, status.state_id
                        )
                    )
                    if not is_running:
                        waiting_approve[ticket_id] = True
                        break
            else:
                waiting_approve[ticket_id] = False
        return waiting_approve

    @classmethod
    def get_batch_waiting_count(cls, ticket_ids, username):
        """
        获取批量审批剩余的数量
        """
        all_status = Status.objects.filter(
            ticket_id__in=ticket_ids, status=RUNNING, type=APPROVAL_STATE
        )
        ticket_status = {}
        for status in all_status:
            ticket_status.setdefault(status.ticket_id, []).append(status)
        count = 0
        for ticket_id, approval_status in ticket_status.items():
            for status in approval_status:
                if username in status.get_processor_in_sign_state():
                    is_running = cache.get(
                        "approval_status_{}_{}_{}".format(
                            username, status.ticket_id, status.state_id
                        )
                    )
                    # 如果发现缓存中有这条记录，说明当前单据还没有审批完，不然正在执行的state_id一定会变
                    if is_running:
                        count += 1
        return count

    @property
    def last_transition_id(self):
        """
        当前流程的最后一个节点记录
        """
        last_flow = self.pipeline_data.get("last_flow", "")
        return self.pipeline_data.get("transitions_map").get(last_flow)

    @cached_property
    def priority(self):
        """单据优先级
        系统规则: 优先级若为空，则返回最低优先级
        """
        # 优先级必定有值，否则数据错误
        priority_field = self.fields.filter(key=FIELD_PRIORITY).first()
        return priority_field.ticket.priority_key

    @property
    def priority_name(self):
        """优先级显示名称"""
        empty_priority_name = "--"
        # 单据已设置优先级
        if "priority" in self.meta:
            return self.meta["priority"].get("name", "")
        else:
            return empty_priority_name

    @property
    def ticket_url(self):
        if not self.notify_url:
            return "{site_url}/#/ticket/{ticket_id}/".format(
                site_url=settings.TICKET_NOTIFY_HOST.rstrip("/"), ticket_id=self.id
            )
        return self.notify_url

    @property
    def iframe_ticket_url(self):
        """专门用来做iframe嵌入的url"""
        return "{site_url}/#/ticket/detail-iframe?id={ticket_id}".format(
            site_url=settings.FRONTEND_URL.rstrip("/"), ticket_id=self.id
        )

    @property
    def pc_ticket_url(self):
        """专门用来做iframe嵌入的url"""
        return "{site_url}/#/ticket/detail?id={ticket_id}".format(
            site_url=settings.FRONTEND_URL.rstrip("/"), ticket_id=self.id
        )

    def generate_ticket_url(self, state_id, receivers):
        cache_key = _uu()
        status = Status.objects.filter(ticket_id=self.id, state_id=state_id).first()
        if not status:
            logger.info(
                "get status object does not exist, param: ticket_id={}, state_id={}".format(
                    self.id, state_id
                )
            )
            raise ObjectNotExist(_("没有获取到当前节点处理状态"))
        ticket_token = TicketFollowerNotifyLog.get_unique_token()
        TicketFollowerNotifyLog.objects.create(
            **{
                "ticket_token": ticket_token,
                "ticket": self,
                "followers": status.processors,
                "followers_type": status.processors_type,
                "state_id": state_id,
            }
        )
        client = Cache()
        self.notify_url = "{site_url}/#/ticket/{ticket_id}/?token={token}&cache_key={cache_key}".format(
            site_url=settings.TICKET_NOTIFY_HOST.rstrip("/"),
            ticket_id=self.id,
            token=ticket_token,
            cache_key=cache_key,
        )
        data = json.dumps({"state_id": state_id, "ticket_id": self.id})
        client.set(cache_key, data, 60 * 60 * 24 * 30)

    @property
    def service_type_name(self):
        return _(SERVICE_CATEGORY.get(self.service_type, self.service_type))

    @cached_property
    def flow(self):
        """流程版本"""
        return get_ticket_flow(self.flow_id)

    @cached_property
    def catalog_name(self):
        """服务名"""
        return self.catalog_fullname.split(">")[-1]

    @cached_property
    def catalog_fullname(self):
        """完整服务名"""
        return get_catalog_fullname(self.catalog_id)

    @cached_property
    def catalog_service_name(self):
        """完整服务目录+服务名"""
        return self.catalog_fullname + "->" + self.service_name

    @cached_property
    def service_name(self):
        """服务项名"""
        return get_service_name(self.service_id)

    @cached_property
    def service_instance(self):
        return Service._objects.get(id=self.service_id)

    @property
    def end_state(self):
        return self.flow.end_state

    @property
    def start_state(self):
        return self.flow.start_state

    @cached_property
    def first_state(self):
        return get_first_state(self.flow)

    @property
    def first_state_id(self):
        return str(self.first_state["id"])

    @property
    def first_transition(self):
        return self.flow.get_first_transition()

    @property
    def current_status_display(self):
        try:
            return TicketStatus.objects.get(
                service_type=self.service_type, key=self.current_status
            ).name
        except TicketStatus.DoesNotExist:
            return "--"

    @property
    def pre_status_display(self):
        try:
            return _(
                TicketStatus.objects.get(
                    service_type=self.service_type, key=self.pre_status
                ).name
            )
        except TicketStatus.DoesNotExist:
            return "--"

    @property
    def pipeline_states(self):
        """从pipeline中获取节点状态"""
        return task_service.get_state(str(self.pk))

    @property
    def active_transitions(self):
        """流程经过的连线ID列表：TODO-待优化版本"""

        start_state_id = str(self.start_state["id"])
        end_state_id = str(self.end_state["id"])

        node_status = set()
        goals = set()

        id_mapper = self.get_id_mapper(reverse=True)
        for uid, child in self.pipeline_states["children"].items():
            state_id = id_mapper.get(uid)

            if state_id:
                node_status.add(state_id)
                # start->ends
                if state_id != start_state_id:
                    goals.add(state_id)

        if self.is_over:
            # start->end
            goals = {end_state_id}

        paths = []
        matrix = self.flow.graph_matrix(scopes=node_status)
        for goal in goals:
            paths += dfs_paths(matrix, start_state_id, goal)

        transitions = set()
        transition_hash = self.flow.transitions_hash
        for path in paths:
            for i in range(len(path) - 1):
                trans_id = transition_hash.get("{}_{}".format(path[i], path[i + 1]))
                transitions.add(trans_id)

        return [int(t) for t in transitions]

    @property
    def current_state_ids(self):
        """当前运行环节的节点ID列表"""
        if self.is_over:
            return []
        return list(
            self.node_status.filter(status__in=Status.CAN_OPERATE_STATUS).values_list(
                "state_id", flat=True
            )
        )

    @property
    def current_steps(self):
        """当前运行环节"""

        from itsm.ticket.serializers import SimpleStatusSerializer

        running_status = self.node_status.filter(status__in=Status.CAN_OPERATE_STATUS)
        return SimpleStatusSerializer(running_status, many=True).data

    @property
    def brief_current_steps(self):
        """当前运行环节"""
        if self.current_status in TICKET_END_STATUS:
            return []

        return list(
            self.node_status.filter(
                Q(status__in=Status.CAN_OPERATE_STATUS)
                | Q(status=FAILED, type=TASK_STATE)
            ).values("id", "tag", "name")
        )

    @classmethod
    def ticket_current_steps(cls, ticket_ids):
        all_status = Status.objects.filter(
            Q(ticket_id__in=ticket_ids)
            & (
                Q(status__in=Status.CAN_OPERATE_STATUS)
                | Q(status=FAILED, type=TASK_STATE)
            )
        ).values("ticket_id", "id", "tag", "name")
        ticket_status = {}
        for status in all_status:
            ticket_id = status.pop("ticket_id")
            ticket_status.setdefault(ticket_id, []).append(status)
        return ticket_status

    @property
    def running_status(self):
        """当前运行环节"""
        running_status = " / ".join(
            [
                "{}({})".format(ns.name, ",".join(ns.get_processors()))
                for ns in self.node_status.filter(status__in=Status.CAN_OPERATE_STATUS)
            ]
        )
        return (
            running_status
            if running_status
            else TICKET_STATUS_DICT[self.current_status]
        )

    @property
    def real_supervisors(self):
        """获取督办人"""

        # 特殊逻辑：督办类型为EMPTY，则提单人为督办人
        if self.supervise_type == "EMPTY":
            return [self.creator]

        supervisors = UserRole.get_users_by_type(
            self.bk_biz_id, self.supervise_type, self.supervisor, self
        )

        # 默认提单人可以督办
        supervisors.append(self.creator)

        return supervisors

    @property
    def real_assignors(self):
        """获取派单人列表"""

        assignors = set()

        for p in chain(
            s.get_assignors() for s in Status.objects.get_running_status(self.id)
        ):
            assignors.update(p)

        return assignors

    @property
    def real_current_processors(self):
        """获取当前处理人列表"""

        if self.current_status in TICKET_END_STATUS:
            return []

        processors = set()

        running_status = Status.objects.get_running_status(self.id)

        for p in chain(s.get_processors() for s in running_status):
            processors.update(p)

        for node_status in running_status:
            tasks = Task.objects.filter(
                ticket_id=self.id, execute_state_id=node_status.state_id
            )
            for task in tasks:
                task_processor = UserRole.get_users_by_type(
                    self.bk_biz_id, task.processors_type, task.processors
                )
                processors.update(task_processor)

        return processors

    @property
    def display_current_processors(self):
        if self.current_status in TICKET_END_STATUS:
            return []

        processors = set()

        running_status = Status.objects.get_running_status(self.id)
        for status in running_status:
            if status.action_type == SYSTEM_OPERATE:
                continue
            processors.update(self.get_display_processors(status))

        for node_status in running_status:

            is_execute = TaskConfig.objects.filter(
                workflow_id=self.flow_id,
                workflow_type=VERSION,
                execute_task_state=node_status.state_id,
            ).exists()

            if is_execute:
                tasks = Task.objects.filter(ticket_id=self.id)
                for task in tasks:
                    processors.update(self.get_display_processors(task))
        return processors

    @classmethod
    def get_ticket_current_processors(cls, ticket_ids):
        running_status = Status.objects.filter(
            Q(ticket_id__in=ticket_ids)
            & (
                Q(status__in=Status.CAN_OPERATE_STATUS)
                | Q(status=FAILED, type=TASK_STATE)
            )
        ).only("action_type", "processors_type", "processors", "ticket_id")

        tickets_processors = {}
        for status in running_status:
            if status.action_type == SYSTEM_OPERATE:
                continue
            tickets_processors.setdefault(status.processors_type, []).extend(
                status.processors.strip(",").split(",")
            )

        instantiated_processors = {}
        for processors_type, processors in tickets_processors.items():
            if processors_type == ORGANIZATION:
                departments = list_departments_info()
                processors_info = {
                    str(department["id"]): department["name"]
                    for department in departments
                }
            elif processors_type in ["CMDB", "GENERAL"]:
                processors_info = UserRole.get_role_name(
                    processors_type, list(set(processors))
                )
            else:
                processors_info = get_bk_users(
                    format="dict", users=list(set(processors))
                )
            instantiated_processors[processors_type] = processors_info

        current_processors = {}
        for status in running_status:
            if status.action_type == SYSTEM_OPERATE:
                continue
            for processor in status.processors.strip(",").split(","):
                real_processor = instantiated_processors[status.processors_type].get(
                    processor, processor
                )
                current_processors.setdefault(status.ticket_id, []).append(
                    real_processor
                )
        return current_processors

    def get_display_processors(self, status):
        if status.processors_type == ORGANIZATION:
            return [get_department_info(status.processors.strip(",")).get("name", "")]
        else:
            return UserRole.get_users_by_type(
                self.bk_biz_id, status.processors_type, status.processors, self
            )

    @property
    def history_handlers(self):
        handlers = set(
            TicketEventLog.objects.filter(ticket_id=self.id).values_list(
                "operator", flat=True
            )
        )
        return handlers

    @cached_property
    def is_over(self):
        return self.current_status in TicketStatus.objects.filter(
            service_type=self.service_type, is_over=True
        ).values_list("key", flat=True)

    @cached_property
    def is_running(self):
        # 当前状态非结束和非挂起表示处于running状态
        return (
            self.current_status
            in TicketStatus.objects.filter(
                service_type=self.service_type, is_over=False
            ).values_list("key", flat=True)
            and self.current_status != SUSPEND
        )

    @property
    def is_commented(self):
        if hasattr(self, "comments"):
            return self.comments.stars > 0
        return False

    @property
    def comment_id(self):
        if hasattr(self, "comments"):
            return str(self.comments.id)
        return ""

    @property
    def is_slave(self):
        """是否子单"""
        return TicketToTicket.objects.filter(
            related_type=MASTER_SLAVE, from_ticket_id=self.id
        ).exists()

    @property
    def is_master(self):
        """是否母单"""
        return TicketToTicket.objects.filter(
            related_type=MASTER_SLAVE, to_ticket_id=self.id
        ).exists()

    def related_type(self):
        """关联类型"""
        ticket_to_ticket = TicketToTicket.objects.filter(
            related_type=MASTER_SLAVE
        ).filter(Q(from_ticket_id=self.id) | Q(to_ticket_id=self.id))

        if ticket_to_ticket:
            related_type = (
                "slave"
                if ticket_to_ticket.last().from_ticket_id == self.id
                else "master"
            )
            return related_type

    @property
    def slave_tickets(self):
        """所有子单"""
        from_ticket_ids = TicketToTicket.objects.filter(
            related_type=MASTER_SLAVE, to_ticket_id=self.id
        ).values_list("from_ticket_id", flat=True)
        return Ticket.objects.filter(id__in=from_ticket_ids)

    @property
    def master_slave_tickets(self):
        """母单+子单"""
        # 实际场景中, 母子单比例较少, 首先进行母子单校验, 总体上会大大减少数据库交互次数
        if self.is_master:
            return [self] + list(self.slave_tickets)
        else:
            return [self]

    @property
    def has_relationships(self):
        """是否有关联单"""
        if TicketToTicket.objects.filter(
            Q(related_type=DERIVE)
            & (Q(from_ticket_id=self.id) | Q(to_ticket_id=self.id))
        ).exists():
            return True
        return False

    def get_master_ticket(self):
        """获取母单单据"""
        # 若存在, 获取单据的母单
        slave_to_master = TicketToTicket.objects.filter(
            related_type=MASTER_SLAVE, from_ticket_id=self.id
        ).last()
        if slave_to_master:
            master_ticket = Ticket.objects.get(id=slave_to_master.to_ticket_id)
            return master_ticket

    @classmethod
    def get_batch_master_ticket(cls, ticket_ids):
        slave_to_master = TicketToTicket.objects.filter(
            related_type=MASTER_SLAVE, from_ticket_id__in=ticket_ids
        )
        ticket_map = {
            slave.from_ticket_id: slave.to_ticket_id for slave in slave_to_master
        }
        master_tickets = Ticket.objects.filter(id__in=ticket_map.values()).values(
            "id", "current_status", "meta", "service_type"
        )
        master_map = {ticket["id"]: ticket for ticket in master_tickets}
        return {
            from_ticket: master_map[to_ticket]
            for from_ticket, to_ticket in ticket_map.items()
        }

    @property
    def ticket_fields(self):
        """
        单据字段列表，提供给openapi使用
        """
        from itsm.openapi.ticket.serializers import TicketFieldSerializer

        return TicketFieldSerializer(
            self.fields.filter(is_deleted=False).order_by("id"), many=True
        ).data

    @property
    def ticket_logs(self):
        """
        单据日志，提供给openapi使用
        """

        from itsm.openapi.ticket.serializers import SimpleLogsSerializer

        return SimpleLogsSerializer(self.logs.all(), many=True).data

    @property
    def ticket_complex_logs(self):
        """
        复杂单据日志
        """

        from itsm.openapi.ticket.serializers import ComplexLogsSerializer

        return ComplexLogsSerializer(self.logs.all(), many=True).data

    @property
    def task_operators(self):
        tasks = Task.objects.filter(ticket_id=self.id)

        operators = []
        for task in tasks:
            operators.extend(task.processor_user_list)

        return list(set(operators))

    @classmethod
    def get_my_approval_ticket(cls, username):
        running_node = Status.objects.filter(type=APPROVAL_STATE, status=RUNNING)
        closed_status = set(
            TicketStatus.objects.filter(is_over=True).values_list("key", flat=True)
        )
        my_approval_ticket = set(
            [
                node.ticket_id
                for node in running_node
                if username in node.get_processor_in_sign_state().split(",")
            ]
        )
        return cls.objects.filter(id__in=my_approval_ticket).exclude(
            current_status__in=closed_status
        )

    def get_output_fields(
        self, state_id=None, return_format="list", need_display=False
    ):
        """
        对外输出变量字段列表
        """
        from itsm.ticket.serializers import TicketGlobalVariableSerializer

        output_fields = []
        # step 获取到当前节点的自定义数据和基础模型的所有字段

        fields = self.fields.filter(is_deleted=False)
        variables = TicketGlobalVariable.objects.filter(ticket_id=self.id)
        if state_id is not None:
            fields = fields.filter(Q(state_id=state_id) | Q(source=BASE_MODEL))
            variables = variables.filter(state_id=state_id)

        for field in fields:
            if field.value is None:
                continue

            value = format_exp_value(field.type, field.value)
            output_fields.append(
                {"key": field.key, "value": value, "source": field.source}
            )
            if need_display:
                display_value = (
                    field.display_value if hasattr(field, "display_value") else value
                )
                output_fields.append(
                    {
                        "key": "{}__display".format(field.key),
                        "value": display_value,
                        "source": field.source,
                    }
                )

        output_fields.extend(TicketGlobalVariableSerializer(variables, many=True).data)
        # 添加单据全局属性
        global_context = self.get_global_context()
        output_fields.extend(global_context)

        if return_format == "dict":
            return {item["key"]: item["value"] for item in output_fields}

        return output_fields

    def get_ticket_global_output(self, display_type="dict"):
        outputs = TicketGlobalVariable.get_ticket_output(
            self.id, display_type=display_type
        )
        fields = self.fields.filter(is_deleted=False)
        exist_keys = set()
        for field in fields:
            if field.key in exist_keys:
                continue
            exist_keys.add(field.key)
            if field.value is None:
                continue
            value = format_exp_value(field.type, field.value)
            if display_type == "list":
                outputs.append({"key": field.key, "value": value, "name": field.name})
            else:
                outputs[field.key] = value
        return outputs

    def get_ticket_result(self):
        workflow_global_variable = GlobalVariable.objects.filter(
            flow_id=self.flow.workflow_id, is_deleted=0
        ).only("key", "meta")
        result_list = []
        for variable in workflow_global_variable:
            if variable.meta.get("code", "") == NODE_APPROVE_RESULT:
                result = TicketGlobalVariable.objects.filter(
                    key=variable.key, ticket_id=self.id
                ).first()
                if result:
                    result_list.append(result.value == "true")
        return all(result_list) if self.current_status == PROCESS_FINISHED else False

    def can_comment(self, username):
        return username in [self.creator, self.meta.get("ticket_agent")] and all(
            [self.current_status == FINISHED, not self.is_commented]
        )

    def can_supervise(self, username):
        # return all(
        #     [
        #         self.is_supervise_needed,
        #         not self.is_over,
        #         username in self.real_supervisors,
        #     ]
        # )
        # 调整为提单人都可以督办
        return username == self.creator and not self.is_over

    def iam_ticket_manage_auth(self, username):
        # 本地开发环境，不校验单据管理权限
        if settings.ENVIRONMENT == "dev":
            return True

        iam_client = IamRequest(username=username)
        resource_info = {
            "resource_id": str(self.service_id),
            "resource_name": self.service_name,
            "resource_type": "service",
        }

        apply_actions = ["ticket_management"]
        auth_actions = iam_client.resource_multi_actions_allowed(
            apply_actions, [resource_info], project_key=self.project_key
        )
        if auth_actions.get("ticket_management"):
            return True

        return False

    def can_operate(self, username):
        """
        能否操作单据：任一节点的处理人
        """
        if self.is_over or self.is_slave:
            return False

        if self.iam_ticket_manage_auth(username):
            return True

        processors = self.current_processors + self.current_task_processors
        all_processors = set(
            [processor for processor in processors.split(",") if processor]
        )

        if not all_processors:
            return False

        if username in all_processors:
            # 用户名存在处理人列表中
            return True

        user_roles = UserRole.get_user_roles(username)

        if all_processors.intersection(user_roles["general"]):
            # 普通角色存在列表中
            return True

        for role_id in all_processors.intersection(user_roles["cmdb"].keys()):
            if self.bk_biz_id in user_roles["cmdb"][role_id]:
                # 对应的业务id和cmdb的角色存在列表中
                return True

        organization = set(map(lambda x: "O_{}".format(x), user_roles["organization"]))
        if all_processors.intersection(organization):
            # 组织架构存在列表中
            return True

        return False

    def can_invite_followers(self, username):
        """能够邀请别人关注：提单人和处理人"""

        return not self.is_over and (
            username == self.creator or self.has_perm(username)
        )

    def has_perm(self, username):
        """
        是否具有处理权限
        """
        return not self.is_slave and any(
            [
                status.can_operate(username)
                for status in self.node_status.filter(
                    status__in=Status.CAN_OPERATE_STATUS
                )
            ]
        )

    def can_derive(self, username):
        """能否转建单"""

        return any([status.can_derive(username) for status in self.node_status.all()])

    def can_view(self, username):
        """能否查看单据"""
        if (
            dotted_name(username) in self.updated_by
            or username in self.task_operators
            or self.can_operate(username)
            or AttentionUsers.objects.filter(
                ticket_id=self.id, follower=username
            ).exists()
        ):
            # 与单据操作相关的人，都是可以查看的
            return True

        return False

    def current_status_can_view(self, username):
        """当前运行环节能否查看"""
        status_list = Status.objects.filter(
            Q(status__in=Status.CAN_OPERATE_STATUS) & Q(ticket_id=self.id)
        ).all()
        if not status_list:
            return False
        return any([status.can_view(username) for status in status_list])

    def can_withdraw(self, username, ignore_user=False):
        """能否撤单"""

        if not self.flow.is_revocable or self.is_over:
            # 不可撤销或者已经结束的单，直接返回
            return False

        if not ignore_user and username != self.creator:
            return False

        if self.flow.revoke_config["type"] == REVOKE_TYPE.FIRST:

            if self.node_status.filter(status__in=Status.STOPPED_STATUS).count() == 1:
                # 自动执行节点
                if self.node_status.filter(
                    status=RUNNING, action_type=SYSTEM_OPERATE
                ).exists():
                    return False

                return True

            # 打回到提单环节
            try:
                first_status = self.node_status.get(state_id=int(self.first_state_id))
                if first_status.status == RUNNING:
                    return True
            except Status.DoesNotExist:
                logger.info(
                    "can_withdraw exception: %s not exist" % self.first_state_id
                )
                return False

            return False
        elif self.flow.revoke_config["type"] == REVOKE_TYPE.ASSIGN:
            state_id = self.flow.revoke_config["state"]
            is_executed = self.node_status.filter(state_id=state_id).exists()
            return not is_executed
        return True

    def can_close(self, username):
        """
        是否可以进行关闭操作
        """
        if (
            self.is_over
            or not StatusTransit.objects.filter(
                service_type=self.service_type,
                from_status__key=self.current_status,
                to_status__is_over=True,
            ).exists()
        ):
            # 当前状态无法到达关闭的时候，不可以进行关闭操作按钮
            return False
        if username == self.creator:
            # 创建人可以直接关闭
            return True

        if self.iam_ticket_manage_auth(username):
            return True

        for _status in self.node_status.filter(
            Q(status__in=Status.CAN_OPERATE_STATUS) | Q(status=FAILED, type=TASK_STATE)
        ):
            if _status.can_operate(username):
                # 当前节点的操作人也可以进行关闭操作
                return True
        return False

    def update_current_status(self, status):
        """更新current_status及字段"""
        self.pre_status = self.current_status
        self.current_status = status
        self.save()

        # 公共字段区域, 单据状态的下拉框数据 需要随着单据状态更新而同步更新
        ticket_status = TicketStatus.objects.get(
            key=status, service_type=self.service_type
        )
        choice = TicketStatusOptionSerializer(ticket_status.to_status, many=True).data
        self.fields.filter(key=FIELD_STATUS).update(
            _value=self.current_status, choice=choice
        )

    def update_priority(self, urgency=None, impact=None):
        """
        更新优先级字段
        优先级由紧急程度、影响程度匹配出来
        """
        try:
            priority_field = self.fields.get(key=FIELD_PRIORITY, source=BASE_MODEL)
        except TicketField.DoesNotExist as error:
            logger.warning("当前单据不包含优先级的字段， error is {}".format(error))
            return {}

        if not impact:
            try:
                impact = self.fields.get(key=FIELD_PY_IMPACT, source=BASE_MODEL).value

            except TicketField.DoesNotExist as error:
                logger.warning("当前单据不包含影响范围的字段， error is {}".format(error))
                return {}

        if not urgency:
            try:
                urgency = self.fields.get(key=FIELD_PX_URGENCY, source=BASE_MODEL).value
            except TicketField.DoesNotExist as error:
                logger.warning("当前单据不包含紧急度的字段， error is {}".format(error))
                return {}

        if not (urgency and impact):
            # 优先级的配置必须相关的两个字段都有值存在, 否则采用默认优先级
            if self.service_instance:
                # 1.在关联表中拿到sla_id
                try:
                    sla_id = ServiceSla.objects.get(
                        service_id=self.service_instance.id
                    ).sla_id
                except ServiceSla.DoesNotExist as error:
                    logger.warning(
                        "Failed to get sla_id from ServiceSla， error is {}".format(
                            error
                        )
                    )
                    return {}
                    # 2.拿到sla实例
                try:
                    sla_instance = Sla.objects.get(id=sla_id)
                except Sla.DoesNotExist as error:
                    logger.warning(
                        "Failed to get sla_instance from Sla， error is {}".format(error)
                    )
                    return {}
                default_priority = sla_instance.get_default_policy()
                priorities = SysDict.list_data(
                    PRIORITY, fields=["key", "name", "order"]
                )
                self.update_ticket_priority(priorities, default_priority)

            return {}

        try:
            new_priority = PriorityMatrix.objects.get_priority(
                self.service_type, urgency, impact
            )
        except PriorityMatrix.DoesNotExist as error:
            logger.warning("当前服务的优先级矩阵设置不正常，错误信息 {}".format(error))
            return {}

        old_priority = priority_field.value

        if old_priority != new_priority:
            # 首次更新优先级, 需初始化下拉框选项
            if old_priority is None:
                choice = SysDict.list_data(PRIORITY, fields=["key", "name", "order"])
                self.fields.filter(key=FIELD_PRIORITY).update(
                    choice=choice, _value=new_priority
                )
            else:
                self.fields.filter(key=FIELD_PRIORITY).update(_value=new_priority)
            priority_field.refresh_from_db()

            # 根据下拉框的choice中获取当前优先级的详细信息
            self.update_ticket_priority(priority_field.choice, new_priority)

            return {"instance": priority_field, "old_value": old_priority}
        return {}

    def update_ticket_priority(self, priorities, new_priority):
        """更新单据的优先级以及优先级排序权重"""
        priority_info = {}
        for priority in priorities:
            if priority["key"] == new_priority:
                priority_info = priority
                break

        # 更新单据的优先级属性
        self.priority_key = priority_info.get("key")
        if not self.meta:
            self.meta = dict(priority=priority_info)
        self.save()

    def _build_actions(self, operate_key, can_operate=True):
        return {
            "key": operate_key,
            "name": ACTION_DICT.get(operate_key),
            "can_operate": can_operate,
        }

    @property
    def operations(self):

        # 审批/派单/认领
        operations = []

        if self.is_over:
            return []

        # 撤销
        if self.can_withdraw("api", ignore_user=True):
            operations.append(self._build_actions(WITHDRAW_OPERATE))

        # 挂起->恢复
        if self.current_status == "SUSPENDED":
            operations.append(self._build_actions(UNSUSPEND_OPERATE))
        # 处理中->挂起
        elif self.current_status == "RUNNING":
            operations.append(self._build_actions(SUSPEND_OPERATE))

        return operations

    def status(self, state_id):
        """获取流程节点状态"""
        try:
            return self.node_status.filter(state_id=state_id).first()
        except ValueError:
            logger.error("获取status异常，state_id非法：%s" % state_id)
            return None

    @property
    def status_instance(self):
        return TicketStatus.objects.get(
            key=self.current_status, service_type=self.service_type
        )

    def is_current_step(self, state_id):
        return self.node_status.filter(
            state_id=state_id, status__in=Status.RUNNING_STATUS
        ).exists()

    def state(self, state_id):
        """获取流程节点"""
        return self.flow.get_state(state_id)

    def transition(self, transition_id):
        """获取流程连线"""
        return self.flow.get_transition(transition_id)

    def field(self, field_id):
        """获取流程字段"""
        return self.flow.get_field(field_id)

    def get_field_value(self, key, default=None):
        """获取字段值"""
        try:
            return self.fields.filter(key=key).first().value
        except BaseException:
            logger.warning("get_field_value({}) = default({})".format(key, default))
            return default

    def get_state_fields(self, state_id, need_serialize=True):
        """获取单据的节点表单字段"""

        from itsm.ticket.serializers import FieldSerializer

        fields = self.fields.filter(state_id=state_id)

        if need_serialize:
            return FieldSerializer(fields, many=True).data

        return fields

    def activity_for_state(self, state_id):
        """
        将state_id转换为pipeline的节点id
        :param state_id: workflow的节点id
        """
        return self.pipeline_data["states_map"][str(state_id)]

    def is_token_accessible(self, username, token):
        """校验token有效性"""

        return self.is_email_invite_token(username, token) or self.is_follow_token(
            username, token
        )

    def is_email_invite_token(self, username, token):
        # 邮件邀请评价

        if not token:
            return False
        # 没有评价
        if not hasattr(self, "comments"):
            return False

        return self.comments.invite.filter(receiver=username, code=token).exists()

    def is_follow_token(self, username, token):
        """验证关注人的token有效性"""
        notify_log = self.follower_notify_logs.filter(ticket_token=token)
        if notify_log:
            followers = UserRole.get_users_by_type(
                self.bk_biz_id,
                notify_log[0].followers_type,
                notify_log[0].followers,
                self,
            )
            return username in followers
        return False

    def get_global_context(self, prefix="", return_format="list"):
        """全局单据属性
        attrs：属性key列表，用于过滤，默认返回所有属性
        params_ticket.sn -> ticket.sn
        """
        start_from = len("ticket_")

        if return_format == "list":
            cxt = [
                {
                    "key": var["key"],
                    "value": self.datetime_clean(
                        getattr(self, var["key"][start_from:], "")
                    ),
                }
                for var in TICKET_GLOBAL_VARIABLES
            ]
        else:
            cxt = {
                "{0}{1}".format(prefix, var["key"]): self.datetime_clean(
                    getattr(self, var["key"][start_from:], "")
                )
                for var in TICKET_GLOBAL_VARIABLES
            }

        return cxt

    def datetime_clean(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value

    @property
    def sops_task_summary(self):
        """
        标准运维任务总结信息
        """
        rel_part = []
        for sops_task in Task.objects.filter(
            ticket_id=self.id, component_type=SOPS_TASK
        ):
            task_info = {}
            for item in sops_task.all_fields.filter(key__in=REL_SUMMARY_FIELDS):
                if item.key in TIME_DURATION_SUMMARY_FIELDS and item.value:
                    try:
                        task_info[item.key] = int(item.value) // 60
                    except BaseException:
                        task_info[item.key] = 0
                else:
                    task_info[item.key] = item.value

            rel_part.append(copy.deepcopy(task_info))
        return rel_part

    @property
    def sops_relate_id(self):
        """
        标准运维任务管理啊REL单据信息
        """
        try:
            return self.fields.filter(key="REL_NO").first().value
        except BaseException:
            return ""

    @property
    def all_task_processors(self):
        processors = []
        for task in Task.objects.filter(ticket_id=self.id):
            processors.extend(task.processor_user_list)
        return processors

    @property
    def followers(self):
        follower = AttentionUsers.objects.filter(ticket_id=self.id).values_list(
            "follower", flat=True
        )
        return list(follower)

    @property
    def ticket_current_processors(self):
        processors_list = self.get_current_processors()

        try:
            processors = (
                transform_username(processors_list) if processors_list else "--"
            )
            logger.info(
                "[ticket_current_processors]Success：用户名转换成中英文格式成功,ticket_id:{}, "
                "processors_list:{}, "
                "transform_processors:{}".format(self.id, processors_list, processors)
            )
        except Exception as e:
            processors = ",".join(processors_list)
            logger.info(
                "[ticket_current_processors]Failed：用户名转换成中英文格式失败,ticket_id:{}, processors_list:{}, error:{}".format(
                    self.id, processors_list, str(e)
                )
            )
        return processors.strip(",")

    def add_follower(self, username):
        exist = AttentionUsers.objects.filter(
            ticket_id=self.id, follower=username
        ).exists()
        if not exist:
            AttentionUsers.objects.create(ticket_id=self.id, follower=username)

    def delete_follower(self, username):
        AttentionUsers.objects.filter(ticket_id=self.id, follower=username).delete()

    def base_info(self):
        fields = []
        workflow_field = self.first_state["fields"]
        node_fields = self.fields.filter(
            Q(state_id=self.first_state_id) | Q(workflow_field_id__in=workflow_field)
        )
        for node_field in node_fields:
            fields.append(
                {
                    "type": node_field.type,
                    "key": node_field.key,
                    "value": node_field.value,
                    "choice": node_field.choice,
                }
            )
        data = {
            "catalog_id": self.catalog_id,
            "service_id": self.service_id,
            "service_type": self.service_type,
            "creator": self.creator,
            "attention": AttentionUsers.objects.filter(
                ticket_id=self.id, follower=self.creator
            ).exists(),
            "fields": fields,
        }
        return data

    def get_notify_context(self, attrs=None):
        """
        获取通知上下文变量：全局单据属性 + 字段属性
            attrs：属性key列表，用于过滤，默认返回所有属性
        """
        ticket_attrs = NOTIFY_GLOBAL_VARIABLES
        if attrs:
            ticket_attrs = [x for x in ticket_attrs if x["key"] in attrs]

        context = {}
        for attr in ticket_attrs:
            plain_value = getattr(self, attr["key"])
            attr_value = _(plain_value) if isinstance(plain_value, str) else plain_value
            context.update(**{attr["key"]: attr_value})

        # 添加时间
        context.update(today_date=datetime.today())
        # creator用户名翻译成中英文格式
        if settings.CONTENT_CREATOR_WITH_TRANSLATION:
            context.update(creator=transform_single_username(self.creator))

        return context

    # ====================================== 辅助操作接口 ==========================

    def get_id_mapper(self, reverse=False):
        """从pipeline中获取节点状态"""

        _states_map = self.pipeline_data.get("states_map", {})

        # 暂时拿不到原始states_map
        if not _states_map:
            return {}

        if reverse:
            return {v: k for k, v in _states_map.items()}

        return _states_map

    def get_further_nodes(self, states, state_id):
        """获取更远处的节点"""

        def _min_path_length(_paths):
            """最短路径"""

            if not _paths:
                return float("inf")

            _paths = [len(x) for x in _paths]

            return min(_paths)

        # 获取有效拓扑节点：流程走过的节点
        node_status = set()
        id_mapper = self.get_id_mapper(reverse=True)
        for uid, child in self.pipeline_states["children"].items():
            sid = id_mapper.get(uid)
            if sid:
                node_status.add(sid)

        # 获取有效拓扑图描述矩阵
        matrix = self.flow.graph_matrix(scopes=node_status)
        # print matrix, state_id, state_id

        # 搜索起点到终点的路径
        further_nodes = set()
        state_id = str(state_id)
        start_state_id = str(self.start_state["id"])
        state_distance = _min_path_length(dfs_paths(matrix, start_state_id, state_id))
        # print '{}->{}: {}'.format(start_state_id, state_id, state_distance)
        for target_id in states:
            if target_id == start_state_id or target_id in further_nodes:
                continue

            target_distance = _min_path_length(
                dfs_paths(matrix, start_state_id, target_id)
            )
            # print '{}->{}: {}'.format(start_state_id, target_id, target_distance)
            if target_distance > state_distance:
                further_nodes.add(target_id)

        return further_nodes

    def get_circle_path(self, state_id):
        """获取环形路径"""

        # 获取有效拓扑节点：流程走过的节点
        node_status = set()
        id_mapper = self.get_id_mapper(reverse=True)
        for uid, child in self.pipeline_states["children"].items():
            sid = id_mapper.get(uid)
            if sid:
                node_status.add(sid)

        # 获取有效拓扑图描述矩阵
        matrix = self.flow.graph_matrix(scopes=node_status)

        # 搜索起点到终点的路径
        state_id = str(state_id)
        paths = dfs_paths(matrix, state_id, state_id, skip_circle=False)

        return paths

    def notify(
        self,
        state_id,
        receivers,
        message="",
        action=TRANSITION_OPERATE,
        retry=True,
        **kwargs
    ):
        """发送单据和任务通知"""
        from itsm.ticket.tasks import notify_task

        logger.info(
            "[ticket->notify] is executed, state_id={}, receivers={}, message={}, action={}".format(
                state_id, receivers, message, action
            )
        )
        if (
            state_id
            and self.node_status.get(state_id=state_id).action_type == SYSTEM_OPERATE
        ):
            return

        if state_id and action in [
            TRANSITION_OPERATE,
            WAITING_FOR_OPERATE,
            WAITING_FOR_CONFIRM,
        ]:
            self.generate_ticket_url(state_id, receivers)

        try:
            # 本次通知
            notify_task.apply_async(
                args=[self, receivers, message, action], kwargs=kwargs
            )
            self.notify_followers(action)

            # 重复通知
            if self.flow.notify_rule == "RETRY" and retry:
                # dispatch_retry_notify_event(self, state_id, receivers)
                pass  # 去除重复通知相关的功能

        except Exception as e:
            logger.error("notify exception: %s" % e)

    def notify_followers(self, action):
        if action in [FOLLOW_OPERATE, INVITE_OPERATE]:
            return
        from itsm.ticket.tasks import notify_task

        try:
            receivers = list(
                AttentionUsers.objects.filter(ticket_id=self.id).values_list(
                    "follower", flat=True
                )
            )
            notify_task.apply_async(
                args=[self, ",".join(receivers), "", NOTIFY_FOLLOWER_OPERATE]
            )
        except Exception as err:
            logger.exception("notify followers exception: {}".format(err))

    def set_finished(
        self, operator="", close_status=FINISHED, desc="", source=SYS, last_flow=None
    ):
        """
        设置结束状态
        """
        self.update_current_status(close_status)
        for ticket in self.master_slave_tickets:
            # TODO: 临时处理, 后面会放在母子单解绑逻辑中
            ticket.current_status = close_status
            ticket.node_status.filter(status__in=Status.RUNNING_STATUS).update(
                status=FINISHED
            )
            ticket.current_task_processors = ""
            ticket.current_processors = ""
            ticket.current_processors_type = ""
            ticket.end_at = datetime.now()
            ticket.pipeline_data.update({"last_flow": last_flow})
            ticket.save()

            # 单据结束创建评价信息
            TicketComment.objects.get_or_create(
                ticket_id=ticket.id, creator=ticket.creator
            )

            # 创建结束流转日志
            message = "流程结束."
            if source == WEB:
                message = (
                    "{operator} 关闭了单据：{detail_message}."
                    if desc
                    else "{operator} 关闭了单据."
                )

            TicketEventLog.objects.create_end_log(
                ticket, message, operator, detail_message=desc
            )

        self.callback_request()

    def get_last_approver(self):
        """
        获取最后一个审批节点的处理人
        """
        status = (
            Status.objects.filter(
                ticket_id=self.id, type__in=[APPROVAL_STATE, SIGN_STATE]
            )
            .order_by("-update_at")
            .first()
        )
        if status is None:
            return ""
        sign_tasks = SignTask.objects.filter(status_id=status.id)

        processors = []
        for sign_task in sign_tasks:
            processors.append(sign_task.processor)
        return ",".join(processors)

    def callback_request(self):
        callback_url = self.meta.get("callback_url", "")
        headers = self.meta.get("headers", {})
        if callback_url:
            message = AESVerification.gen_signature(
                settings.APP_CODE + "_" + settings.SECRET_KEY
            )
            request_data = {
                "title": self.title,
                "current_status": self.current_status,
                "sn": self.sn,
                "ticket_url": self.ticket_url,
                "update_at": str(self.update_at),
                "updated_by": self.updated_by,
                "approve_result": self.get_ticket_result(),
                "token": str(message, encoding="utf-8"),
                "last_approver": self.get_last_approver(),
            }
            try:
                logger.info(
                    "[TICKET] callback_request params is {}".format(request_data)
                )
                session = requests.session()
                resp = session.post(
                    url=callback_url, json=request_data, verify=False, headers=headers
                )
                if resp.status_code not in {200, 201}:
                    raise Exception(
                        "status_code is {}, msg is {}".format(
                            resp.status_code, resp.content
                        )
                    )
                result = resp.json()
                if result.get("code") != 0:
                    raise Exception(
                        "error is {}, msg is {}".format(
                            result["code"], result["message"]
                        )
                    )
            except Exception as err:
                Cache().hset("callback_error_ticket", self.sn, int(time.time()))
                logger.exception(
                    "[TICKET] callback_error_ticket, callback_url is {},"
                    "message is {}, ticket_id is {}".format(callback_url, err, self.id)
                )

    def prepare_all_fields(self):
        """单据上下文准备：创建字段"""

        fields = []

        all_fields = self.flow.table.get("fields", []) + list(self.flow.fields.values())
        status_choice = TicketStatus.objects.get_status_choice(self.service_type)
        for field in all_fields:
            ticket_field = copy.deepcopy(field)
            ticket_field.pop("workflow_id", None)
            ticket_field.pop("flow_type", None)
            ticket_field_key = ticket_field["key"]

            # 填充默认值
            default = ticket_field.pop("default", "")
            if default:
                ticket_field.update(_value=default)

            # 特殊字段：工单状态
            if ticket_field_key == FIELD_STATUS:
                ticket_field.update(choice=status_choice)

            ticket_field.update(
                workflow_field_id=ticket_field.pop("id", None), ticket=self
            )
            ticket_field.pop("api_info", None)
            ticket_field.pop("project_key", None)
            fields.append(TicketField(**ticket_field))

        TicketField.objects.bulk_create(fields)

    def fill_state_fields(self, fields):
        """更新单据字段"""

        filter_fields = []
        for field in fields:
            # 更新优先级由update_priority统一处理
            if field["key"] == FIELD_PRIORITY:
                continue
            filter_fields.append(field)

        fields_map = {filed["key"]: filed for filed in filter_fields}
        filter_field_query_set = self.fields.filter(key__in=fields_map.keys())
        for ticket_field in filter_field_query_set:
            ticket_field.value = fields_map[ticket_field.key]["value"]
            ticket_field.choice = fields_map[ticket_field.key].get("choice", [])
            ticket_field.update_at = datetime.now()

        bulk_update(
            filter_field_query_set, update_fields=["_value", "choice", "update_at"]
        )

    # def fill_state_fields(self, fields):
    #     """更新单据字段"""
    #
    #     for field in fields:
    #         # 更新优先级由update_priority统一处理
    #         if field["key"] == FIELD_PRIORITY:
    #             continue
    #
    #         filter_fields = self.fields.filter(key=field["key"])
    #         # 多个单据字段：插入到节点的基础模型字段 + 唯一基础模型字段
    #         for ticket_field in filter_fields:
    #             ticket_field.value = field["value"]
    #             ticket_field.choice = field.get("choice", [])
    #
    #         bulk_update(filter_fields, update_fields=["_value", "choice"])

    def update_ticket_fields(self, fields):
        for field in fields:
            # 更新优先级由update_priority统一处理
            if field["key"] == FIELD_PRIORITY:
                continue

            # 多个单据字段：插入到节点的基础模型字段 + 唯一基础模型字段
            for ticket_field in self.fields.filter(key=field["key"]):
                ticket_field.value = field["_value"]
                ticket_field.save()

    def update_ticket_before_enter(self, status):
        """更新单据属性"""
        # 根据节点的配置, 更新单据状态
        ticket_status = status.get_ticket_status_setting(self.service_type)

        # 若自动设置单据状态, 单据状态的下拉框选项也随之更新
        if ticket_status:
            choice = TicketStatusOptionSerializer(
                TicketStatus.objects.get(
                    key=ticket_status.key, service_type=self.service_type
                ).to_status,
                many=True,
            ).data

            # 更新单据属性
            self.current_status = ticket_status.key
            # 更新单据公共字段
            self.fields.filter(key=FIELD_STATUS).update(
                _value=ticket_status.key, choice=choice
            )
            # 如果是结束状态，直接结束
            if ticket_status.is_over:
                self.close(
                    close_status=ticket_status.key,
                    desc=_("节点设置的默认单据状态为结束状态"),
                    operator="system",
                )
            self.save()

    def update_state_before_enter(self, state_id, **kwargs):
        """更新单据当前各节点的属性"""

        def _formatted(pros_type, pros, ticket):
            if pros_type == PERSON:
                return dotted_name(pros), PERSON

            if pros_type == VARIABLE:
                # 引用变量的处理人逻辑
                var_pros = ""
                for f_key in pros.split(","):
                    f_value = self.get_field_value(f_key)
                    # 跳过空值字段
                    if not f_value:
                        continue

                    for user in f_value.split(","):
                        # 历史数据中多选人员选择字段存入了中文名: miya(miya)，暂时兼容
                        username = user[0 : user.find("(")] if "(" in user else user
                        var_pros = "{},{}".format(var_pros, username)

                    # 取到第一个处理人则停止解析
                    break
                else:
                    # 所有引用的处理人字段均为空
                    return "", PERSON

                return dotted_name(var_pros), PERSON

            if pros_type == STARTER:
                return dotted_name(ticket.creator), PERSON

            if pros_type == STARTER_LEADER:
                # 获取到当前提单人的leader, 如果支持组织架构，这里直接返回空
                leaders = get_user_leader(ticket.creator)
                leaders = dotted_name(",".join(leaders)) if leaders else ""
                return leaders, PERSON

            if pros_type == ASSIGN_LEADER:
                obj = Status.objects.get(ticket_id=ticket.id, state_id=int(pros))
                leaders = get_user_leader(obj.processed_user)
                leaders = dotted_name(",".join(leaders)) if leaders else ""
                return leaders, PERSON

            return pros, pros_type

        state = bunchify(self.state(state_id))

        # 根据场景更新节点状态及单据状态
        distribute_type = state.distribute_type

        # 被分派的人
        assignors_type, assignor_to = "", ""
        f_assignors, f_assignors_type = _formatted(
            state.assignors_type, state.assignors, self
        )
        f_processors, f_processors_type = _formatted(
            state.processors_type, state.processors, self
        )

        # 分派后处理/分派后认领
        if distribute_type in ["DISTRIBUTE_THEN_PROCESS", "DISTRIBUTE_THEN_CLAIM"]:
            processors_type = f_assignors_type
            processors = f_assignors
            assignors_type = f_processors_type
            assignor_to = f_processors
            status = DISTRIBUTING
            action_type = DISTRIBUTE_OPERATE
        # 认领后处理
        elif distribute_type == "CLAIM_THEN_PROCESS":
            real_processors = UserRole.get_users_by_type(
                self.bk_biz_id, f_processors_type, f_processors, self
            )
            if len(real_processors) == 1:
                processors = dotted_name(",".join(real_processors))
                processors_type = PERSON
                status = RUNNING
                action_type = TRANSITION_OPERATE
            else:
                processors = f_processors
                processors_type = f_processors_type
                status = RECEIVING
                action_type = CLAIM_OPERATE
        # 待处理：PROCESS（自动+手动）
        else:
            predefined_processors = self.meta.get("state_processors", {}).get(state_id)
            if predefined_processors:
                processors = dotted_name(predefined_processors)
                processors_type = PERSON
            else:
                processors = f_processors
                processors_type = f_processors_type
            status = RUNNING
            action_type = (
                SYSTEM_OPERATE
                if state.type
                in [
                    TASK_STATE,
                    TASK_SOPS_STATE,
                    TASK_DEVOPS_STATE,
                    WEBHOOK_STATE,
                    BK_PLUGIN_STATE,
                ]
                else TRANSITION_OPERATE
            )

        defaults = {
            "bk_biz_id": self.bk_biz_id or DEFAULT_BK_BIZ_ID,
            "status": status,
            "tag": getattr(state, "tag", DEFAULT_STRING),
            "name": state.name,
            "type": state.type,
            "is_sequential": getattr(state, "is_sequential", False),
            "action_type": action_type,
            "api_instance_id": kwargs.get("api_instance_id", 0),
            "distribute_type": distribute_type,
            "processors": processors,
            "processors_type": processors_type,
            "can_deliver": state.can_deliver,
            "delivers": state.delivers,
            "delivers_type": state.delivers_type,
            "assignors": assignor_to,
            "assignors_type": assignors_type,
            "can_terminate": state.is_terminable,
            "state_id": state_id,
            "ticket_id": self.id,
            "meta": state.extras,
            "by_flow": kwargs.get("by_flow") or "",
            "query_params": {},
            "ignore_params": {},
        }

        # 若status存在，则说明是回路，线条往回走
        # # 清理该距离远的节点：距开始节点距离 > 当前节点距开始节点的距离
        if Status.objects.filter(state_id=state_id, ticket_id=self.id).exists():
            # state_id, ticket_id对应唯一未删除的status，若存在多个，则存在BUG
            status = Status.objects.get(state_id=state_id, ticket_id=self.id)
            defaults.update(
                processors_type=status.processors_type,
                processors=status.processors,
                distribute_type="PROCESS",
                action_type="TRANSITION",
                status=RUNNING,
                query_params=status.query_params,
                ignore_params=status.ignore_params,
            )

            # 针对引用变量类型的，当被打回时, 重新刷新处理人，防止引用变量被修改审批人仍为旧的问题
            if state.processors_type == "VARIABLE":
                defaults["processors_type"] = processors_type
                defaults["processors"] = processors

            path = list(self.get_circle_path(state_id))

            circle_nodes = set()
            for p in path:
                circle_nodes.update(set(p))

            # 获取更远的节点
            further_nodes = self.get_further_nodes(circle_nodes, state_id)
            further_nodes.update([state_id])
            self.node_status.filter(state_id__in=further_nodes).delete()

        status = Status.objects.create(**defaults)
        return status

    def get_printable_states(self, username):
        """获取可以打印的节点："""
        from itsm.ticket.serializers import StatusSerializer

        ticket_logs = (
            self.logs.filter(is_valid=True)
            .exclude(from_state_id__in=[self.start_state["id"], self.end_state["id"]])
            .order_by("operate_at")
        )

        state_list = []
        for log in ticket_logs:
            status = Status._objects.filter(id=log.status).last()
            ticket_status = StatusSerializer(
                status,
                context={
                    "username": username,
                    "show_all_fields": False,
                },
            )

            state_info = ticket_status.data
            status_fields = {}
            if status is not None:
                status_fields = dict(
                    [(str(field["id"]), field) for field in status.fields]
                )

            # 根据status存储的当时的fields的值更新
            if log.type == TRANSITION_OPERATE:
                for field in state_info.get("fields", []):
                    field.update(
                        value=status_fields.get(str(field["id"]), {}).get(
                            "value", field["value"]
                        ),
                        display_value=status_fields.get(str(field["id"]), {}).get(
                            "display_value", field["display_value"]
                        ),
                        choice=status_fields.get(str(field["id"]), {}).get(
                            "choice", field["choice"]
                        ),
                    )
            else:
                # 认领/分派/挂起/恢复挂起/转单等操作，字段置空
                state_info.update(fields=[])

            message = _(log.message)
            if log.type == SYSTEM_OPERATE:
                message = message.format(
                    name=log.from_state_name, detail_message=log.detail_message
                )
            else:
                message = message.format(
                    operator=log.operator,
                    name=log.from_state_name,
                    action=_(log.action).lower(),
                    detail_message=log.detail_message,
                )

            state_info.update(
                operator=log.operator,
                operate_at=log.operate_at.strftime("%Y-%m-%d %H:%M:%S"),
                action=_(OPERATE_TYPE.get(log.type, "")),
                message=message,
                status=FINISHED,
            )
            state_list.append(state_info)

        # running state
        running_state = self.node_status.filter(status=RUNNING)
        running_status = StatusSerializer(
            running_state,
            many=True,
            context={
                "username": username,
                "show_all_fields": False,
            },
        )
        state_info = running_status.data
        for state in state_info:
            state.update(
                operator=state["processors"],
                operate_at="--",
                action="--",
                message="--",
                status=RUNNING,
            )
        state_list += state_info

        # append end status
        if self.is_over:
            try:
                end_log = self.logs.get(
                    is_valid=True, from_state_id=self.end_state["id"]
                )
                state_list.append(
                    {
                        "name": _("结束"),
                        "operator": "system",
                        "operate_at": end_log.operate_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "fields": [],
                        "message": end_log.message,
                        "action": "",
                    }
                )
            except Exception:
                state_list.append(
                    {
                        "name": _("结束"),
                        "operator": "system",
                        "operate_at": self.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "fields": [],
                        "message": "",
                        "action": "",
                    }
                )

        return state_list

    def get_wx_states(self, username):
        """
        微信节点
        """

        from itsm.ticket.serializers import StatusSerializer

        if self.flow.engine_version == DEFAULT_ENGINE_VERSION:
            status_serializer_data = StatusSerializer(
                self.node_status,
                many=True,
                context={
                    "username": username,
                    "bk_biz_id": self.bk_biz_id,
                    "show_all_fields": True,
                },
            ).data
            for status in status_serializer_data:
                log = self.logs.filter(status=status["id"]).last()
                if log:
                    status.update(
                        operator=transform_single_username(log.operator),
                        operate_at=log.operate_at.strftime("%Y-%m-%d %H:%M:%S"),
                        action=ACTION_DICT.get(log.type, ""),
                    )
                else:
                    status.update(
                        operator=status["processors"], operate_at="--", action="--"
                    )
                for index, item in enumerate(status["operations"]):
                    if status["operations"][index]["key"] == TRANSITION_OPERATE:
                        status["operations"][index]["name"] = _("处理")

            return status_serializer_data

        # old tickets
        states = self.get_old_ticket_state_list()
        return states

    def get_old_ticket_state_list(self):
        """兼容2.2.x之前已结束的单据展示"""

        from itsm.ticket.serializers import OldTicketStateSerializer

        old_ticket_states = OldTicketStateSerializer(
            list(self.flow.states.values()), many=True, context={"ticket": self}
        ).data
        states = [
            state
            for state in old_ticket_states
            if state["type"] not in ["START", "END"]
        ]
        master_ids = [state["id"] for state in self.flow.master]
        states.sort(key=lambda x: master_ids.index(x["id"]), reverse=True)
        for state in states:
            log = self.logs.filter(from_state_id=state["state_id"]).last()
            state.update(
                operator=transform_single_username(log.operator),
                operate_at=log.operate_at.strftime("%Y-%m-%d %H:%M:%S"),
                action=OPERATE_TYPE.get(log.type, ""),
                message=log.message,
            )
        return states

    def table_fields(self):

        # 兼容旧数据
        if not self.flow.table:
            return []

        table_field_order = self.flow.table.get("field_key_order", [])
        if not table_field_order:
            return []

        fields = list(self.fields.filter(source=BASE_MODEL, state_id=""))
        fields.sort(key=lambda x: table_field_order.index(x.key))
        return fields

    # ======================================单据操作接口================================================

    def start(self, **kwargs):
        """创建当前单据对应的流程快照"""

        # 创建并启动pipeline
        print("\n-------  ticket pipeline start  ----------\n")
        pipeline_wrapper = PipelineWrapper(kwargs.pop("flow", self.flow))
        pipeline_data = pipeline_wrapper.create_pipeline(
            self.id, need_start=True, **kwargs
        )

        self.pipeline_data = pipeline_data
        self.save(update_fields=("pipeline_data",))

    def clone_pipeline(self, parent_ticket):
        # 创建并启动pipeline
        print("\n-------  clone parent ticket pipeline start  ----------\n")
        from pipeline.engine.models import (
            PipelineProcess,
            Status as PipelineStatus,
            PipelineModel,
        )  # noqa

        # 第一步，删除原有pipeline信息
        PipelineStatus.objects.filter(id=self.id).delete()
        PipelineProcess.objects.filter(root_pipeline_id=self.id).delete()
        PipelineModel.objects.filter(id=self.id).delete()

        # 删除node_status的内容
        self.node_status.all().exclude(state_id=self.first_state_id).delete()

        # 删除掉除了提单节点以外的内容
        self.logs.all().exclude(
            from_state_id__in=[self.first_state_id, self.start_state["id"]]
        ).delete()

        # 结束节点也要去掉 Todo: 但是子单的end时间还是跟母单不一样
        parent_logs = parent_ticket.logs.all().exclude(
            from_state_id__in=[
                self.first_state_id,
                self.start_state["id"],
                self.end_state["id"],
            ]
        )
        for log in parent_logs:
            log.id = None
            log.ticket = self
            operate_at = log.operate_at
            log.save()
            # 改为和母单的日志创建时间一样
            log.operate_at = operate_at
            log.save()

        # 第二步，重新启动
        # 使用母单的flow初始化pipeline, 所有state_id来源母单
        self.start(
            is_cloning=True, parent_ticket_id=parent_ticket.id, flow=parent_ticket.flow
        )

    def activity_callback(self, state_id, operator, fields=None, source=WEB):
        # 转换state_id为activity_id
        if fields is None:
            fields = []
        activity_id = self.activity_for_state(state_id)
        callback_data = {
            "ticket_id": self.id,
            "fields": fields,
            "state_id": state_id,
            "operator": operator,
            "source": source,
        }
        try:
            return pipeline_api.activity_callback(activity_id, callback_data)
        except Exception as e:
            raise CallPipelineError(_("流程服务异常（%s）") % e)

    def retry_node(self, state_id, inputs=None, action=RETRY, operator="system"):
        if inputs is None:
            inputs = []
        try:
            if action == RETRY:
                self.node_status.filter(state_id=state_id).update(
                    query_params=inputs, status=QUEUEING
                )
            else:
                self.node_status.filter(state_id=state_id).update(
                    ignore_params=inputs, status=QUEUEING
                )
            cache.set(
                "node_retry_{}_{}".format(self.id, state_id),
                json.dumps({"action": action, "operator": operator}),
                CACHE_1H,
            )
            node_id = self.pipeline_data["states_map"].get(str(state_id))
            res = pipeline_api.retry_node(node_id)
            if not res.result:
                logger.warning(
                    "callback error， current state id %s, error message: %s"
                    % (state_id, res.message)
                )
                self.node_status.filter(state_id=state_id).update(status=RUNNING)
            return res
        except Exception as e:
            raise CallPipelineError(_("流程服务异常（%s）") % e)

    def do_before_enter_state(self, state_id, **kwargs):
        """进入节点前的准备动作
        1. 更新单据状态：处理人/单据状态/各节点状态
        2. 判断是否启动任务模块
        3. 发送通知信息
        """
        # 线条信号
        from_transitions = self.get_from_transition(kwargs.get("by_flow"))
        for from_transition in from_transitions:
            self.send_trigger_signal(THROUGH_TRANSITION, sender=from_transition["id"])

        # 更新节点
        status = self.update_state_before_enter(state_id, **kwargs)

        # 单据绑定节点
        self.node_status.add(status)

        # 更新单据 暂时保留此功能
        self.update_ticket_before_enter(status)

        # Set ticket operator
        self.set_current_processors()

        # 判断是否启动任务模块
        if status.can_execute_task(is_system=True):
            status.start_task()

        # 判断节点是否SLA开始节点 创建启动SLA任务
        if self.is_sla_start_state(state_id):
            self.create_sla_task(state_id=state_id)
            self.start_sla(state_id)

        self.send_trigger_signal(
            ENTER_STATE,
            sender=state_id,
            context={"dst_state": status.id, "operator": self.creator},
        )

        # 全局 进入节点 触发器
        self.send_trigger_signal(GLOBAL_ENTER_STATE, sender=self.flow.workflow_id)

        # 提单节点给提单人发送关注通知邮件, 非提单节点给处理人发送单据待办通知邮件
        context = {}
        status.refresh_from_db()
        if state_id == self.first_state_id:
            receivers = self.creator
            action = FOLLOW_OPERATE
            # 提单节点无法获取当前运行节点, 所以手动传入上下文
            context = {"running_status": status.name}
        else:
            receivers = ",".join(status.get_processors())
            action = TRANSITION_OPERATE
        self.notify(
            state_id,
            receivers,
            action=action,
            retry=kwargs.get("retry", True),
            **context
        )

    def do_before_enter_sign_state(self, state_id, **kwargs):
        """Actions before enter sign state
        1. Sync variables to TicketGlobalVariable
        2. Create node and binding ticket
        3. Update Ticket status
        4. Update Ticket processors
        5. Send notify
        """
        # 线条信号
        from_transitions = self.get_from_transition(kwargs.get("by_flow"))
        for from_transition in from_transitions:
            self.send_trigger_signal(THROUGH_TRANSITION, sender=from_transition["id"])

        state = self.flow.get_state(state_id)
        variables = state["variables"].get("outputs", [])
        finish_condition = state["finish_condition"]

        # Sync variables to TicketGlobalVariable  and Get code key mapping
        ticket_global_variable_objs = []
        code_key = {}
        for variable in variables:
            ticket_global_variable_objs.append(
                TicketGlobalVariable(
                    **{
                        "key": variable.get("key", ""),
                        "name": variable.get("name", ""),
                        "state_id": state_id,
                        "ticket_id": self.id,
                    }
                )
            )
            # Get code-key mapping
            if variable.get("meta", {}).get("code"):
                code_key[variable["meta"]["code"]] = variable["key"]
        TicketGlobalVariable.objects.bulk_create(ticket_global_variable_objs)

        node_status = self.update_state_before_enter(state_id, **kwargs)
        self.node_status.add(node_status)
        self.update_ticket_before_enter(node_status)

        self.set_current_processors()

        # 判断是否启动任务模块
        if node_status.can_execute_task(is_system=True):
            node_status.start_task()

        # 判断节点是否SLA开始节点 创建启动SLA任务
        if self.is_sla_start_state(state_id):
            self.create_sla_task(state_id=state_id)
            self.start_sla(state_id)

        # 全局 进入节点 触发球
        self.send_trigger_signal(GLOBAL_ENTER_STATE, sender=self.flow.workflow_id)

        # 发送进入节点的信号
        self.send_trigger_signal(
            ENTER_STATE, sender=state_id, context={"dst_state": node_status.id}
        )

        # Send notify
        processor = node_status.get_processor_in_sign_state()
        # 快速审批通知
        self.notify_fast_approval(
            state_id, processor, "", action=TRANSITION_OPERATE, kwargs=kwargs
        )

        # TODO 发送通知可用触发器替代
        self.notify(
            state_id,
            processor,
            action=TRANSITION_OPERATE,
            retry=kwargs.get("retry", True),
        )

        return variables, finish_condition, code_key

    def get_fast_approval_message_params(self):
        """获取快速审批模版所需参数"""
        return {
            "title": self.title,
            "ticket_url": self.ticket_url,
            "sn": self.sn,
            "catalog_service_name": self.catalog_service_name,
            "running_status": self.running_status,
        }

    def set_current_processors(self):
        """单据中设置当前的操作人员"""

        def _formatted(processors_type, processors):
            """角色前缀格式化"""

            pros = list_by_separator(processors)

            if processors_type == ORGANIZATION:
                return map(lambda x: "O_{}".format(x), pros)

            return pros

        node_processors = []
        task_processors = []
        for node_status in self.node_status.filter(
            Q(status__in=Status.CAN_OPERATE_STATUS) | Q(status=FAILED, type=TASK_STATE)
        ):
            # Get all types node processors
            if node_status.type in [SIGN_STATE, APPROVAL_STATE]:
                processor = node_status.get_processor_in_sign_state()
                processor_list = list_by_separator(processor)
            else:
                processor_list = _formatted(
                    node_status.processors_type, node_status.processors
                )

            node_processors.extend(
                processor
                for processor in processor_list
                if processor and processor not in node_processors
            )

            tasks = Task.objects.filter(
                ticket_id=self.id,
                execute_state_id=node_status.state_id,
                status__in=[QUEUE, WAITING_FOR_OPERATE],
            )
            for task in tasks:
                task_processors.extend(
                    _formatted(task.processors_type, task.processors)
                )

        current_processors = node_processors[:]
        current_processors.extend(
            processor
            for processor in task_processors
            if processor and processor not in current_processors
        )

        self.current_processors = dotted_name(",".join(current_processors))
        self.save(update_fields=("current_processors",))

        # 批量同步修改子单
        if self.is_master:
            slaves = self.slave_tickets
            for slave in slaves:
                slave.current_processors = node_processors
            bulk_update(slaves, update_fields=["current_processors"])

    def set_history_operators(self, current_operator):
        """设置历史处理人"""
        history_operators = [user for user in self.updated_by.split(",") if user]
        if current_operator not in history_operators:
            history_operators.append(current_operator)
        self.updated_by = dotted_name(",".join(set(history_operators)))
        self.save(update_fields=("updated_by",))

    def do_in_sign_state(self, node_status, fields, operator, source):
        """
        In sign node action
        1. Update ticket status
        2. Create sign task
        3. Create task fields
        4. Update ticket priority, processors, history operators
        5. Update sla task
        6. Create log
        """
        from itsm.ticket.serializers import TaskFieldSerializer

        # Update ticket status
        self.update_ticket_status(fields, operator)

        # Create sign task
        task, result = SignTask.objects.update_or_create(
            status_id=node_status.id,
            processor=operator,
            defaults={"status": "RUNNING"},
        )
        # Create task fields
        task_field_objs = []
        field_map = {}
        is_passed = False
        for f in fields:
            f.pop("id", None)
            f.pop("choice", None)
            f["_value"] = f.pop("value", "")
            field_map[f["key"]] = f

        node_fields = TicketField.objects.filter(
            state_id=node_status.state_id, ticket_id=self.id
        )
        exclude_fields = list(TicketField.FIELDS) + ["id", "ticket"]
        for node_field in node_fields:
            node_field_dict = node_field.tag_data(exclude=exclude_fields)
            if node_field.key not in field_map:
                continue
            update_dict = dict(field_map[node_field.key], task_id=task.id)
            node_field_dict.update(update_dict)
            task_field_objs.append(TaskField(**node_field_dict))

            # Table field need sync to BASE-MODEL field
            if node_field_dict["source"] == TABLE:
                TicketField.objects.filter(
                    ticket_id=self.id, key=node_field_dict["key"]
                ).update(_value=node_field_dict["_value"])

            # Get sign task approve result
            if (
                node_field.meta.get("code") == APPROVE_RESULT
                and node_field_dict["_value"] == "true"
            ):
                is_passed = True

        task_fields = TaskField.objects.bulk_create(task_field_objs)

        task.is_passed = is_passed
        task.save()

        # Sequential node send notify every finish a task
        if node_status.is_sequential:
            processor = node_status.get_processor_in_sign_state()
            self.notify(node_status.state_id, processor, action=TRANSITION_OPERATE)

        # Update ticket priority, processors, history operators
        self.update_priority()
        # self.set_current_processors()
        self.set_history_operators(operator)

        # Update sla task
        # if self._sla_tasks:
        #     self.refresh_sla_task()

        # Event log form data
        task_fields_list = TaskFieldSerializer(task_fields, many=True).data
        # Create log
        TicketEventLog.objects.create_sign_state_log(
            self, node_status, operator, source, task_fields_list
        )
        SignTask.objects.filter(status_id=node_status.id, processor=operator).update(
            status="EXECUTED"
        )

    def do_before_exit_sign_state(self, state_id):
        status = self.status(state_id)
        status.status = FINISHED
        status.save()

        if self.is_sla_end_state(state_id):
            self.stop_sla(state_id)

        self.send_trigger_signal(LEAVE_STATE, state_id)

        # 全局触发器
        self.send_trigger_signal(GLOBAL_LEAVE_STATE, sender=self.flow.workflow_id)

    def do_in_state(self, state_id, fields, operator, source):
        """节点内动作
        1. 填充表单
        """
        self.proceed(state_id, fields, operator, source)

    def do_before_exit_state(self, state_id, operator=None):
        """退出节点前的清理动作
        1. 更新单据信息：同步字段值到单据
        2. 单据转正
        """

        self.set_current_processors()

        if str(state_id) == self.first_state_id:
            self.title = self.get_field_value("title", "--")
            self.bk_biz_id = self.get_field_value("bk_biz_id", DEFAULT_BK_BIZ_ID)
            self.save(update_fields=("title", "bk_biz_id"))

        if self.is_sla_end_state(state_id):
            self.stop_sla(state_id)

        current_status = Status.objects.filter(
            ticket_id=self.id, state_id=state_id
        ).first()
        if current_status is None:
            logger.info(
                "get status object does not exist, param: ticket_id={}, state_id={}".format(
                    self.id, state_id
                )
            )
            raise ObjectNotExist(_("没有获取到当前节点处理状态"))
        if current_status.status == FINISHED:
            self.send_trigger_signal(
                LEAVE_STATE, state_id, context={"operator": operator}
            )
            # 全局触发器
            self.send_trigger_signal(GLOBAL_LEAVE_STATE, sender=self.flow.workflow_id)

    def do_after_create(self, fields, from_ticket_id=None, source=WEB):
        # 创建关联关系
        self.create_ticket_relation(from_ticket_id)
        print("----- create ticket create_ticket_relation end")

        # 启动SLA任务
        print("----- create ticket create_sla_task end")

        # 单据上下文准备：创建字段
        self.prepare_all_fields()
        print("----- create ticket prepare_all_fields end")
        # 创建开始流转日志
        TicketEventLog.objects.create_start_log(self)
        print("----- create ticket create_start_log end")

        # 为sla提前初始化优先级
        self.fill_state_fields(fields)
        self.update_priority()

        self.do_before_enter_state(self.first_state_id)
        print("----- create ticket do_before_enter_state end")
        self.do_in_state(self.first_state_id, fields, self.creator, source)
        print("----- create ticket do_in_state end")

        # 更新公共字段
        self.fields.filter(key=FIELD_STATUS).update(_value=self.current_status)

        self.do_before_exit_state(self.first_state_id)
        print("----- create ticket do_before_exit_state end")

        # 发送创建成功的信号
        self.send_trigger_signal(CREATE_TICKET)

    def get_list_view(self):
        list_view = [
            {"key": "单号", "value": self.sn},
            {"key": "服务目录", "value": self.catalog_fullname},
            {"key": "提单人", "value": self.creator},
        ]
        reason = self.get_field_value("reason", None)
        if reason is None:
            list_view.append(
                {"key": "提单时间", "value": self.create_at.strftime("%Y-%m-%d %H:%M:%S")}
            )
        else:
            list_view.append({"key": "申请理由", "value": reason})

        return list_view

    @staticmethod
    def display_content(field_type, content):
        if field_type != "CUSTOM-FORM":
            return content
        try:
            schemes_map = {}
            schemes = [form_data["scheme"] for form_data in content["form_data"]]
            for scheme_name in schemes:
                schemes_map[scheme_name] = {
                    column["key"]: column["name"]
                    for column in content["schemes"][scheme_name]["attrs"].get(
                        "column", []
                    )
                }

            text_content = []
            for data in content["form_data"]:
                scheme = data["scheme"]
                label = data["label"]
                detail = []
                if isinstance(data["value"], str):
                    if label and data["value"]:
                        text_content.append("{}:\n{}\n".format(label, data["value"]))
                    continue
                for attr in data["value"]:
                    single = []
                    for attr_name, attr_value in attr.items():
                        try:
                            if isinstance(attr_value["value"], str):
                                single.append(
                                    "{}:{}".format(
                                        schemes_map[scheme][attr_name],
                                        attr_value["value"],
                                    )
                                )
                        except Exception as err:
                            logger.error(
                                "parser moa content error, form data is {}, err is {}".format(
                                    data, err
                                )
                            )
                    detail.append(",".join(single))
                if label:
                    text_content.append("{}:\n{}\n".format(label, "\n".join(detail)))
            return "\n".join(text_content)
        except Exception as err:
            logger.exception(
                "create_moa_ticket parser CUSTOM-FORM error, msg is {}".format(err)
            )
            return ""

    def send_trigger_signal(self, signal, sender=None, context=None):
        from itsm.iadmin.utils import is_trigger_switch_off

        if is_trigger_switch_off():
            # 如果触发器关闭的话，直接返回
            return

        if not isinstance(context, dict):
            context = {}

        context.update(
            {
                item["key"]: item["value"]
                for item in self.get_output_fields(need_display=True)
            }
        )
        context.update({"dst_ticket": self.id})

        try:
            logger.info(
                "[ticket->send_trigger_signal] 正在发送触发器事件, signal={}, ticket_id={}".format(
                    signal, self.id
                )
            )
            trigger_signal.send(
                signal,
                sender=sender,
                source_type=SOURCE_TICKET,
                source_id=self.id,
                context=context,
                rule_source_id=self.flow.id,
                rule_source_type=SOURCE_TICKET,
            )
            logger.info(
                "[ticket->send_trigger_signal] 触发器发送发生成功, ticket_id={}".format(self.id)
            )
        except BaseException:
            logger.info(
                "[ticket->send_trigger_signal] 触发器事件发送失败, ticket_id={}".format(self.id)
            )
            logger.exception(
                _("触发器事件发送失败, ticket_sn {} signal ：{}").format(self.sn, signal)
            )

    def create_ticket_relation(self, from_ticket_id):
        # 创建单据关联关系
        if not from_ticket_id:
            return

        TicketToTicket.objects.create(
            from_ticket_id=from_ticket_id,
            to_ticket_id=self.id,
            related_type=DERIVE,
            creator=self.creator,
        )
        # 创建关联单的信号发出
        self.send_trigger_signal(CREATE_RELATE_TICKET)

    def can_schedule(self, state_id):
        schema_ids = TaskConfig.objects.filter(
            workflow_id=self.flow_id,
            workflow_type=VERSION,
            execute_task_state=state_id,
            need_task_finished=True,
        ).values_list("task_schema_id")
        is_exist = (
            Task.objects.filter(
                ticket_id=self.pk,
                execute_state_id=state_id,
                task_schema_id__in=schema_ids,
            )
            .exclude(status__in=["FINISHED", "SKIPPED"])
            .exists()
        )
        return not is_exist

    @property
    def is_schedule_ready(self):
        """任务控制流程节点的提交"""

        for state_id in self.current_state_ids:
            schema_ids = TaskConfig.objects.filter(
                workflow_id=self.flow_id,
                workflow_type=VERSION,
                execute_task_state=state_id,
                need_task_finished=True,
            ).values_list("task_schema_id")
            if schema_ids:
                is_exist = (
                    Task.objects.filter(
                        ticket_id=self.pk,
                        execute_state_id=state_id,
                        task_schema_id__in=schema_ids,
                    )
                    .exclude(status="FINISHED")
                    .exists()
                )
                if is_exist:
                    return False
        return True

    def update_task_when_enter_state(self, state_id=None):
        """进入执行任务节点时更新子任务为QUEUE
        NEW->QUEUE
        """

        # 进入任务执行节点时
        is_execute = TaskConfig.objects.filter(
            workflow_id=self.flow_id, workflow_type=VERSION, execute_task_state=state_id
        ).exists()
        if not is_execute:
            return

        # 更新任务状态
        Task.objects.filter(ticket_id=self.pk, status="NEW").update(status="QUEUE")

        # 更新单据中的任务处理人
        operators = []
        for task in Task.objects.filter(ticket_id=self.pk, status="QUEUE"):
            # 支持通用角色
            if task.processors_type == PERSON:
                operators.extend(task.processor_user_list)
            elif task.processors_type == GENERAL:
                operators.extend(list_by_separator(task.processors))

        self.current_task_processors = dotted_name(",".join(list(set(operators))))
        self.save()

    def add_history_task_processors(self, username):
        """追加历史任务处理人"""
        history_task_processors = list_by_separator(self.history_task_processors)
        history_task_processors.append(username)
        self.history_task_processors = dotted_name(",".join(history_task_processors))
        self.save()

    def close(self, close_status, desc="", operator=""):
        # 关闭单据
        self.do_before_end_pipeline(operator, close_status, desc, source=WEB)
        # 直接终止后台流程
        task_service.revoke_pipeline(self.id)

        self.stop_all_sla()
        return

    def do_before_end_pipeline(
        self, operator="", close_status=FINISHED, desc="", source=SYS, by_flow=None
    ):
        self.set_finished(
            operator=operator,
            close_status=close_status,
            desc=desc,
            source=source,
            last_flow=by_flow,
        )

        self.send_trigger_signal(CLOSE_TICKET)

        self.notify(
            state_id="",
            receivers=self.creator,
            message=_("您的单据已经完成！"),
            action=FINISHED,
            retry=False,
        )
        return

    def proceed(self, state_id, fields, operator="", source=WEB):
        """处理单据
        1. 保存表单
        2. 创建日志
        3. 发送通知? 离开发送？
        """

        state = self.state(state_id)

        message = _("{operator} 处理【{name}】")
        with transaction.atomic():
            # 1、更新单据字段
            self.fill_state_fields(fields)

            # 更新优先级
            self.update_priority()

            # 1、更新状态 2、保存字段到status.fields
            self.update_status(state_id)

            # 新建操作日志
            TicketEventLog.objects.create_log(
                self,
                state_id,
                operator,
                message=message,
                action="提交",
                from_state_name=state.get("name"),
                source=source,
            )

            self.update_ticket_status(fields, operator)

    def skip_node(self, state_id, operator="", source=WEB):
        message = "{operator} 忽略了【{name}】的执行结果."
        state = self.state(state_id)
        node_id = self.pipeline_data["states_map"].get(str(state_id))
        action_result = pipeline_api.skip_node(node_id)
        TicketEventLog.objects.create_log(
            self,
            state_id,
            operator,
            from_state_name=state.get("name"),
            message=message,
            source=source,
            action=API_DICT[IGNORE],
            operate_type=IGNORE,
        )
        return action_result

    def skip_gateway_node(self, state_id, transition_id):
        node_id = self.pipeline_data["exclusive_gateway_source_state"].get(
            str(state_id)
        )
        flow_id = {
            value: key for key, value in self.pipeline_data["transitions_map"].items()
        }.get(str(transition_id))
        return pipeline_api.skip_exclusive_gateway(node_id, flow_id)

    def update_ticket_status(self, fields, operator):
        # 根据FIELD_STATUS字段更新单据状态
        field_kv = {field["key"]: field["value"] for field in fields}
        if FIELD_STATUS in field_kv:
            next_status = field_kv.get(FIELD_STATUS)

            if next_status in self.status_instance.to_over_status_keys:
                self.close(next_status, operator=operator)
                return

            self.current_status = next_status
            self.save()

    def update_status(self, state_id):
        """更新当前节点的字段信息"""
        from itsm.ticket.serializers import FieldSerializer

        status = self.status(state_id)
        status.status = FINISHED
        all_fields = FieldSerializer(
            status.ticket_fields, many=True, context={"show_all_fields": False}
        ).data
        status.fields = [field for field in all_fields]
        status.save()

    def terminate(self, state_id, operator="", terminate_message="--"):
        """终止单据"""
        node_status = self.status(state_id)
        message = _("{operator}处理节点【{name}】(流程被终止，【终止原因】:{detail_message}).")
        # 创建流转日志
        with transaction.atomic():
            # 撤销流程
            res = task_service.revoke_pipeline(self.id)

            if not res.result:
                raise RevokePipelineError(res.message)

            # 更新节点状态及终止原因
            node_status.set_status(
                TERMINATED, operator, terminate_message=terminate_message
            )

            for ticket in self.master_slave_tickets:
                TicketEventLog.objects.create_log(
                    ticket,
                    state_id,
                    operator,
                    TRANSITION_OPERATE,
                    message=message,
                    detail_message=terminate_message,
                    from_state_name=node_status.name,
                    transition_id=VIRTUAL_TRANSITION_ID,
                    to_state_id=self.end_state.get("id"),
                )

                # 单据结束创建评价信息
                TicketComment.objects.get_or_create(ticket_id=ticket.id)
                ticket.end_at = datetime.now()
                ticket.save()

            # 单据状态设置：终止了某一个节点 -> 终止整个流程
            self.update_current_status(TERMINATED)

            self.send_trigger_signal(TERMINATE_TICKET)

            # 向提单人发送通知
            message = message.format(
                operator=operator,
                name=node_status.name,
                detail_message=terminate_message,
            )
            self.close_moa_ticket(state_id, operator)
            self.callback_request()
            self.notify(
                state_id=state_id,
                receivers=self.creator,
                message=message,
                action=TERMINATE_OPERATE,
                retry=False,
            )

        self.stop_all_sla()

        return {"result": True, "message": _("流程终止成功：%s") % res.message, "code": 0}

    def suspend(self, suspend_message, operator="system"):
        """挂起"""

        self.update_current_status("SUSPENDED")
        message = "{operator} 挂起了单据：{detail_message}."
        tlog = TicketEventLog.objects.create_log(
            self,
            0,
            operator,
            operate_type=SUSPEND_OPERATE,
            message=message,
            detail_message=suspend_message,
            to_state_id=0,
        )

        self.send_trigger_signal(
            SUSPEND_TICKET, context={"suspend_message": suspend_message}
        )

        # 向提单人发送通知
        self.notify(
            state_id="",
            receivers=self.creator,
            message=tlog.translated_message,
            action=SUSPEND_OPERATE,
            retry=False,
        )

        # 暂停SLA计时
        self.pause_sla()

    def unsuspend(self, operator="system"):
        """恢复"""

        message = "{operator} 恢复了单据."

        # 确保恢复操作后，状态不再是挂起状态?? 如果之前是suspend，恢复之后还是suspend？
        if self.pre_status != "SUSPENDED":
            status = "RUNNING" if not self.pre_status else self.pre_status
            self.update_current_status(status)

        tlog = TicketEventLog.objects.create_log(
            self, 0, operator, UNSUSPEND_OPERATE, message=message, to_state_id=0
        )
        # 向提单人发送通知
        self.send_trigger_signal(RECOVERY_TICKET)

        self.notify(
            state_id="",
            receivers=self.creator,
            message=tlog.translated_message,
            action=UNSUSPEND_OPERATE,
            retry=False,
        )

        # 恢复SLA计时
        self.resume_sla()

    def withdraw(self, operator, source):
        """撤销单据"""
        running_status = Status.objects.get_running_status(self.id)
        state_id = (
            running_status.first().state_id if running_status else self.first_state_id
        )

        node_status = self.status(state_id)

        message = "{operator} 撤销单据."

        with transaction.atomic():
            end_at = datetime.now()
            node_status.set_status(TERMINATED, operator, terminate_message=message)
            for ticket in self.master_slave_tickets:
                TicketEventLog.objects.create_log(
                    ticket,
                    state_id,
                    operator,
                    WITHDRAW_OPERATE,
                    message=message,
                    transition_id=VIRTUAL_TRANSITION_ID,
                    to_state_id=state_id,
                    source=source,
                )
                # TODO 应该按照母子单来操作
                # ticket.is_deleted = True
                ticket.current_status = "REVOKED"
                ticket.end_at = end_at
                ticket.save()

            # 更新状态
            self.update_current_status("REVOKED")
            self.close_moa_ticket(state_id, operator)
            self.callback_request()

        self.stop_all_sla()

        # 撤销单据触发信号发送
        self.send_trigger_signal(DELETE_TICKET)

    def revoke(self):
        pipeline_api.delete_pipeline_data(self.id)
        Status.objects.filter(ticket_id=self.id).delete()

    # =======================================兼容流程引擎前版本旧单据接口==================================

    def get_current_state_name(self):
        state = self.flow.states.get(str(self.current_state_id))
        return state["name"] if state is not None else "--"

    def get_current_role_display(self):
        """获取对应角色的名称"""
        if self.current_processors_type == "BY_ASSIGNOR":
            return "派单人指定"

        if self.current_processors_type not in ["GENERAL", "CMDB"]:
            return "个人"

        try:
            role = UserRole.objects.get(id=self.current_processors)
            return "%s-> %s" % (
                "通用角色" if role.role_type == "GENERAL" else "CMDB角色",
                role.name,
            )
        except UserRole.DoesNotExist:
            return ""

    def get_current_processors(self, bk_biz_id=None):
        """获取当前处理人列表"""

        users = UserRole.get_users_by_type(
            bk_biz_id if bk_biz_id else self.bk_biz_id,
            self.current_processors_type,
            self.current_processors,
            self,
        )

        return users

    def get_from_transition(self, pipeline_flow_id):
        if "transitions_map" not in self.pipeline_data:
            return []
        transition_id = self.pipeline_data.get("transitions_map", {}).get(
            pipeline_flow_id
        )
        # if transition_id:
        #     return self.flow.transitions[transition_id]
        if transition_id:
            transition_detail = self.flow.transitions[transition_id]
            transition_list = []

            def parser_transition(transition_info, pre_transition_list):
                pre_transition_list.append(transition_info)
                from_state = transition_info["from_state"]
                state_info = self.flow.states[str(from_state)]
                if state_info["type"] in ["ROUTER-P", "COVERAGE"]:
                    for trans_id, transition in self.flow.transitions.items():
                        if transition["to_state"] == from_state:
                            parser_transition(transition, pre_transition_list)

            parser_transition(transition_detail, transition_list)
            return transition_list
        return []

    def update_organization_ticket(self):
        try:
            departments = get_user_departments(self.creator, id_only=False)
            for department in departments:
                family = list(reversed(department["family"]))
                second_level_id, second_level_name = (
                    (int(family[0]["id"]), family[0]["name"])
                    if len(family) > 0
                    else (-1, _("其他"))
                )
                third_level_id, third_level_name = (
                    (int(family[1]["id"]), family[1]["name"])
                    if len(family) > 1
                    else (-1, _("其他"))
                )
                TicketOrganization.objects.create(
                    username=self.creator,
                    first_level_id=int(department["id"]),
                    first_level_name=department["name"],
                    second_level_id=second_level_id,
                    second_level_name=second_level_name,
                    third_level_id=third_level_id,
                    third_level_name=third_level_name,
                    create_at=datetime.now(),
                    family=family,
                )
        except Exception as err:
            logger.exception("update_organization_ticket failed, msg is {}".format(err))

    @classmethod
    def sync_organization_ticket(cls):
        TicketOrganization.objects.all().delete()
        tickets = cls.objects.all().order_by("id").values("creator", "create_at")
        user_departments = {}
        organization_info = []
        for ticket in tickets:
            if ticket["creator"] not in user_departments:
                user_departments[ticket["creator"]] = get_user_departments(
                    ticket["creator"], id_only=False
                )
            for department in user_departments[ticket["creator"]]:
                family = list(reversed(department["family"]))
                second_level_id, second_level_name = (
                    (int(family[0]["id"]), family[0]["name"])
                    if len(family) > 0
                    else (-1, _("其他"))
                )
                third_level_id, third_level_name = (
                    (int(family[1]["id"]), family[1]["name"])
                    if len(family) > 1
                    else (-1, _("其他"))
                )
                organization_info.append(
                    TicketOrganization(
                        **{
                            "username": ticket["creator"],
                            "create_at": ticket["create_at"],
                            "first_level_id": int(department["id"]),
                            "first_level_name": department["name"],
                            "second_level_id": second_level_id,
                            "second_level_name": second_level_name,
                            "third_level_id": third_level_id,
                            "third_level_name": third_level_name,
                            "family": family,
                        }
                    )
                )
        TicketOrganization.objects.bulk_create(organization_info)

    @classmethod
    def get_count(cls, service_id=None, scope=None, project_query=Q()):
        tickets = cls.objects.filter(project_query)
        if service_id:
            tickets = tickets.filter(service_id=service_id)
        if scope:
            tickets = tickets.filter(create_at__range=scope)
        return tickets.count()

    @classmethod
    def get_biz_count(cls, service_id=None, scope=None, project_query=Q()):
        tickets = Ticket.objects.filter(project_query).filter(bk_biz_id__gt=-1)
        if service_id:
            tickets = tickets.filter(service_id=service_id)
        if scope:
            tickets = tickets.filter(create_at__range=scope)
        return len(set(tickets.values_list("bk_biz_id", flat=True)))

    @classmethod
    def get_ticket_user_count(cls, service_id, scope=None, project_query=Q()):
        tickets = cls.objects.filter(project_query).filter(service_id=service_id)
        event_log = TicketEventLog.objects.filter(
            ticket__id__in=set(tickets.values_list("id", flat=True))
        )
        if scope:
            print("scope is {}".format(scope))
            event_log = event_log.filter(operate_at__range=scope)

        users_count = len(set(event_log.values_list("operator", flat=True)))
        return users_count

    @classmethod
    def get_creator_statistics(cls, time_delta, time_range, project_key=None):
        project_query = Q(project_key=project_key) if project_key else Q()
        data_str = TIME_DELTA[time_delta].format(field_name="create_at")
        info = (
            cls.objects.filter(project_query)
            .filter(**time_range)
            .extra(select={"date_str": data_str})
            .values("date_str")
            .annotate(count=Count("creator", distinct=True))
            .order_by("date_str")
        )
        dates_range = fill_time_dimension(
            time_range["create_at__gte"], time_range["create_at__lte"], info, time_delta
        )
        return dates_range

    @classmethod
    def get_ticket_statistics(cls, time_delta, data, project_key=None):
        project_query = Q(project_key=project_key) if project_key else Q()
        data_str = TIME_DELTA[time_delta].format(field_name="create_at")
        info = (
            cls.objects.filter(project_query)
            .filter(**data)
            .extra(select={"date_str": data_str})
            .values("date_str")
            .annotate(count=Count("id"))
            .order_by("date_str")
        )
        dates_range = fill_time_dimension(
            data["create_at__gte"], data["create_at__lte"], info, time_delta
        )
        return dates_range

    @classmethod
    def get_biz_statistics(cls, time_delta, data, project_key=None):
        project_query = Q(project_key=project_key) if project_key else Q()
        data_str = TIME_DELTA[time_delta].format(field_name="create_at")
        info = (
            cls.objects.filter(project_query)
            .filter(**data)
            .filter(bk_biz_id__gt=-1)
            .extra(select={"date_str": data_str})
            .values("date_str")
            .annotate(count=Count("bk_biz_id", distinct=True))
            .order_by("date_str")
        )
        dates_range = fill_time_dimension(
            data["create_at__gte"], data["create_at__lte"], info, time_delta
        )
        return dates_range

    # ======================================= SLA功能接口 =====================================

    def refresh_sla_task(self):
        """刷新sla任务：
        刷新耗时和截止日期，并刷新任务
        """
        try:
            refresh_at = datetime.now()
            for sla_task in self._sla_tasks:
                sla_task.refresh(refresh_at)
        except Exception as e:
            logger.exception("refresh_sla_task exception: %s" % e)

    @property
    def slas(self):
        sla_ids = self._sla_tasks.values_list("sla_id", flat=True)
        return Sla.objects.filter(id__in=sla_ids)

    @property
    def _sla_tasks(self):
        return SlaTask.objects.filter(ticket_id=self.id)

    @property
    def sla_color(self):
        """单据高亮颜色"""

        if not self._sla_tasks.exists():
            return ""

        color = SlaTicketHighlight.objects.all().first()
        if self.is_sla_inner_state(self.current_state_ids):
            if self._sla_tasks.filter(sla_status=HANDLE_TIMEOUT).exists():
                return color.handle_timeout_color
            if self._sla_tasks.filter(sla_status=REPLY_TIMEOUT).exists():
                return color.reply_timeout_color

        return ""

    def create_sla_task(self, state_id=None):
        """
        创建sla任务
        """
        service_sla_objs = ServiceSla.objects.filter(service_id=self.service_id)

        if state_id:
            service_sla_objs = service_sla_objs.filter(start_node_id=state_id)

        # 服务SLA任务未启用
        if not service_sla_objs.exists():
            return

        # 任务是否需要响应
        sla_objs = Sla.objects.filter(
            id__in=service_sla_objs.values_list("sla_id", flat=True)
        ).values("id", "is_reply_need")
        reply_hash = {obj["id"]: obj["is_reply_need"] for obj in sla_objs}
        # 创建工单SLA任务
        sla_tasks = [
            SlaTask(
                sla_id=task.sla_id,
                name=task.name,
                ticket_id=self.id,
                start_node_id=task.start_node_id,
                end_node_id=task.end_node_id,
                is_reply_need=reply_hash.get(task.sla_id, False),
            )
            for task in service_sla_objs
        ]

        SlaTask.objects.bulk_create(sla_tasks)

    def is_sla_start_state(self, state_id):
        return ServiceSla.objects.filter(
            service_id=self.service_id, start_node_id=state_id
        ).exists()

    def is_sla_end_state(self, state_id):
        return ServiceSla.objects.filter(
            service_id=self.service_id, end_node_id=state_id
        ).exists()

    def is_sla_inner_state(self, state_ids):
        """判断当前节点是否在sla内"""

        inner_ids = set()
        # TODO ServiceSla缺少版本
        for states in ServiceSla.objects.filter(service_id=self.service_id).values_list(
            "states"
        ):
            inner_ids.update(states[0])

        return bool(set(state_ids) & inner_ids)

    def start_sla(self, state_id):

        begin_at = datetime.now()
        for sla_task in self._sla_tasks.filter(start_node_id=state_id).exclude(
            task_status=SLA_STOPPED
        ):
            sla_task.start(begin_at)

    def stop_sla(self, state_id):

        end_at = datetime.now()
        for sla_task in self._sla_tasks.filter(end_node_id=state_id).exclude(
            task_status=SLA_STOPPED
        ):
            sla_task.stop(end_at)

    def stop_all_sla(self):
        end_at = datetime.now()
        for sla_task in self._sla_tasks.exclude(task_status=SLA_STOPPED):
            sla_task.stop(end_at)

    def reply(self, state_id):
        """
        响应只在开始节点执行
        多个SLA任务只需响应1次
        """
        replied_at = datetime.now()
        for task in self._sla_tasks.filter(is_reply_need=True, start_node_id=state_id):
            task.reply(replied_at)

    def pause_sla(self):
        """暂停SLA计时"""
        pause_at = datetime.now()
        for task in self._sla_tasks.filter(task_status=SLA_RUNNING):
            task.pause(pause_at)

    def resume_sla(self):
        """恢复SLA计时"""
        resume_at = datetime.now()
        for task in self._sla_tasks.filter(task_status=SLA_PAUSED):
            task.resume(resume_at)

    def get_approve_fields(self, state_id, msg):
        node_fields = TicketField.objects.filter(state_id=state_id, ticket_id=self.id)
        fields = []
        remarked = False
        for field in node_fields:
            if field.meta.get("code") == APPROVE_RESULT:
                fields.append(
                    {
                        "id": field.id,
                        "key": field.key,
                        "type": field.type,
                        "choice": field.choice,
                        "value": "true",
                    }
                )
            else:
                if not remarked:
                    fields.append(
                        {
                            "id": field.id,
                            "key": field.key,
                            "type": field.type,
                            "choice": field.choice,
                            "value": msg,
                        }
                    )
                    remarked = True

        return fields

    @property
    def comment(self):
        return self.comments.comments

    @property
    def stars(self):
        return self.comments.stars

    def create_dynamic_fields(self, dynamic_fields):
        """
        dynamic_fields: list:[{
            "type": "INT",
            "name": "年龄",
            "value": 1
        }]
        """
        if not dynamic_fields:
            return

        fields = []
        for field in dynamic_fields:
            ticket_field = copy.deepcopy(field)
            ticket_field.pop("workflow_id", None)
            ticket_field.pop("flow_type", None)

            # 填充默认值
            default = ticket_field.pop("default", "")
            if default:
                ticket_field.update(_value=default)

            ticket_field["ticket_id"] = self.id

            ticket_field.pop("api_info", None)
            ticket_field.pop("project_key", None)
            ticket_field["workflow_field_id"] = 0
            fields.append(TicketField(**ticket_field))

        TicketField.objects.bulk_create(fields)


class TicketOrganization(Model):
    username = models.CharField(_("用户名"), max_length=LEN_LONG)
    first_level_id = models.IntegerField(_("一级组织id"), default=-1)
    first_level_name = models.CharField(
        _("一级组织名称"), max_length=LEN_LONG, default=_("其他")
    )
    second_level_id = models.IntegerField(_("二级组织id"), default=-1)
    second_level_name = models.CharField(
        _("二级组织名称"), max_length=LEN_LONG, default=_("其他")
    )
    third_level_id = models.IntegerField(_("三级组织id"), default=-1)
    third_level_name = models.CharField(
        _("三级组织名称"), max_length=LEN_LONG, default=_("其他")
    )
    family = jsonfield.JSONField(_("组织树"), default=EMPTY_DICT)
    create_at = models.DateTimeField(_("创建时间"))

    class Meta:
        app_label = "ticket"
        verbose_name = _("用户组织")
        verbose_name_plural = _("用户组织")
        index_together = (
            ("create_at", "username", "first_level_id"),
            ("first_level_id", "create_at"),
        )


class TicketToTicket(Model):
    """单据间关联"""

    RELATED_STATUS_CHOICES = [
        ("RUNNING", _("处理中")),
        ("BIND_SUCCESS", _("绑定成功")),
        ("BIND_FAILED", _("绑定失败")),
        ("UNBIND_SUCCESS", _("解绑成功")),
        ("UNBIND_FAILED", _("解绑失败")),
    ]

    from_ticket = models.ForeignKey(
        Ticket,
        help_text=_("源单据"),
        related_name="from_tickettotickets",
        null=True,
        on_delete=models.CASCADE,
    )
    to_ticket = models.ForeignKey(
        Ticket,
        help_text=_("目标单据"),
        related_name="to_tickettotickets",
        null=True,
        on_delete=models.CASCADE,
    )
    related_type = models.CharField(
        _("单据关联类型"), max_length=LEN_SHORT, choices=RELATE_CHOICES, default=DERIVE
    )
    related_status = models.CharField(
        _("关联状态"),
        max_length=LEN_SHORT,
        choices=RELATED_STATUS_CHOICES,
        default="BIND_SUCCESS",
    )

    objects = managers.Manager()
    raw_objects = models.Manager()

    class Meta:
        app_label = "ticket"
        verbose_name = _("单据间关联")
        verbose_name_plural = _("单据间关联")

    def __unicode__(self):
        return "{}->{}".format(self.from_ticket_id, self.to_ticket_id)


class StatusTransitLog(models.Model):
    """单据状态流转日志"""

    ticket = models.ForeignKey(
        Ticket,
        help_text=_("关联的单据"),
        related_name="transit_log",
        on_delete=models.CASCADE,
    )
    from_status = models.CharField(_("流转前的单据状态"), max_length=LEN_LONG)
    to_status = models.CharField(_("流转后的单据状态"), max_length=LEN_LONG)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)

    class Meta:
        app_label = "ticket"
        verbose_name = _("单据状态流转日志")
        verbose_name_plural = _("单据状态流转日志")

    def __unicode__(self):
        return "{}({}->{})".format(self.ticket.sn, self.from_status, self.to_status)


class AttentionUsers(models.Model):
    """单据关注人"""

    ticket_id = models.IntegerField(_("单号"))
    follower = models.CharField(_("关注人"), max_length=LEN_LONG)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)

    class Meta:
        app_label = "ticket"
        verbose_name = _("单据关注人")
        verbose_name_plural = _("单据状态流转日志")

    def __unicode__(self):
        return "{}({})".format(self.ticket_id, self.follower)

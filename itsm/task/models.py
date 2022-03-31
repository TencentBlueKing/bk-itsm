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

from functools import reduce
import operator as filter_operator
import copy
import datetime
import logging
import json
import jsonfield

from django.db.models import Q
from django.db import models, transaction
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from mako.template import Template
from bulk_update.helper import bulk_update
from pipeline.engine import api as pipeline_api
from itsm.component.esb.esbclient import client_backend, backend_client, client

from itsm.component.apigw import client as apigw_client
from itsm.component.utils.client_backend_query import get_biz_names
from itsm.component.utils.lock import share_lock
from itsm.component.db.models import Model
from itsm.component.db import managers
from itsm.component.constants.basic import (
    EMPTY_DICT,
    LEN_NORMAL,
    LEN_LONG,
    LEN_SHORT,
    EMPTY_STRING,
    EMPTY_INT,
    TASK_GLOBAL_VARIABLES,
    TICKET_GLOBAL_VARIABLES,
    LEN_XX_LONG,
    EMPTY_LIST,
    WEB,
)
from itsm.component.constants.role import PROCESSOR_CHOICES, PERSON, GENERAL
from itsm.component.constants import task as TASK_CONSTANTS
from itsm.component.constants.trigger import (
    SOURCE_TASK,
    CREATE_TASK,
    DELETE_TASK,
    BEFORE_START_TASK,
    AFTER_FINISH_TASK,
    AFTER_CONFIRM_TASK,
)
from itsm.component.exceptions import ComponentCallError
from itsm.component.utils.basic import now, dotted_name, list_by_separator
from itsm.component.utils.misc import (
    get_field_display_value,
    set_field_value,
    transform_username,
    get_field_value,
)
from itsm.role.models import UserRole, BKUserRole
from itsm.workflow.models import BaseField, TaskSchema
from itsm.trigger.signal import trigger_signal

logger = logging.getLogger("celery")


class TaskManager(managers.Manager):
    def set_activity_id(self, ticket_id, tasks):
        """写入任务的pipeline节点ID"""
        task_objs = self.filter(ticket_id=ticket_id)
        for task_obj in task_objs:
            task_obj.activity_id = tasks.get(task_obj.id, EMPTY_DICT).get(
                "unique_id", EMPTY_STRING
            )

        bulk_update(task_objs, update_fields=["activity_id"])

    def get_tasks(self, queryset, **kwargs):
        """查询任务"""
        username = kwargs.get("username")

        if username:
            role_filter = self.build_todo_role_filter(username)
            return queryset.filter(role_filter)

        return queryset

    @staticmethod
    def build_todo_role_filter(username):
        """processors的列表为混合内容，比如
        node1: GENERAL 1,2,3
        node2: PERSON zhangsan,lisi
        node3: Organization 1,2,3
        -> ,1,2,3,zhangsan,lisi,4,5,O_1,O_2,O_3,
        """
        dotted_username = dotted_name(username)

        # PERSON
        filters = [Q(processors__contains=dotted_username)]

        # GENERAL
        for role in UserRole.get_general_role_by_user(dotted_username):
            filters.append(Q(processors__contains=dotted_name(role["id"])))

        # ORGANIZATION
        bk_user_roles = BKUserRole.get_or_update_user_roles(username)
        for organization_id in bk_user_roles["organization"]:
            filters.append(
                Q(processors__contains=dotted_name("O_{}".format(organization_id)))
            )

        return reduce(filter_operator.or_, filters)


class Task(Model):
    """
    任务模型
    """

    ticket_id = models.IntegerField(_("单据ID"), default=0)
    state_id = models.IntegerField(_("节点ID"), default=0)
    activity_id = models.CharField(_("Pipeline节点ID"), max_length=LEN_NORMAL, blank=True)
    name = models.CharField(_("任务的名称"), max_length=LEN_LONG)
    task_schema_id = models.IntegerField(_("对应的任务模板ID"), null=False)
    component_type = models.CharField(
        _("任务组件类型"),
        choices=TASK_CONSTANTS.TASK_COMPONENT_CHOICE,
        max_length=LEN_NORMAL,
        null=False,
    )
    processors_type = models.CharField(
        _("处理人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )
    processors = models.CharField(
        _("处理人列表"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )
    inputs = jsonfield.JSONField(
        _("组件输入信息"), help_text=_("当前组件输入参数引用的参数变量"), default=EMPTY_DICT
    )
    outputs = jsonfield.JSONField(
        _("组件输出信息"), help_text=_("当前组件输出信息，比如sops各阶段返回"), default=EMPTY_DICT
    )

    order = models.IntegerField(_("任务的执行顺序"), default=1)
    status = models.CharField(
        _("任务的状态"),
        max_length=LEN_NORMAL,
        choices=TASK_CONSTANTS.TASK_STATUS_CHOICE,
        default="NEW",
    )

    executor = models.CharField(_("处理人"), max_length=LEN_NORMAL, default=EMPTY_STRING)
    confirmer = models.CharField(_("确认人"), max_length=LEN_NORMAL, default=EMPTY_STRING)
    start_at = models.DateTimeField(_("开始执行的时间"), null=True)
    end_at = models.DateTimeField(_("结束执行的时间"), null=True)
    pipeline_data = jsonfield.JSONField(_("Pipeline流程树元数据"), default=EMPTY_DICT)
    execute_state_id = models.IntegerField(_("执行节点ID"), default=0)

    objects = TaskManager()

    class Meta:
        verbose_name = _("子任务")
        verbose_name_plural = _("子任务")
        ordering = ("-id",)

    def __unicode__(self):
        return "{}({})".format(self.name, self.component_type)

    @property
    def ticket(self):
        from itsm.ticket.models import Ticket

        return Ticket._objects.get(id=self.ticket_id)

    @property
    def task(self):
        return SopsTask._objects.get(task_id=self.id)

    @property
    def component_type_display(self):
        return self.get_component_type_display()

    @property
    def status_display(self):
        return self.get_status_display()

    @property
    def can_start_sops_task(self):
        """SOPS任务启动控制
        未创建、新建或启动失败时，可启动任务
        """

        try:
            return self.task.can_start
        except SopsTask.DoesNotExist:
            # NOT-CREATED
            return True

    @property
    def processor_users(self):
        """获取任务的所有处理人(平铺式)"""
        user_list = self.processor_user_list
        return transform_username(user_list)

    @cached_property
    def processor_user_list(self):
        """任务的所有处理人列表"""
        return UserRole.get_users_by_type(
            self.ticket.bk_biz_id, self.processors_type, self.processors, self.ticket
        )

    @property
    def error_message(self):
        return self.outputs.get("error_message", "--")

    def can_process(self, username):
        """是否具有处理的权限"""

        is_processor = username in self.processor_user_list

        if (
            self.status == TASK_CONSTANTS.WAITING_FOR_OPERATE
            and self.component_type == TASK_CONSTANTS.SOPS_TASK
        ):
            return is_processor and self.can_start_sops_task

        return is_processor

    def create_task_fields(self, fields):
        """
        任务创建后的动作：
            创建各阶段字段，并填充用户提交的字段值或默认值
        """
        task_field_instances = []
        for field in self.task_schema.all_fields.all():
            field_data = field.tag_data(exclude=["task_schema", "id"])
            field_data.update(task=self)

            if field_data["stage"] == TASK_CONSTANTS.CREATE:
                # 填充`创建任务`前端提交的字段
                field_data.update(value=fields.get(field_data["key"], ""))
            else:
                # 填充默认值
                if field_data["default"]:
                    field_data.update(value=field_data["default"])

            task_field_instances.append(TaskField(**field_data))
        TaskField.objects.bulk_create(task_field_instances)

    def do_after_create(self, fields):
        self.create_task_fields(fields)
        self.send_trigger_signal(CREATE_TASK, context={"operator": self.creator})

    def do_before_delete(self, operator):
        self.send_trigger_signal(DELETE_TASK, context={"operator": operator})

    @property
    def operator(self):
        return self.updated_by

    @property
    def sops_step_list(self):
        return self.outputs.get("sops_step_list", [])

    def get_output_context(self, format="list"):
        """获取变量输出上下文"""

        # 任务全局
        context = [
            {"key": _field.key, "value": _field.value}
            for _field in self.all_fields.filter(is_deleted=False)
        ]
        start_from = len("task_")
        context.extend(
            [
                {"key": var["key"], "value": getattr(self, var["key"][start_from:], "")}
                for var in TASK_GLOBAL_VARIABLES
            ]
        )

        # 单据全局
        start_from = len("ticket_")
        context.extend(
            [
                {
                    "key": var["key"],
                    "value": getattr(self.ticket, var["key"][start_from:], ""),
                }
                for var in TICKET_GLOBAL_VARIABLES
            ]
        )

        # 额外
        if self.component_type == TASK_CONSTANTS.SOPS_TASK:
            context.append(
                {"key": "sops_relate_id", "value": self.ticket.sops_relate_id}
            )

        # 格式调整
        if format == "dict":
            return {item["key"]: item["value"] for item in context}

        return context

    def get_task_status(self):
        try:
            if self.component_type == TASK_CONSTANTS.SOPS_TASK:
                sops_task = SopsTask.objects.get(task_id=self.id)
                return sops_task.get_status()
            elif self.component_type == TASK_CONSTANTS.DEVOPS_TASK:
                sub_task = SubTask.objects.get(task_id=self.id)
                return sub_task.get_status()

        except (SopsTask.DoesNotExist, SubTask.DoesNotExist):
            return None

    @classmethod
    def sync_sops_tasks_status(cls, task_ids):
        from itsm.task.tasks import sops_task_poller

        try:
            sops_task_poller(task_ids)
        except Exception as err:
            logger.exception("sync sops tasks status failed, msg is {}".format(err))

    @classmethod
    def sync_devops_tasks_status(cls, task_ids):
        from itsm.task.tasks import devops_task_poller

        try:
            devops_task_poller(task_ids)
        except Exception as err:
            logger.exception("devops sops tasks status failed, msg is {}".format(err))

    @classmethod
    def sync_tasks_status(cls, ticket_id):
        type_dict = {
            "SOPS": cls.sync_sops_tasks_status,
            "DEVOPS": cls.sync_devops_tasks_status,
        }
        for component_type, func in type_dict.items():
            task_ids = cls.objects.filter(
                ticket_id=ticket_id, component_type=component_type
            ).values_list("id", flat=True)
            func(task_ids)

    def send_trigger_signal(self, signal, sender=None, context=None):
        from itsm.iadmin.utils import is_trigger_switch_off

        if is_trigger_switch_off():
            # 如果触发器关闭的话，直接返回
            return

        if not isinstance(context, dict):
            context = {}

        context.update(
            {item["key"]: item["value"] for item in self.get_output_context()}
        )

        trigger_signal.send(
            signal,
            sender=sender,
            source_type=SOURCE_TASK,
            source_id=self.id,
            context=context or EMPTY_DICT,
            rule_source_id=self.task_schema_id,
            rule_source_type=SOURCE_TASK,
        )

    def do_before_enter_task(self, **kwargs):
        """进入任务前的准备动作
        1. 更新任务状态、开始执行的时间
        """
        self.set_status(TASK_CONSTANTS.WAITING_FOR_OPERATE, "system")
        self.update_task_processors()
        self.send_trigger_signal(BEFORE_START_TASK)

        # self.ticket.flow.get_execute_by_create(self.state_id, self.task_schema_id)
        # 任务待处理通知
        self.ticket.notify(
            self.execute_state_id,
            ",".join(self.processor_user_list),
            _("您收到一个单据任务，请及时处理"),
            action=TASK_CONSTANTS.WAITING_FOR_OPERATE,
            retry=False,
            task_id=self.id,
        )

    @share_lock()
    def update_task_processors(self):
        from itsm.ticket.models import Ticket

        operators = []
        if self.processors_type == PERSON:
            operators.extend(self.processor_user_list)
        elif self.processors_type == GENERAL:
            operators.extend(list_by_separator(self.processors))

        task_processors = self.ticket.current_task_processors.strip(",")
        if task_processors:
            operators.extend(task_processors.split(","))

        Ticket.objects.filter(id=self.ticket_id).update(
            current_task_processors=dotted_name(",".join(set(operators)))
        )

    def do_after_finish_operate(self, **kwargs):
        """
        处理操作结束之后过程
        """
        operator = kwargs.get("operator", "")
        self.set_status(TASK_CONSTANTS.WAITING_FOR_CONFIRM, operator=operator)
        # self.ticket.flow.get_execute_by_create(self.state_id, self.task_schema_id),
        self.ticket.notify(
            self.execute_state_id,
            ",".join(self.processor_user_list),
            _("您收到一个单据总结任务，请及时处理"),
            action=TASK_CONSTANTS.WAITING_FOR_CONFIRM,
            retry=False,
            task_id=self.id,
        )
        self.send_trigger_signal(AFTER_FINISH_TASK, context={"operator": operator})

    def do_after_finish_confirm(self, **kwargs):
        """
        完成总结之后的操作
        """
        operator = kwargs.get("operator", "")

        self.set_status(TASK_CONSTANTS.FINISHED, operator=operator)

        self.send_trigger_signal(AFTER_CONFIRM_TASK, context={"operator": operator})

        self.start_next_order()

    def start_next_order(self):
        from itsm.task.backend import TaskPipelineWrapper

        unfinished_order_task = Task.objects.filter(
            ticket_id=self.ticket_id,
            order=self.order,
            state_id=self.state_id,
            status__in=TASK_CONSTANTS.ACTIVE_TASK_STATUS,
        ).exists()
        if not unfinished_order_task:
            order_list = Task.objects.filter(
                ticket_id=self.ticket_id,
                order__gt=self.order,
                status__in=[TASK_CONSTANTS.WAITING_FOR_OPERATE, TASK_CONSTANTS.QUEUE],
            ).values_list("order")
            if order_list:
                sorted_id = sorted(set([obj[0] for obj in order_list]))
                task_objs = Task.objects.filter(
                    ticket_id=self.ticket_id, state_id=self.state_id, order=sorted_id[0]
                )
                for obj in task_objs:
                    task_pipeline_wrapper = TaskPipelineWrapper(self.ticket_id, obj.id)
                    task_pipeline_wrapper.start_pipeline(obj.pipeline_data)

    def do_before_exit_task(self, operator, source=WEB):
        """退出任务的准备动作"""
        # 新建操作日志
        from itsm.ticket.models import TicketEventLog, Ticket

        ticket = Ticket.objects.get(id=self.ticket_id)
        # state_id = self.ticket.flow.get_execute_by_create(self.state_id, self.task_schema_id)
        state = ticket.state(self.execute_state_id)
        message = "{} 处理【{}】任务.".format(operator, self.name)
        TicketEventLog.objects.create_log(
            ticket,
            self.execute_state_id,
            operator,
            message=message,
            action="提交",
            from_state_name=state.get("name"),
            source=source,
        )

    def operate_sops_task(self, **kwargs):
        """执行标准运维任务"""
        fields = kwargs.get("fields", [])
        for field in fields:
            operate_field = self.operate_fields.get(key=field["key"])
            operate_field.value = field["value"]
            operate_field.save()

        sops_task = SopsTask.objects.get(ticket_id=self.ticket_id, task_id=self.id)

        operator = kwargs.get("operator", "")

        self.claim_sops_task(sops_task.sops_task_id, sops_task.bk_biz_id, operator)

        start_task_params = {
            "__raw": True,
            "task_id": sops_task.sops_task_id,
            "bk_biz_id": sops_task.bk_biz_id,
            "operator": operator,
            "username": operator,
        }

        # 创建任务 或者重试任务
        res = client_backend.sops.start_task(start_task_params)

        if not res.get("result", False):
            if sops_task:
                sops_task.state = TASK_CONSTANTS.START_FAILED
                sops_task.save()
            self.set_status(
                TASK_CONSTANTS.FAILED, operator, error_message=res.get("message", "--")
            )
            return

        sops_task.executor = operator
        sops_task.start_time = datetime.datetime.now()
        sops_task.state = TASK_CONSTANTS.RUNNING
        sops_task.save()

        self.set_status(TASK_CONSTANTS.RUNNING, operator)

    def operate_devops_task(self, **kwargs):
        """执行任务"""
        fields = kwargs.get("fields", [])
        for field in fields:
            operate_field = self.operate_fields.get(key=field["key"])
            operate_field.value = field["value"]
            operate_field.save()

        sub_task = SubTask.objects.get(ticket_id=self.ticket_id, task_id=self.id)

        operator = kwargs.get("operator", "")
        start_params = {field["key"]: field["value"] for field in fields}
        start_params.update(
            {
                "username": operator,
                "project_id": sub_task.project_id,
                "pipeline_id": sub_task.sub_pipeline_id,
            }
        )
        # 创建任务
        try:
            res = apigw_client.devops.pipeline_build_start(start_params)
        except Exception as err:
            sub_task.state = TASK_CONSTANTS.START_FAILED
            sub_task.save()
            self.set_status(TASK_CONSTANTS.FAILED, operator, error_message=err)
            return

        task_url = "/{project_id}/{sub_pipeline_id}/detail/{build_id}".format(
            **{
                "project_id": sub_task.project_id,
                "sub_pipeline_id": sub_task.sub_pipeline_id,
                "build_id": res["id"],
            }
        )
        sub_task.executor = operator
        sub_task.sub_task_id = res["id"]
        sub_task.sub_task_url = apigw_client.devops.CLIENT_URL + task_url
        sub_task.start_time = datetime.datetime.now()
        sub_task.state = TASK_CONSTANTS.RUNNING
        sub_task.save()

        self.set_status(TASK_CONSTANTS.RUNNING, operator)

    def create_task_pipeline(self, need_start=False):
        from itsm.task.backend import TaskPipelineWrapper

        task_pipeline_wrapper = TaskPipelineWrapper(self.ticket_id, self.id)
        pipeline_data = task_pipeline_wrapper.create_pipeline()
        if need_start:
            task_pipeline_wrapper.start_pipeline(pipeline_data)

    def call_sops_create_task(self, fields, operator, exclude):
        # task_prefix = 'ITSM_SOPS_TASK'
        # task_name = '{}|{}|{}'.format(task_prefix, self.id, self.name)
        task_params = {
            "__raw": True,
            "bk_biz_id": fields["bk_biz_id"],
            "operator": operator,
            "username": operator,
            "template_id": fields["id"],
            "name": self.name,
            "flow_type": "common_func",
            "template_source": fields["template_source"],
            "constants": {
                cst["key"]: cst["value"]
                for cst in fields["constants"]
                if cst["source_tag"] and cst["show_type"] != "hide"
            },
            "exclude_task_nodes_id": exclude,
        }
        res = client.sops.create_task(task_params)
        if not res.get("result", False):
            logger.error(
                "operate_sops_task->create_task failed: %s"
                % res.get("message", "unknown")
            )
            raise ComponentCallError(res)
        return res, task_params

    def claim_sops_task(self, task_id, bk_biz_id, operator):
        res = client_backend.sops.get_tasks_status(
            {"task_id_list": [task_id], "bk_biz_id": str(bk_biz_id)}
        )
        if not res or res[0].get("current_flow") != "func_claim":
            return
        data = {
            "task_id": task_id,
            "bk_biz_id": bk_biz_id,
            "name": self.name,
            "__raw": True,
        }
        res = backend_client(
            username=operator, __backend__=True
        ).sops.claim_functionalization_task(data)
        if not res.get("result", False):
            logger.error(
                "create_task->claim_task failed: %s" % res.get("message", "unknown")
            )
            raise ComponentCallError(res)

    def call_sops_update_task(self, fields, operator, task_id):
        task_params = {
            "__raw": True,
            "bk_biz_id": fields["bk_biz_id"],
            "operator": operator,
            "task_id": task_id,
            "name": self.name,
            "constants": {
                cst["key"]: cst["value"]
                for cst in fields["constants"]
                if cst["source_tag"] and cst["show_type"] != "hide"
            },
        }
        res = client.sops.modify_constants_for_task(task_params)
        if not res.get("result", False):
            logger.error(
                "operate_sops_task->modify_constants_for_task failed: %s"
                % res.get("message", "unknown")
            )
            raise ComponentCallError(res)
        return res, task_params

    def create_sops_task(self, **kwargs):
        # 不存在标准运维任务的时候，生成标准运维任务信息
        # fill task operate fields
        operator = kwargs["operator"]
        fields = kwargs["fields"]

        if kwargs["source"] == "template":
            result, task_params = self.call_sops_create_task(
                fields, operator, kwargs["exclude"]
            )
            sops_task_id = result["data"]["task_id"]
        elif kwargs["source"] == "started_task":
            task_params = {
                "__raw": True,
                "bk_biz_id": fields["bk_biz_id"],
                "operator": operator,
                "username": operator,
                "template_id": fields["id"],
                "name": self.name,
                "flow_type": "common_func",
                "template_source": fields["template_source"],
                "constants": {
                    cst["key"]: cst["value"]
                    for cst in fields["constants"]
                    if cst["source_tag"] and cst["show_type"] != "hide"
                },
                "exclude_task_nodes_id": kwargs["exclude"],
            }
            sops_task_id = fields["task_id"]
        else:
            result, task_params = self.call_sops_update_task(
                fields, operator, fields["task_id"]
            )
            sops_task_id = fields["task_id"]

        # 创建完成之后查询详情
        res = client_backend.sops.get_task_detail(
            {"__raw": True, "task_id": sops_task_id, "bk_biz_id": fields["bk_biz_id"]}
        )
        sops_task = SopsTask.objects.create(
            ticket_id=self.ticket_id,
            bk_biz_id=fields["bk_biz_id"],
            task_id=self.id,
            task_name=self.name,
            creator=self.creator,
            sops_template_id=fields["id"],
            sops_task_id=sops_task_id,
            sops_task_url=res["data"]["task_url"],
            state=TASK_CONSTANTS.CREATED,
            sops_task_info={"params": task_params, "detail": res["data"]},
        )

        return sops_task

    def create_sub_task(self, fields, operator, data):
        # 创建子任务
        if self.component_type == "SOPS":
            rendered_field = self.render_fields(fields)
            return self.create_sops_task(
                fields=rendered_field["sops_templates"],
                operator=operator,
                source=data.get("source", "template"),
                exclude=data.get("exclude_task_nodes_id", []),
            )
        elif self.component_type == "DEVOPS":
            devops_params = fields["sub_task_params"]
            sub_task = SubTask.objects.create(
                ticket_id=self.ticket_id,
                project_id=devops_params["project_id"],
                task_id=self.id,
                task_name=self.name,
                creator=self.creator,
                sub_pipeline_id=devops_params["pipeline_id"],
                state=TASK_CONSTANTS.CREATED,
            )
            return sub_task

    def render_fields(self, fields):
        rendered_field = copy.deepcopy(fields)
        outputs = self.ticket.get_ticket_global_output()
        logger.error(
            "outputs is {}, fields is {}".format(outputs, json.dumps(rendered_field))
        )
        for constant in rendered_field["sops_templates"].get("constants", []):
            if constant.get("is_quoted", False):
                constant["value"] = Template(constant["value"]).render(**outputs)
        return rendered_field

    def update_sops_task(self, **kwargs):
        operator = kwargs["operator"]
        fields = kwargs["fields"]

        sop_task = SopsTask.objects.get(ticket_id=self.ticket_id, task_id=self.id)
        # 更新
        res, task_params = self.call_sops_update_task(
            fields, operator, sop_task.sops_task_id
        )

        detail = sop_task.sops_task_info.get("detail", "")
        # 修改完成之后查询详情
        res = client_backend.sops.get_task_detail(
            {
                "__raw": True,
                "task_id": sop_task.sops_task_id,
                "bk_biz_id": fields["bk_biz_id"],
            }
        )
        if res.get("result", False):
            detail = res.get("data")

        sop_task.task_name = self.name
        sop_task.sops_task_info = {"params": task_params, "detail": detail}
        sop_task.save()

        return sop_task

    def retry_sops_task(self, sops_task, retry_operator):
        """
        重试标准运维任务
        :param sops_task: 标准任务记录信息
        :param retry_operator: 重试操作人员
        :return:
        """

        res = client_backend.sops.get_task_status(
            {
                "__raw": True,
                "task_id": sops_task.sops_task_id,
                "bk_biz_id": sops_task.bk_biz_id,
            }
        )
        if res.get("result", False) is False:
            # 获取不到标准运维任务信息，直接设置为异常
            return {
                "result": False,
                "message": "重试失败，获取标准运维任务信息出错 %s" % res.get("message", ""),
            }

        failed_nodes = [
            node_id
            for node_id, node_info in res["data"]["children"].items()
            if node_info["state"] == TASK_CONSTANTS.FAILED
        ]
        if not failed_nodes:
            # 不存在失败节点的时候，说明任务成功执行了
            return {"result": True, "message": u"重试成功，标准运维任务已经在执行中"}

        for node_id in failed_nodes:
            # 依次进行重试，除了并行节点，一般只会有一个错误的id
            operate_res = client.sops.operate_node(
                {
                    "__raw": True,
                    "username": retry_operator,
                    "operator": retry_operator,
                    "bk_biz_id": sops_task.bk_biz_id,
                    "task_id": sops_task.sops_task_id,
                    "node_id": node_id,
                    "action": "retry",
                }
            )
            if operate_res.get("result"):
                continue
        return operate_res

    def operate_normal_task(self, **kwargs):
        """处理普通任务"""
        with transaction.atomic():
            # fill task operate fields
            fields = kwargs.pop("fields", [])
            for field in fields:
                operate_field = self.operate_fields.get(key=field["key"])
                operate_field.value = field["value"]
                operate_field.save()

        self.do_after_finish_operate(**kwargs)

    def skip_normal_task(self, **kwargs):
        """忽略普通任务"""
        self.do_after_finish_operate(**kwargs)

    def skip_sops_task(self, **kwargs):
        """忽略标准运维任务"""
        self.do_after_finish_operate(**kwargs)

    def confirm_task(self, **kwargs):
        """总结普通任务"""
        with transaction.atomic():
            # fill task confirm fields
            fields = kwargs.pop("fields", [])
            for field in fields:
                confirm_field = self.confirm_fields.get(key=field["key"])
                confirm_field.value = field["value"]
                confirm_field.save()

        self.do_after_finish_confirm(**kwargs)

    def set_status(self, status, operator="", **kwargs):
        """设置任务状态，并更新处理人"""

        self.status = status
        if operator:
            self.updated_by = operator
        self.outputs.update(error_message=kwargs.get("error_message", ""))

        if status == TASK_CONSTANTS.WAITING_FOR_OPERATE:
            self.start_at = now()
        elif status == TASK_CONSTANTS.FINISHED:
            self.end_at = now()

        self.save(
            update_fields=["outputs", "status", "updated_by", "start_at", "end_at"]
        )

    def update_executor_status(self, username, status):
        self.ticket.add_history_task_processors(username)
        self.status = status
        self.executor = username
        self.save(update_fields=["executor", "status"])

    def activity_callback(self, action, fields, operator, is_finished=False):
        """任务节点回调
        :param action: operate 处理动作, confirm 总结动作
        :param fields: 任务字段列表
        :param operator: 操作者
        :param is_finished: 任务节点的生命周期是否结束
        """
        return pipeline_api.activity_callback(
            self.activity_id,
            {
                "task_id": self.id,
                "action": action,
                "operator": operator,
                "fields": fields,
                "is_finished": is_finished,
            },
        )

    @property
    def task_schema(self):
        return TaskSchema.objects.get(id=self.task_schema_id)

    @property
    def create_fields(self):
        return TaskField.objects.filter(
            task_id=self.id, stage=TASK_CONSTANTS.CREATE
        ).order_by("sequence")

    @property
    def operate_fields(self):
        return TaskField.objects.filter(
            task_id=self.id, stage=TASK_CONSTANTS.OPERATE
        ).order_by("sequence")

    @property
    def confirm_fields(self):
        return TaskField.objects.filter(
            task_id=self.id, stage=TASK_CONSTANTS.CONFIRM
        ).order_by("sequence")


class TaskField(BaseField):
    """任务对应的表单字段"""

    task = models.ForeignKey(
        Task,
        help_text=_("对应的任务模型"),
        related_name="all_fields",
        on_delete=models.CASCADE,
    )
    stage = models.CharField(
        _("所处阶段"),
        choices=TASK_CONSTANTS.TASK_STAGE_CHOICE,
        max_length=LEN_NORMAL,
        default="CREATE",
    )
    sequence = models.IntegerField(_("序号"), default=0)
    _value = models.TextField(_("表单值"), null=True, blank=True)

    class Meta:
        verbose_name = _("任务字段表")
        verbose_name_plural = _("任务字段表")
        ordering = ("-id",)

    def __unicode__(self):
        return "{}({})".format(self.name, self.task.name)

    @property
    def display_value(self):
        """根据_value是否有值对其进行转换"""
        return get_field_display_value(self)

    @property
    def value(self):
        """
        根据type转换_value并返回
        """
        return get_field_value(self)

    @value.setter
    def value(self, v):
        """
        保存时自动根据类型做转换
        """
        set_field_value(self, v)

    @property
    def show_result(self):
        return True


class SopsTask(Model):
    """
    标准运维任务模型
    {
            "id": 30000105,
            "name": "task test tree",
            "status": {
                "id": "n580c9bf42a93bfc9a6cfe309bb3b418",
                "state": "FINISHED",
                "name": "<class 'pipeline.core.pipeline.Pipeline'>",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "",
                "elapsed_time": 41,
                "start_time": "2020-03-18 17:22:05 +0800",
                "finish_time": "2020-03-18 17:22:46 +0800"
            },
            "create_time": "2020-03-18 17:21:24 +0800",
            "start_time": "2020-03-18 17:22:04 +0800",
            "finish_time": "2020-03-18 17:22:46 +0800",
            "url": "https://paasee.xx.com/taskflow/execute/13/?instance_id=30000105"
        }
    """

    ticket_id = models.IntegerField(_("单据ID"))
    bk_biz_id = models.IntegerField(_("业务ID"), default=-1)
    task_id = models.CharField(_("itsm任务ID"), max_length=LEN_NORMAL)
    task_name = models.CharField(_("任务的名称"), max_length=LEN_LONG)
    sops_template_id = models.IntegerField(_("sops任务模板ID"))
    sops_task_id = models.IntegerField(_("sops任务ID，成功启动后填充"), null=True, blank=True)
    # params|detail|status
    sops_task_info = jsonfield.JSONField(_("sops任务信息"), default=EMPTY_DICT)
    sops_task_url = models.CharField(
        _("sops任务详情链接，成功启动后填充"), max_length=LEN_LONG, null=True, blank=True
    )

    creator = models.CharField(_("创建者"), max_length=LEN_NORMAL, blank=True)
    executor = models.CharField(_("执行者"), max_length=LEN_NORMAL, blank=True)
    create_time = models.DateTimeField(_("创建时间"), auto_now_add=True)
    start_time = models.DateTimeField(_("启动时间"), null=True, blank=True)
    finish_time = models.DateTimeField(_("结束时间"), null=True, blank=True)
    elapsed_time = models.IntegerField(_("当前耗时"), default=EMPTY_INT)
    state = models.CharField(
        _("任务状态"),
        max_length=LEN_NORMAL,
        choices=TASK_CONSTANTS.SOPS_TASK_STATE_CHOICE,
        default=TASK_CONSTANTS.NOT_CREATED,
    )

    def __str__(self):
        return "{}-{}:{}".format(self.task_id, self.task_name, self.state)

    @property
    def task(self):
        return Task._objects.get(id=self.task_id)

    @property
    def bk_biz_name(self):
        apps = get_biz_names()
        return apps.get(str(self.bk_biz_id))

    @property
    def can_start(self):
        return self.state in [TASK_CONSTANTS.CREATED, TASK_CONSTANTS.START_FAILED]

    def get_status(self):
        from itsm.task.tasks import sops_task_poller

        # 未结束任务先同步，后返回
        if (
            self.state == TASK_CONSTANTS.RUNNING
            or self.task.status not in TASK_CONSTANTS.END_TASK_STATUS
        ):
            sops_task_poller([self.task_id])
            self.refresh_from_db()

        return {
            "bk_biz_id": "{}（ID: {}）".format(self.bk_biz_name, self.bk_biz_id),
            "creator": self.creator,
            "executor": self.executor,
            "sops_task_id": self.sops_task_id,
            "task_name": self.task_name,
            "sops_task_url": self.sops_task_url,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.start_time
            else "",
            "finish_time": self.finish_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.finish_time
            else "",
            "elapsed_time": self.elapsed_time,
            "state": self.state,
        }

    class Meta:
        verbose_name = _("标准运维任务")
        verbose_name_plural = _("标准运维任务")
        ordering = ("-id",)


class SubTask(Model):
    """
    子任务模型
    """

    ticket_id = models.IntegerField(_("单据ID"))
    project_id = models.CharField(_("项目ID/业务ID"), default="", max_length=LEN_NORMAL)
    task_id = models.CharField(_("itsm任务ID"), max_length=LEN_NORMAL)
    task_name = models.CharField(_("任务的名称"), max_length=LEN_LONG)
    sub_pipeline_id = models.CharField(_("子流水线ID"), max_length=LEN_NORMAL)
    sub_task_id = models.CharField(
        _("子ID，成功启动后填充"), null=True, blank=True, max_length=LEN_NORMAL
    )
    sub_task_info = jsonfield.JSONField(_("子任务信息"), default=EMPTY_DICT)
    sub_task_url = models.CharField(
        _("子任务详情链接"), max_length=LEN_LONG, null=True, blank=True
    )
    creator = models.CharField(_("创建者"), max_length=LEN_NORMAL, blank=True)
    executor = models.CharField(_("执行者"), max_length=LEN_NORMAL, blank=True)
    create_time = models.DateTimeField(_("创建时间"), auto_now_add=True)
    start_time = models.DateTimeField(_("启动时间"), null=True, blank=True)
    finish_time = models.DateTimeField(_("结束时间"), null=True, blank=True)
    elapsed_time = models.IntegerField(_("当前耗时"), default=EMPTY_INT)
    state = models.CharField(
        _("任务状态"),
        max_length=LEN_NORMAL,
        choices=TASK_CONSTANTS.DEVOPS_TASK_STATE_CHOICE,
        default=TASK_CONSTANTS.NOT_CREATED,
    )

    def __str__(self):
        return "{}-{}:{}".format(self.task_id, self.task_name, self.state)

    @property
    def task(self):
        return Task._objects.get(id=self.task_id)

    def get_status(self):
        from itsm.task.tasks import devops_task_poller

        devops_task_poller([self.task_id])
        self.refresh_from_db()

        return {
            "project_id": self.project_id,
            "creator": self.creator,
            "executor": self.executor,
            "sub_task_id": self.sub_task_id,
            "task_name": self.task_name,
            "sub_task_url": self.sub_task_url,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.start_time
            else "",
            "finish_time": self.finish_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.finish_time
            else "",
            "elapsed_time": self.elapsed_time,
            "state": self.state,
            "sub_pipeline_id": self.sub_pipeline_id,
            "task_schema_id": self.task.task_schema_id,
        }

    class Meta:
        verbose_name = _("子任务")
        verbose_name_plural = _("子任务")
        ordering = ("-id",)


class TaskLib(Model):
    """任务库"""

    service_id = models.IntegerField(_("服务ID"))
    name = models.CharField(_("任务库名称"), max_length=LEN_NORMAL)

    class Meta:
        verbose_name = _("任务库")
        verbose_name_plural = _("任务库")
        ordering = ("-id",)

    def create_lib_tasks(self, task_id_list):
        from itsm.task.serializers import TaskFieldSerializer

        lib_tasks = []
        for task_id in task_id_list:
            task = Task.objects.get(id=task_id)
            task_info = {
                "task_lib": self,
                "name": task.name,
                "task_schema_id": task.task_schema_id,
                "component_type": task.component_type,
                "processors_type": task.processors_type,
                "processors": task.processors,
                "fields": TaskFieldSerializer(task.create_fields, many=True).data,
            }
            if task.component_type == TASK_CONSTANTS.SOPS_TASK:
                sub_task = SopsTask.objects.get(task_id=task_id)
                task_info["sub_template_id"] = sub_task.sops_template_id
                task_info["project_id"] = sub_task.bk_biz_id
                task_info["exclude_task_nodes"] = sub_task.sops_task_info["params"].get(
                    "exclude_task_nodes_id", []
                )
            if task.component_type == TASK_CONSTANTS.DEVOPS_TASK:
                sub_task = SubTask.objects.get(task_id=task_id)
                task_info["sub_template_id"] = sub_task.sub_pipeline_id
                task_info["project_id"] = sub_task.project_id
            lib_tasks.append(TaskLibTasks(**task_info))

        TaskLibTasks.objects.bulk_create(lib_tasks)


class TaskLibTasks(Model):
    task_lib = models.ForeignKey(
        TaskLib,
        help_text=_("关联的任务库"),
        related_name="lib_tasks",
        on_delete=models.CASCADE,
    )
    name = models.CharField(_("任务名称"), max_length=LEN_NORMAL)
    task_schema_id = models.CharField(_("任务模版ID"), max_length=LEN_NORMAL)
    component_type = models.CharField(_("任务类型"), max_length=LEN_NORMAL)
    processors_type = models.CharField(_("处理人类型"), max_length=LEN_NORMAL)
    processors = models.CharField(_("处理人"), max_length=LEN_LONG)
    fields = jsonfield.JSONField(_("字段列表"), max_length=LEN_XX_LONG, default=EMPTY_LIST)
    sub_template_id = models.CharField(_("子模版ID"), default="", max_length=LEN_NORMAL)
    project_id = models.CharField(_("项目ID/业务ID"), default="", max_length=LEN_NORMAL)
    exclude_task_nodes = jsonfield.JSONField(
        _("排除节点ID列表"), max_length=LEN_LONG, default=EMPTY_LIST
    )

    class Meta:
        verbose_name = _("任务库任务列表")
        verbose_name_plural = _("任务库任务列表")

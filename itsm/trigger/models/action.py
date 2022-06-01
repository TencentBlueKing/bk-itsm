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

import traceback
from datetime import datetime

import jsonfield

from django.db import models
from django.utils.translation import ugettext as _
from mako.template import Template

from itsm.component.utils.client_backend_query import get_bk_users
from itsm.component.constants import (
    SYS,
    LEN_NORMAL,
    LEN_MIDDLE,
    EMPTY_DICT,
    EMPTY_STRING,
    ACTION_STATUS_CHOICE,
    TRIGGER_SIGNAL,
    EMPTY_INT,
    TRIGGER_SIGNAL_CHOICE,
    EMPTY_DISPLAY_STRING,
)
from itsm.trigger.managers import ActionManagers
from .trigger import ActionSchema, Trigger, TriggerRule
from .base import Model as TriggerBaseModel


class Action(TriggerBaseModel):
    """响应事件实例"""

    FIELDS = (
        "sender",
        "signal_type",
        "display_name",
        "source_type",
        "source_id",
        "inputs",
        "id",
        "status",
        "status_name",
        "operator",
        "operator_username",
        "can_repeat",
        "need_refresh",
        "component_name",
        "end_time",
        "ex_data",
        "component_type",
    )

    signal = models.CharField(
        _("触发事件信号"), choices=TRIGGER_SIGNAL_CHOICE, max_length=LEN_MIDDLE
    )
    sender = models.CharField(
        _("触发对象"), help_text=_("一般为触发该信号的元素id"), max_length=LEN_NORMAL
    )
    rule_id = models.IntegerField(_("事件关联的触发器规则信息"), default=EMPTY_INT)
    trigger_id = models.IntegerField(_("事件关联的触发器信息"), default=EMPTY_INT)
    schema_id = models.IntegerField(_("事件关联的配置信息"))

    # 真正处罚对象的来源, 可以根据用户的需要来定义
    source_type = models.CharField(
        _("响应事件来源类型"),
        help_text=_("记录响应事件的来源类型, 由用户自定义，方便使用方后期管理"),
        max_length=LEN_NORMAL,
        default=EMPTY_STRING,
    )
    source_id = models.IntegerField(_("对应的来源PK值"), null=True, blank=True)

    context = jsonfield.JSONField(_("触发事件的上下文参数"), default=EMPTY_DICT)
    inputs = jsonfield.JSONField(
        _("用户的输入参数"), help_text=_("输入参数引用的参数变量"), default=EMPTY_DICT
    )
    outputs = jsonfield.JSONField(
        _("动作的输出参数"), help_text=_("动作的输出参数字典"), default=EMPTY_DICT
    )

    # 事件的执行状态
    status = models.CharField(
        _("响应事件状态"),
        choices=ACTION_STATUS_CHOICE,
        default="CREATED",
        max_length=LEN_NORMAL,
    )
    end_time = models.DateTimeField(_("任务结束事件"), null=True)
    operator = models.CharField(_("执行人"), max_length=LEN_NORMAL, default=SYS)
    ex_data = jsonfield.JSONField(
        _("执行错误信息"), help_text=_("状态为失败的时候记录的错误日志"), default=EMPTY_DICT
    )

    params = jsonfield.JSONField(_("执行的参数"), help_text=_("手动触发器实际执行的参数信息"), default={})

    objects = ActionManagers()

    temporary_params = None

    class Meta:
        verbose_name = _("响应动作表")
        verbose_name_plural = _("响应动作表")
        ordering = ("-id",)

    def __unicode__(self):
        return "{}({})".format(self.name, self.component_type)

    def execute(self, operator=SYS, need_update_context=False):
        """
        # 任务执行的接口
        """
        self.status = "RUNNING"
        self.operator = operator
        if self.action_schema.can_repeat:
            self.id = None
        self.save()
        self.refresh_from_db(fields=["id"])

        if need_update_context:
            self.update_context()
        try:
            self.component_obj.run()
        except BaseException:
            error_message = traceback.format_exc()
            self.set_finished(False, error_message)

    def update_context(self):
        """
        跟新上下文信息
        """
        self.context = self.component_obj.update_context()
        self.save(update_fields=["context"])

    def set_finished(self, result, ex_data, outputs=None):

        self.status = "SUCCEED" if result else "FAILED"
        self.end_time = datetime.now()
        if outputs is not None:
            self.outputs = outputs
        if self.ex_data and isinstance(self.ex_data, list):
            self.ex_data.append({"result": result, "message": ex_data})
        else:
            self.ex_data = [{"result": result, "message": ex_data}]
        self.save(update_fields=("status", "ex_data", "end_time", "outputs"))

    def get_fields(self, flat=False):
        return self.component_obj.to_representation_data(flat=flat)

    @property
    def fields(self):
        return self.get_fields()

    @property
    def component_obj(self):
        self.context.update(self.outputs if self.outputs else EMPTY_DICT)
        if self.params:
            return self.action_schema.component_class(
                self.context, self.params, self.id, self.count_down
            )
        return self.action_schema.component_class(
            self.context, self.action_schema.params, self.id, self.count_down
        )

    @property
    def count_down(self):
        if self.action_schema.delay_params["type"] == "custom":
            return int(self.action_schema.delay_params["value"])
        else:
            return int(self.context.get(self.action_schema.delay_params["value"], 0))

    @property
    def action_schema(self):
        return ActionSchema.objects.get(id=self.schema_id)

    @property
    def operate_type(self):
        return self.action_schema.get_operate_type_display()

    def render_params(self, template_value):
        try:
            if isinstance(template_value, str):
                return Template(template_value).render(**self.context)
            if isinstance(template_value, dict):
                render_value = {}
                for key, value in template_value.items():
                    render_value[key] = self.render_params(value)
                return render_value
            if isinstance(template_value, list):
                return [self.render_params(value) for value in template_value]
        except NameError:
            return template_value
        return template_value

    def action_params(self, context):
        self.update_context()
        self.context.update(context)
        return self.render_params(self.action_schema.params)

    @property
    def trigger_name(self):
        try:
            trigger = Trigger.objects.get(id=self.trigger_id)
        except Trigger.DoesNotExist:
            return "None"
        return trigger.name

    @property
    def rule_name(self):
        try:
            rule = TriggerRule.objects.get(id=self.trigger_id)
        except Trigger.DoesNotExist:
            return "None"
        return rule.name

    @property
    def display_name(self):
        return self.action_schema.display_name

    @property
    def can_repeat(self):
        return self.action_schema.can_repeat

    @property
    def status_name(self):
        return self.get_status_display()

    @property
    def signal_type(self):
        for _type, signals in TRIGGER_SIGNAL.items():
            if self.signal in signals:
                return _type
        return "Undefined"

    @property
    def signal_name(self):
        return self.get_signal_display()

    @property
    def need_refresh(self):
        return self.action_schema.component_class.need_refresh

    @property
    def component_type(self):
        return self.action_schema.component_type

    @property
    def component_name(self):
        return self.action_schema.component_class.name

    @property
    def operator_username(self):
        if not self.operator:
            return EMPTY_DISPLAY_STRING
        if self.operator == SYS:
            return _("系统")
        bk_users = get_bk_users(format="dict", users=[self.operator])
        return bk_users.get(self.operator, EMPTY_DISPLAY_STRING)

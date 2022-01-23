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
from itertools import chain
from django.db import models
from django.utils.translation import ugettext as _
import jsonfield

from itsm.component.dlls.component import ComponentLibrary
from itsm.component.constants import (
    LEN_NORMAL,
    LEN_MIDDLE,
    LEN_LONG,
    LEN_X_LONG,
    EMPTY_DICT,
    EMPTY_LIST,
    EMPTY_STRING,
    EMPTY_INT,
    OPT_TYPE_CHOICE,
    TRIGGER_SOURCE_TYPE,
    TRIGGER_ICON_CHOICE,
    TRIGGER_SIGNAL,
    LEN_SHORT,
)
from .base import Model as TriggerBaseModel
from ...project.models import Project


class ActionSchema(TriggerBaseModel):
    """
    响应动作的参数配置
    """

    FIELDS = (
        "id",
        "name",
        "display_name",
        "component_type",
        "operate_type",
        "can_repeat",
        "params",
        "inputs",
        "delay_params",
    )

    name = models.CharField(_("动作模版的名称"), max_length=LEN_LONG)
    display_name = models.CharField(_("动作显示名称"), max_length=LEN_LONG, null=True)
    component_type = models.CharField(_("组件类型"), max_length=LEN_LONG)

    operate_type = models.CharField(
        _("操作方式"), choices=OPT_TYPE_CHOICE, max_length=LEN_NORMAL, default="BACKEND"
    )
    delay_params = jsonfield.JSONField(
        _("延迟参数"), default={"type": "custom", "value": 0}
    )
    can_repeat = models.BooleanField(_("是否可以重复执行"), default=False)

    params = jsonfield.JSONField(_("配置参数"), help_text=_("当前响应事件配置的参数模版"), default={})
    inputs = jsonfield.JSONField(_("输入参数"), help_text=_("输入参数引用的参数变量"), default={})

    class Meta:
        verbose_name = _("响应动作参数配置表")
        verbose_name_plural = _("响应动作参数配置表")
        ordering = ("id",)

    def __unicode__(self):
        return "{}({})".format(self.name, self.component_type)

    @property
    def component_class(self):
        return ComponentLibrary.get_component_class(
            "trigger", component_code=self.component_type
        )

    def clone(self):
        self.id = None
        self.save()
        self.refresh_from_db()
        return self.id

    def tag_data(self):
        data = {}
        for f in chain(self._meta.concrete_fields, self._meta.private_fields):
            if not getattr(f, "editable", False):
                continue
            if isinstance(f, models.ForeignKey):
                data["{}_id".format(f.name)] = getattr(getattr(self, f.name), "id", "")
            else:
                data[f.name] = getattr(self, f.name, "")
        return data


class Trigger(TriggerBaseModel):
    """触发器"""

    FIELDS = (
        "id",
        "name",
        "desc",
        "signal",
        "sender",
        "source_type",
        "source_id",
        "source_table_id",
        "is_draft",
        "is_enabled",
        "icon",
        "project_key",
    )

    name = models.CharField(_("名称"), max_length=LEN_NORMAL)
    desc = models.CharField(_("描述信息"), max_length=LEN_X_LONG)

    signal = models.CharField(_("触发事件信号"), null=False, max_length=LEN_MIDDLE)
    sender = models.CharField(
        _("触发对象"), help_text=_("一般为触发该信号的实际对象模型id"), max_length=LEN_NORMAL
    )

    # inputs 好像暂时没需要
    inputs = jsonfield.JSONField(
        _("输入参数"), help_text=_("输入参数引用的参数变量"), default=EMPTY_LIST
    )

    # 触发器的来源, 可以根据用户的需要来定义
    source_type = models.CharField(
        _("来源类型"),
        help_text=_("触发规则的配置来源"),
        choices=TRIGGER_SOURCE_TYPE,
        max_length=LEN_NORMAL,
    )
    source_id = models.IntegerField(_("对应的来源PK值"), null=True, blank=True)

    source_table_id = models.IntegerField(_("对应的变量来源表ID"), default=EMPTY_INT)

    is_draft = models.BooleanField(_("是否为草稿"), default=True)
    is_enabled = models.BooleanField(_("是否可启用"), default=False)
    icon = models.CharField(
        _("对应的icon"), default=EMPTY_STRING, choices=TRIGGER_ICON_CHOICE, max_length=64
    )
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    need_auth_grant = True

    auth_resource = {"resource_type": "trigger", "resource_type_name": "触发器"}
    resource_operations = ["triggers_view", "triggers_manage"]

    class Meta:
        verbose_name = _("触发器")
        verbose_name_plural = _("触发器")
        ordering = ("-id",)

    def __unicode__(self):
        return "{}({}-{})".format(self.name, self.source_type, self.source_id)

    def trigger_rules(self, source_type, source_id):
        return [
            {
                "conditions": item.condition
                if item.by_condition
                else {
                    "all": [
                        {
                            "name": "constant_bool_true",
                            "operator": "is_true",
                            "value": True,
                        }
                    ]
                },
                "actions": [
                    {
                        "name": "trigger_handle",
                        "params": {
                            "rule": item,
                            "source_type": source_type,
                            "source_id": source_id,
                        },
                    }
                ],
            }
            for item in self.rules
        ]

    @property
    def rules(self):
        return TriggerRule.objects.filter(trigger_id=self.id)

    @property
    def project(self):
        return Project.objects.get(key=self.project_key)

    def clone(self, dst_source_type, dst_source_id, dst_sender=None, **kwargs):
        """
        克隆功能
        """
        self.id = None
        version_number = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.name = "{}{}".format(self.name, version_number)
        self.source_id = dst_source_id
        self.source_type = dst_source_type
        if dst_sender:
            self.sender = dst_sender

        # 覆盖属性
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.save()
        self.refresh_from_db()
        return self.id

    def tag_data(self):
        rules = []
        data = {"rules": rules}
        for rule in TriggerRule.objects.filter(trigger_id=self.id):
            rules.append(rule.tag_data())

        for f in chain(self._meta.concrete_fields, self._meta.private_fields):
            if not getattr(f, "editable", False):
                continue
            if isinstance(f, models.ForeignKey):
                data["{}_id".format(f.name)] = getattr(getattr(self, f.name), "id", "")
            else:
                data[f.name] = getattr(self, f.name, "")
        return data

    @property
    def signal_type(self):
        for _type, signals in TRIGGER_SIGNAL.items():
            if self.signal in signals:
                return _type
        return "Undefined"


class TriggerRule(TriggerBaseModel):
    """
    触发器条件与动作配置
    """

    FIELDS = ("id", "name", "condition", "action_schemas", "trigger_id", "by_condition")
    name = models.CharField(_("规则标题"), max_length=LEN_NORMAL, default="")

    condition = jsonfield.JSONField(_("触发条件"), default=EMPTY_DICT)
    by_condition = models.BooleanField(_("触发方式"), default=False)
    action_schemas = jsonfield.JSONCharField(
        _("响应事件列表"),
        help_text=_("关联事件的配置ID列表,关联actionSchema"),
        max_length=LEN_LONG,
        default=EMPTY_LIST,
    )
    trigger_id = models.IntegerField(_("对应的触发器id"), null=True)

    class Meta:
        verbose_name = _("触发器条件与动作配置")
        verbose_name_plural = _("触发器条件与动作配置")
        ordering = ("id",)

    def __unicode__(self):
        return "{}({}-{})".format(self.name, self.source_type, self.source_id)

    @property
    def actions(self):
        return ActionSchema.objects.filter(id__in=self.action_schemas)

    def tag_data(self):
        data_action_schemas = []
        for action_schema in ActionSchema.objects.filter(id__in=self.action_schemas):
            data_action_schemas.append(action_schema.tag_data())
        return dict(
            name=self.name,
            condition=self.condition,
            by_condition=self.by_condition,
            action_schemas=data_action_schemas,
        )

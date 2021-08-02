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

import jsonfield
from django.db import models
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    DEFAULT_FLOW_CONDITION,
    EMPTY_DICT,
    FLOW_CONDITION_TYPE_CHOICES,
    LEN_NORMAL,
    LEN_SHORT,
)
from itsm.workflow import managers

from .base import Model


class Condition(Model):
    """流转线条件配置"""

    workflow = models.ForeignKey('workflow.Workflow', related_name="flows", help_text=_("关联工作流"),
                                 on_delete=models.CASCADE)
    name = models.CharField(_("流转操作"), max_length=LEN_NORMAL)
    data = jsonfield.JSONField(_("流转条件表达式"), default=DEFAULT_FLOW_CONDITION)

    objects = managers.ConditionManager()

    class Meta:
        app_label = 'workflow'
        verbose_name = _("流转条件")
        verbose_name_plural = _("流转条件")

    def __unicode__(self):
        return self.name

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class Transition(Model):
    """状态流转"""

    DIRECTION_CHOICES = [
        ("BACK", '向后'),
        ("FORWARD", '向前'),
    ]

    workflow = models.ForeignKey('workflow.Workflow', related_name="transitions",
                                 help_text=_("关联流程"), on_delete=models.CASCADE)

    name = models.CharField(_("流转操作"), max_length=LEN_NORMAL)
    condition = jsonfield.JSONField(_("流转条件表达式"), default=DEFAULT_FLOW_CONDITION)
    condition_type = models.CharField(
        _("流转类型"), max_length=LEN_SHORT, choices=FLOW_CONDITION_TYPE_CHOICES, default="default"
    )

    # 线条的方向坐标 {"start":"left|right|top|bottom", "end": "left|right|top|bottom"}
    axis = jsonfield.JSONCharField(_("线条的坐标位置的坐标轴"), max_length=LEN_NORMAL, default=EMPTY_DICT)

    from_state = models.ForeignKey('workflow.State', related_name="transitions_from",
                                   help_text=_("源状态ID"), on_delete=models.CASCADE)
    to_state = models.ForeignKey('workflow.State', related_name="transitions_to",
                                 help_text=_("目标状态ID"), on_delete=models.CASCADE)

    # deprecated fields: check_needed/opt_needed
    direction = models.CharField(_("流转方向"), max_length=LEN_SHORT, choices=DIRECTION_CHOICES,
                                 default="FORWARD")
    check_needed = models.BooleanField(_("是否需要校验表单完整性"), default=True)
    opt_needed = models.BooleanField(_("是否需要执行操作"), default=True)

    is_builtin = models.BooleanField(_("是否为系统内置"), default=False)

    objects = managers.TransitionManager()
    _objects = models.Manager()

    class Meta:
        app_label = 'workflow'
        verbose_name = _("状态流转")
        verbose_name_plural = _("状态流转")

    def __unicode__(self):
        return "{} -{} {}".format(self.from_state, '>' if self.opt_needed else '-', self.to_state)

    @property
    def serialized_data(self):
        from itsm.workflow.serializers import TransitionSerializer

        return TransitionSerializer(self).data

    def delete(self, using=None):
        from itsm.workflow.models import State

        super(Transition, self).delete(using)
        State.objects.update_state_label(self.from_state, self.to_state, operate_type='delete')

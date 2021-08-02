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
    DEFAULT_STRING,
    EMPTY_DICT,
    EMPTY_INT,
    EMPTY_LIST,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_SHORT,
    NOTIFY_RULE_CHOICES,
)
from itsm.workflow import managers
from itsm.workflow.models.field import BaseField


class WorkflowSnap(models.Model):
    """实例化工作流
        废弃：迁移至WorkflowVersion
    """

    snapshot_time = models.DateTimeField(_("快照创建时间"), auto_now_add=True)

    workflow_id = models.IntegerField(_("工作流ID"))

    fields = jsonfield.JSONField(_("字段快照字典"), default=EMPTY_DICT, null=True, blank=True)
    states = jsonfield.JSONField(_("状态快照字典"), default=EMPTY_DICT, null=True, blank=True)
    transitions = jsonfield.JSONField(_("流转快照字典"), default=EMPTY_DICT, null=True, blank=True)

    # 记录主分支数据
    master = jsonfield.JSONField(_("主分支列表"), default=EMPTY_LIST, null=True, blank=True)

    notify = models.ManyToManyField('workflow.Notify', help_text=_("可关联多种通知方式"))
    notify_rule = models.CharField(_("通知规则"), max_length=LEN_SHORT, choices=NOTIFY_RULE_CHOICES, default="NONE")
    notify_freq = models.IntegerField(_("重试间隔(s)"), default=EMPTY_INT)

    objects = managers.WorkflowSnapManager()

    class Meta:
        app_label = 'workflow'
        verbose_name = _("工作流快照")
        verbose_name_plural = _("工作流快照")

    def __unicode__(self):
        return "{}({})".format(self.workflow_id, str(self.snapshot_time))


class DefaultField(BaseField):
    """初始环节内置字段表: deprecated"""

    flow_type = models.CharField(_("流程分类"), max_length=LEN_NORMAL, default=DEFAULT_STRING)
    category = models.CharField(_("字段归类，面向业务逻辑，比如服务类型（change|event）"), max_length=LEN_MIDDLE)

    objects = models.Manager()

    class Meta:
        app_label = "workflow"
        verbose_name = _("内置字段表")
        verbose_name_plural = _("内置字段表")

    def __unicode__(self):
        return "{}({})".format(self.name, self.type)

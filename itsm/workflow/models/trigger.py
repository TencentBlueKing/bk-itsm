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

from itsm.component.constants import EMPTY_DICT, LEN_LONG, LEN_NORMAL, LEN_SHORT, TRIGGER_TYPE
from itsm.workflow.managers import TriggerManager
from itsm.workflow.models import Model


class Trigger(Model):
    name = models.CharField(_("名称"), max_length=LEN_NORMAL)
    component_key = models.CharField(_("原子key"), max_length=LEN_NORMAL)
    type = models.CharField(_("类型"), max_length=LEN_SHORT, choices=TRIGGER_TYPE)
    condition = jsonfield.JSONCharField(_("触发条件"), max_length=LEN_LONG, default=EMPTY_DICT)
    inputs = jsonfield.JSONCharField(_("传入参数"), max_length=LEN_LONG, default=EMPTY_DICT)
    """
    key: one input key
      value: mapping value
      source: input source, ex: admin/operator
    """
    state_id = models.IntegerField(_("节点ID"), null=True, blank=True)
    workflow_id = models.IntegerField(_("流程ID"), null=True, blank=True)

    objects = TriggerManager()

    class Meta:
        app_label = "workflow"
        verbose_name = _("触发器")
        verbose_name_plural = _("触发器")

    def __str__(self):
        return "{}({})".format(self.name, self.component_key)

    @property
    def serialized_data(self):
        from itsm.workflow.serializers import TriggerSerializer

        return TriggerSerializer(self).data

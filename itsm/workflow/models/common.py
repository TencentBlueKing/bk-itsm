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
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    EMPTY_DICT,
    EMPTY_STRING,
    LEN_LONG,
    LEN_NORMAL,
    LEN_SHORT,
)
from itsm.component.notify import BaseNotifier
from itsm.workflow.managers import GlobalVariableManager

from .base import Model
from ..utils import init_notify_type_choice


class Notify(models.Model):
    """通知"""

    name = models.CharField(_("通知方式名称"), max_length=LEN_NORMAL, unique=True)
    is_builtin = models.BooleanField(_("是否为系统内置"), default=False)
    type = models.CharField(_("通知渠道"), max_length=LEN_SHORT, default="EMAIL")
    template = models.TextField(
        _("通知模板：可使用变量如下：xxx（TODO）"), default=EMPTY_STRING, null=True, blank=True
    )

    class Meta:
        app_label = "workflow"
        verbose_name = _("通知方式")
        verbose_name_plural = _("通知方式")

    def __unicode__(self):
        return "{}-{}({})".format(self.name, self.type, self.is_builtin)

    @classmethod
    def init_builtin_notify(cls, *args, **kwargs):
        notify_type_choice = init_notify_type_choice()
        for notify_type, notify_name in notify_type_choice:
            if not settings.OPEN_VOICE_NOTICE:
                if notify_type == "VOICE":
                    continue

            if not cls.objects.filter(type=notify_type).exists():
                cls.objects.create(name="{}通知".format(notify_name), type=notify_type)

    def send_message(self, title, receivers, message, ticket_id=""):
        """
        发送通知
        """

        notifier = BaseNotifier(title, receivers, message).get_notify_class(
            self.type.lower(),
            **{
                "ticket_id": ticket_id,
            }
        )

        notifier.send()


class GlobalVariable(Model):
    """全局变量
    meta:
      code: pass_count  # 通过人数
      unit: percent  # 百分比
    """

    TYPE_CHOICES = [("STRING", "单行文本"), ("INT", "数字"), ("BOOLEAN", "布尔类型")]

    key = models.CharField(_("变量关键字"), max_length=LEN_LONG)
    name = models.CharField(_("变量名"), max_length=LEN_NORMAL, default=EMPTY_STRING)
    type = models.CharField(
        _("变量类型"), max_length=LEN_SHORT, default="STRING", choices=TYPE_CHOICES
    )

    state_id = models.IntegerField(_("关联节点"), null=True, blank=True)
    flow_id = models.IntegerField(_("关联流程"), null=True, blank=True)

    is_valid = models.BooleanField(_("是否有效"), default=True)
    is_deleted = models.BooleanField(_("是否已删除"), default=False)

    meta = jsonfield.JSONField(_("扩展描述信息"), default=EMPTY_DICT)

    objects = GlobalVariableManager()

    class Meta:
        app_label = "workflow"
        verbose_name = _("全局变量")
        verbose_name_plural = _("全局变量")

    def __unicode__(self):
        return "{}({}-{})".format(self.key, self.flow_id, self.state_id)

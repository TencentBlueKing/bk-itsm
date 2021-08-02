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
    EMPTY_DICT,
    EMPTY_STRING,
    LEN_LONG,
    LEN_NORMAL,
    LEN_SHORT,
    LEN_X_LONG,
    OPERATE_CHOICES,
    PROCESSOR_CHOICES,
    TRANSITION_OPERATE,
)


class Event(models.Model):
    """流转事件"""

    workflow_id = models.IntegerField(_("工作流ID"))
    from_state_id = models.IntegerField(_("当前状态ID"))
    transition_id = models.IntegerField(_("流转ID"), null=True, blank=True)
    to_state_id = models.IntegerField(_("下一个状态ID"), null=True, blank=True)
    type = models.CharField(_("流转事件类型"), max_length=LEN_SHORT, choices=OPERATE_CHOICES, default=TRANSITION_OPERATE)
    processors_type = models.CharField(_("处理人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="OPEN")
    processors = models.CharField(_("处理人列表"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True)
    form_data = jsonfield.JSONField(_("表单快照字典"), default=EMPTY_DICT, null=True, blank=True)

    operate_at = models.DateTimeField(_("操作时间"), auto_now_add=True)
    operator = models.CharField(_("操作人"), max_length=LEN_NORMAL, null=True, blank=True)
    message = models.CharField(_("日志概述"), max_length=LEN_X_LONG, null=True, blank=True)
    is_deleted = models.BooleanField(_("是否软删除"), default=False, db_index=True)

    # 新增
    action = models.CharField(_("动作"), max_length=LEN_NORMAL, blank=True)
    detail_message = models.CharField(_("详细信息"), max_length=LEN_X_LONG, null=True, blank=True)
    from_state_name = models.CharField(_("任务name"), max_length=LEN_NORMAL, blank=True)

    _objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(Event, self).delete()

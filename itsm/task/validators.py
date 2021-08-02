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

from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from itsm.task.models import Task, TaskField
from itsm.ticket.models import Ticket
from itsm.ticket.validators import regex_validate


class TicketValidValidator(object):
    context = {}

    def __call__(self, value):
        try:
            ticket = Ticket.objects.get(id=value)
        except Ticket.DoesNotExist:
            raise ValidationError(_("请输入合法单据ID"))

        request = self.context.get("request")
        if not isinstance(request, Request):
            raise ValidationError(_("非法请求"))
        if not ticket.can_operate(request.user.username):
            raise ValidationError(_("抱歉, 你没有权限操作该单据"))

    def set_context(self, serializer_field):
        self.context = getattr(serializer_field, "context")


class TaskOrdersValidator(object):
    def __call__(self, value):
        task_ids = [i["task_id"] for i in value]
        valid_task_ids = list(Task.objects.filter(id__in=task_ids).values_list("id", flat=True))
        invalid_task_ids = set(task_ids).difference(valid_task_ids)
        if invalid_task_ids:
            raise ValidationError(_("无效任务ID(%s)" % (",".join([str(i) for i in invalid_task_ids]))))


class TaskFieldBatchUpdateValidator(object):
    def __call__(self, value):
        field_ids = [v["id"] for v in value if "id" in v]
        valid_field_ids = TaskField.objects.filter(id__in=field_ids).values_list("id", flat=True)
        invalid_field_ids = set(field_ids).difference(valid_field_ids)
        if invalid_field_ids:
            raise ValidationError(_("无效任务字段ID(%s)" % (",".join([str(i) for i in invalid_field_ids]))))


def validate_task_fields(task_fields, fields):
    required_fields = filter(lambda f: f.validate_type == 'REQUIRE', task_fields)
    required_keys = {f.key for f in required_fields}
    fields_for_key = {f['key']: f for f in fields}
    field_keys = set(fields_for_key.keys())

    lost_keys = required_keys - field_keys
    if lost_keys:
        raise serializers.ValidationError({str(_('参数校验失败')): _('任务处理失败，缺少参数：{}'.format(list(lost_keys)))})

    # 正则校验, 时间校验
    for task_field in task_fields:
        field = fields_for_key.get(task_field.key)
        if field:
            regex_validate(field, task_field)

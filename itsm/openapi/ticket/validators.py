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

from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext as _
from rest_framework import serializers

from itsm.component.exceptions import ParamError
from itsm.component.utils.conversion import format_exp_value
from itsm.ticket.models import TicketGlobalVariable, LEN_MIDDLE
from itsm.ticket.validators import (
    required_validate,
    choice_validate,
    regex_validate,
    custom_regex_validate,
)


def openapi_operate_validate(username, ticket, state_id=None, action_type=None):
    """操作单据校验，state_id不空时，校验节点操作权限"""

    if ticket.is_over:
        raise serializers.ValidationError(_("抱歉，单据已关闭，无法操作"))

    if ticket.is_slave:
        raise serializers.ValidationError(_("抱歉，子单为只读状态，无法操作"))

    if state_id and action_type:
        status = ticket.status(state_id)

        if not status:
            raise serializers.ValidationError(_("抱歉，没有找到该节点：{}").format(state_id))
        if status.status == "FINISHED":
            raise serializers.ValidationError(_("抱歉，当前节点：{} 已经结束").format(state_id))
        if not status.can_operate(username, action_type):
            raise serializers.ValidationError(
                _("抱歉，{}不能操作该节点（没有权限或操作类型不支持）").format(username)
            )
    else:
        if not ticket.can_operate(username):
            raise serializers.ValidationError(_("抱歉，{}无权操作该单据").format(username))


def openapi_suspend_validate(ticket):
    """挂起操作单据校验"""

    if not ticket.is_running:
        raise serializers.ValidationError(_("抱歉，该单据不在流程中，无法操作"))


def openapi_unsuspend_validate(ticket):
    """解挂操作单据校验"""

    if ticket.current_status != "SUSPENDED":
        raise serializers.ValidationError(_("抱歉，该单据不在挂起中，无法操作"))


def edit_field_validate(ticket, field, **kwargs):
    """修改单个字段校验"""

    field_obj = ticket.fields.filter(key=field["key"]).first()

    if field_obj is None:
        raise ParamError(_("未找到提单节点找到对应的字段, key={}".format(field["key"])))

    if not (
        field_obj.key in ["title", "impact", "urgency", "priority"]
        or field_obj.state_id == ticket.first_state_id
    ):
        raise ParamError(_("只允许修改提单节点的字段和内置字段, key={}".format(field["key"])))

    key_value = {
        "params_%s" % field["key"]: format_exp_value(field["type"], field["_value"])
        for field in field_obj.ticket.fields.filter(_value__isnull=False).values(
            "key", "type", "_value"
        )
    }

    key_value.update(
        {
            "params_%s" % item["key"]: item["value"]
            for item in TicketGlobalVariable.objects.filter(
                ticket_id=field_obj.ticket_id
            ).values("key", "value")
        }
    )

    key_value.update(
        {"params_" + field["key"]: format_exp_value(field["type"], field["value"])}
    )

    required_validate(field, field_obj, key_value, skip_readonly=True)
    if field_obj.key == "title" and len(key_value["params_title"]) > LEN_MIDDLE:
        raise serializers.ValidationError(_("标题不能超过120个字符"))

    # 是否必填已经校验
    if not str(field["value"]):
        return field, field_obj

    choice_validate(field, field_obj, key_value, **kwargs)
    regex_validate(field, field_obj)
    custom_regex_validate(field, field_obj)
    return field, field_obj

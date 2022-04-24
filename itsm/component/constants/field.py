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

from django.utils.translation import gettext_lazy as _
from itsm.component.constants import SHOW_BY_CONDITION

# Field code
PROCESS_COUNT = "PROCESS_COUNT"  # 处理人数
PASS_COUNT = "PASS_COUNT"  # 通过人数
REJECT_COUNT = "REJECT_COUNT"  # 拒绝人数
PASS_RATE = "PASS_RATE"  # 通过率
REJECT_RATE = "REJECT_RATE"  # 拒绝率
APPROVE_RESULT = "APPROVE_RESULT"  # 审批结果
NODE_APPROVE_RESULT = "NODE_APPROVE_RESULT"  # 审批结果
NODE_APPROVER = "NODE_APPROVER"  # 审批人

# Value unit
PERCENT = "PERCENT"

# Built-in variables
SIGN_VARIABLES = [
    {"name": _("处理人数"), "type": "INT", "meta": {"code": PROCESS_COUNT}},
    {"name": _("通过人数"), "type": "INT", "meta": {"code": PASS_COUNT}},
    {"name": _("拒绝人数"), "type": "INT", "meta": {"code": REJECT_COUNT}},
    {"name": _("通过率"), "type": "INT", "meta": {"code": PASS_RATE, "unit": PERCENT}},
    {"name": _("拒绝率"), "type": "INT", "meta": {"code": REJECT_RATE, "unit": PERCENT}},
]

# Built-in fields
SIGN_FIELDS = [
    {
        "name": _("会签意见"),
        "is_builtin": False,
        "display": True,
        "type": "SELECT",
        "regex": "EMPTY",
        "choice": [{"key": "true", "name": _("通过")}, {"key": "false", "name": _("拒绝")}],
        "meta": {"code": APPROVE_RESULT},
    },
    {
        "name": _("备注"),
        "is_builtin": False,
        "display": True,
        "type": "TEXT",
        "regex": "EMPTY",
        "layout": "COL_12",
    },
]

APPROVAL_VARIABLES = [
    {
        "name": _("审批结果"),
        "type": "STRING",
        "meta": {
            "code": NODE_APPROVE_RESULT,
            "type": "SELECT",
            "choice": [
                {"key": "false", "name": _("拒绝")},
                {"key": "true", "name": _("通过")},
            ],
        },
    },
    {
        "name": _("审批人"),
        "type": "STRING",
        "meta": {"code": NODE_APPROVER},
    },
]

APPROVAL_FIELDS = [
    {
        "name": _("审批意见"),
        "is_builtin": False,
        "display": True,
        "type": "RADIO",
        "regex": "EMPTY",
        "choice": [{"key": "true", "name": _("通过")}, {"key": "false", "name": _("拒绝")}],
        "meta": {"code": APPROVE_RESULT},
        "default": "true",
    },
    {
        "name": _("备注"),
        "is_builtin": False,
        "type": "TEXT",
        "regex": "EMPTY",
        "layout": "COL_12",
        "validate_type": "OPTION",
        "show_conditions": {
            "expressions": [
                {"value": "false", "type": "RADIO", "condition": "==", "key": ""}
            ],
            "type": "and",
        },
        "show_type": SHOW_BY_CONDITION,
    },
    {
        "name": _("备注"),
        "is_builtin": False,
        "type": "TEXT",
        "regex": "EMPTY",
        "layout": "COL_12",
        "show_conditions": {
            "expressions": [
                {"value": "true", "type": "RADIO", "condition": "==", "key": ""}
            ],
            "type": "and",
        },
        "show_type": SHOW_BY_CONDITION,
    },
]

# 快速审批通知信息模版
FAST_APPROVAL_MESSAGE = """
 标题：{title}
 单号：<a href="{ticket_url}">{sn}</a>
 服务目录：{catalog_service_name}
 当前环节：{running_status}
 """

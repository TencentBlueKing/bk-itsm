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


from django.utils.translation import gettext as _

from .flow import *  # noqa

# 内置单据状态
BUILTIN_TICKET_STATUS = [
    {
        "key": "NEW",
        "name": _("新"),
        "flow_status": PROCESS_RUNNING,
        "order": 1,
        "is_builtin": True,
        "is_start": False,
        "is_over": False,
        "is_suspend": False,
        "color_hex": "#3A84FF",
    },
    {
        "key": "RUNNING",
        "name": _("处理中"),
        "flow_status": PROCESS_RUNNING,
        "order": 2,
        "is_builtin": True,
        "is_start": True,
        "is_over": False,
        "is_suspend": False,
        "color_hex": "#3A84FF",
    },
    {
        "key": "RESOLVED",
        "name": _("已解决"),
        "flow_status": PROCESS_RUNNING,
        "order": 3,
        "is_builtin": False,
        "is_start": False,
        "is_over": False,
        "is_suspend": False,
        "color_hex": "#3A84FF",
    },
    {
        "key": "CONFIRMED",
        "name": _("待确认"),
        "flow_status": PROCESS_RUNNING,
        "order": 4,
        "is_builtin": False,
        "is_start": False,
        "is_over": False,
        "is_suspend": False,
        "color_hex": "#3A84FF",
    },
    {
        "key": "SUSPENDED",
        "name": _("挂起"),
        "flow_status": PROCESS_SUSPENDED,
        "order": 5,
        "is_builtin": True,
        "is_start": False,
        "is_over": False,
        "is_suspend": True,
        "color_hex": "#FF5656",
    },
    {
        "key": "FINISHED",
        "name": _("已完成"),
        "flow_status": PROCESS_FINISHED,
        "order": 6,
        "is_builtin": True,
        "is_start": False,
        "is_over": True,
        "is_suspend": False,
        "color_hex": "#A4AAB3",
    },
    {
        "key": "TERMINATED",
        "name": _("已终止"),
        "flow_status": PROCESS_FAILED,
        "order": 7,
        "is_builtin": True,
        "is_start": False,
        "is_over": True,
        "is_suspend": False,
        "color_hex": "#FF5656",
    },
    {
        "key": "REVOKED",
        "name": _("已撤销"),
        "flow_status": PROCESS_REVOKED,
        "order": 8,
        "is_builtin": True,
        "is_start": False,
        "is_over": True,
        "is_suspend": False,
        "color_hex": "#FF5656",
    },
]
TICKET_END_STATUS = ["FINISHED", "TERMINATED", "REVOKED"]

TICKET_STATUS_CHOICES = [(item["key"], item["name"]) for item in BUILTIN_TICKET_STATUS]
TICKET_STATUS_DICT = dict(TICKET_STATUS_CHOICES)

# 内置字段标识
FIELD_BIZ = "bk_biz_id"
FIELD_TITLE = "title"
FIELD_PY_IMPACT = "impact"
FIELD_PX_URGENCY = "urgency"
FIELD_PRIORITY = "priority"
FIELD_STATUS = "current_status"
FIELD_APPLY_REASON = "apply_reason"
FIELD_APPLY_CONTENT = "apply_content"

# 必选字段
REQUIRED_FIELD = {
    FIELD_PX_URGENCY: _("紧急程度"),
    FIELD_PY_IMPACT: _("影响范围"),
    FIELD_PRIORITY: _("优先级"),
}

# 打回信息字段key
FIELD_BACK_MSG = "can_back_message"
# 终止信息字段key
FIELD_TERM_MSG = "terminate_message"

# 迁移旧流程自动增加的字段key
REJECT_SELECT_KEY = "SYSTEM__REJECT_SELECT__"
DIAMOND_SELECT_KEY = "SYSTEM__DIAMOND_SELECT__"
REJECT_MESSAGE = "SYSTEM__REJECT_MESSAGE__"

# 字段数据需要做json化/反json处理
JSON_HANDLE_FIELDS = [
    "TABLE",
    "CUSTOMTABLE",
    "SOPS_TEMPLATE",
    "CUSTOM-FORM",
    "DEVOPS_TEMPLATE",
]

# 导出字段表
EXPORT_FIELDS = [
    {"id": "sn", "name": _("工单编号")},
    {"id": "title", "name": _("标题")},
    {"id": "bk_biz_id", "name": _("关联业务")},
    {"id": "service_type_name", "name": _("工单类型")},
    {"id": "catalog_fullname", "name": _("服务目录")},
    {"id": "current_status_display", "name": _("状态")},
    {"id": "current_steps", "name": _("当前步骤")},
    {"id": "creator", "name": _("创建人")},
    {"id": "create_at", "name": _("创建时间")},
    {"id": "end_at", "name": _("结束时间")},
    {"id": "service_name", "name": _("服务")},
    {"id": "stars", "name": _("满意度评分")},
    {"id": "comment", "name": _("满意度评价")},
]

# regex
REGEX_STRING_TEXT = [
    ("EMPTY", ""),
    ("FLOAT", _("浮点数")),
    ("NON_NEGATIVE", _("非负数（0，正整数，正浮点数）")),
    ("NON_POSITIVE", _("非正数（0，负整数，负浮点数）")),
    ("GTE_ZERO", _("大于零的数（包括正数和正浮点数）")),
    ("LTE_ZERO", _("小于零的数（包括负数和负浮点数）")),
    ("LOWER_EN", _("仅小写字母")),
    ("UPPER_EN", _("仅大写字母")),
    ("EN", _("仅英文字符")),
    ("EN_NUM", _("仅能包含英文字符和数字")),
    ("CH", _("仅中文字符")),
    ("EN_CH", _("仅能包含中英文字符")),
    ("EN_CH_NUM", _("仅能包含中英文，数字，下划线")),
    ("START_EN", _("包含中英文，数字，以英文字符开头")),
    ("EMAIL", _("邮件")),
    ("PHONE_NUM", _("内地手机号码")),
    ("ID_CARD", _("身份证")),
    ("QQ", _("QQ号码")),
    ("IP", _("IP地址")),
    ("CUSTOM", u"自定义正则表达式"),
]

REGEX_CHOICES = {
    "INT": [
        ("EMPTY", ""),
        ("NUM", _("数字0-9")),
        ("NUMWITHOUTZERO", _("非零正整数")),
        ("ASSOCIATED_FIELD_VALIDATION", _("联合字段校验")),  # v2.4.1暂不支持
        ("CUSTOM", u"自定义正则表达式"),
    ],
    "DATE": [
        ("EMPTY", ""),
        ("AFTER_DATE", _("系统日期之后")),
        ("BEFORE_DATE", _("系统日期之前")),
        ("ASSOCIATED_FIELD_VALIDATION", _("联合字段校验")),
    ],
    "DATETIME": [
        ("EMPTY", ""),
        ("AFTER_TIME", _("系统时间之后")),
        ("BEFORE_TIME", _("系统时间之前")),
        ("ASSOCIATED_FIELD_VALIDATION", _("联合字段校验")),
    ],
    "STRING": REGEX_STRING_TEXT,
    "TEXT": [
        ("EMPTY", ""),
        ("LOWER_EN", _("仅小写字母")),
        ("UPPER_EN", _("仅大写字母")),
        ("EN", _("仅英文字符")),
        ("EN_NUM", _("仅能包含英文字符和数字")),
        ("CH", _("仅中文字符")),
        ("EN_CH", _("仅能包含中英文字符")),
        ("EN_CH_NUM", _("仅能包含中英文，数字，下划线")),
        ("START_EN", _("包含中英文，数字，以英文字符开头")),
        ("CUSTOM", u"自定义正则表达式"),
    ],
}

REGEX_CHOICES_LIST = REGEX_STRING_TEXT + [
    ("NUM", _("数字0-9")),
    ("NUMWITHOUTZERO", _("非零正整数")),
    ("AFTER_DATE", _("系统日期之后")),
    ("BEFORE_DATE", _("系统日期之前")),
    ("AFTER_TIME", _("系统时间之后")),
    ("BEFORE_TIME", _("系统时间之前")),
    ("ASSOCIATED_FIELD_VALIDATION", _("联合字段校验")),
]

# 单据关联关系
DERIVE = "DERIVE"
MASTER_SLAVE = "MASTER_SLAVE"
RELATE_CHOICES = [
    (DERIVE, "转建单"),
    (MASTER_SLAVE, "母子单"),
]

# 单据处理方式
DISTRIBUTE_TYPE_CHOICES = [
    ("DISTRIBUTE_THEN_PROCESS", "先派单，后处理"),
    ("PROCESS", "直接处理"),
    ("CLAIM_THEN_PROCESS", "先认领，后处理"),
    ("DISTRIBUTE_THEN_CLAIM", "先派单，后认领"),
]

DISTRIBUTE_TYPE_ACTION_DICT = {
    "DISTRIBUTE_THEN_PROCESS": [
        (DISTRIBUTE_OPERATE, "DISTRIBUTING"),
        (TRANSITION_OPERATE, "RUNNING"),
    ],
    "PROCESS": [(TRANSITION_OPERATE, "RUNNING")],
    "CLAIM_THEN_PROCESS": [
        (CLAIM_OPERATE, "RECEIVING"),
        (TRANSITION_OPERATE, "RUNNING"),
    ],
    "DISTRIBUTE_THEN_CLAIM": [
        (DISTRIBUTE_OPERATE, "DISTRIBUTING"),
        (CLAIM_OPERATE, "RECEIVING"),
        (TRANSITION_OPERATE, "RUNNING"),
    ],
}

VIRTUAL_TICKET_ID = -1

# 子单同步母单的属性列表
SLAVE_SYNC_ATTRS = [
    "priority_key",
    "current_status",
    "pre_status",
    "current_assignor",
    "current_processors",
    "current_assignor_type",
    "current_processors_type",
    "updated_by",
    "meta",
]

REL_SUMMARY_FIELDS = [
    "reviewIsShutdown",
    "actualBeginTime",
    "actualEndTime",
    "reviewIsDbChange",
    "isSuccess",
    "conclusion",
    "reviewNumerator",
    "executeTime",
    "testTime",
    "reviewDbChangeTime",
    "reviewShutdownTime",
    "dbBackupTime",
    "prepareTime",
]

TIME_DURATION_SUMMARY_FIELDS = [
    "executeTime",
    "testTime",
    "reviewDbChangeTime",
    "reviewShutdownTime",
    "dbBackupTime",
    "prepareTime",
]

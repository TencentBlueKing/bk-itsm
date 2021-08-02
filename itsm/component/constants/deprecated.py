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

from .basic import *  # noqa
from .service import *  # noqa


# ================================================
# deprecated vars
# ================================================
class Field(object):
    def __init__(self, key, name, field_type, pk=False, choices=(), max_length=LEN_LONG, unique=False):
        self.key = key
        self.name = name
        self.field_type = field_type
        self.pk = pk
        self.choices = choices
        self.max_length = max_length
        self.unique = unique


class RelatedField(Field):
    def __init__(
        self,
        key,
        name,
        field_type,
        pk=False,
        choices=(),
        max_length=LEN_LONG,
        unique=False,
        related_name="",
        depend_on="",
    ):
        super(RelatedField, self).__init__(key, name, field_type, pk, choices, max_length, unique)
        self.related_name = related_name
        self.depend_on = depend_on


# 初始化变更服务属性
CHANGE_PROPERTIES = [
    {
        "key": "change_type",
        "name": "变更类型",
        "fields": [
            Field("level", "变更类型", "string", True, max_length=20, unique=True).__dict__,
            Field("desc", "说明", "string").__dict__,
        ],
    }
]

# 初始化事件服务属性
EVENT_PROPERTIES = [
    {
        "key": "plat_type",
        "name": "对应平台",
        "fields": [
            Field("name", "平台名称", "string", True, unique=True).__dict__,
            Field("desc", "描述", "string").__dict__,
        ],
    },
    {
        "key": "event_type",
        "name": "事件类型",
        "is_cascade": True,
        "fields": [
            Field("name", "名称", "string", True, max_length=20, unique=True).__dict__,
            Field("level", "级别", "int", choices=(1, 2, 3)).__dict__,
            Field("desc", "描述", "string", max_length=150).__dict__,
            RelatedField(
                "event_type", "父类型", "string", False, related_name="children", depend_on="event_type"
            ).__dict__,
        ],
    },
    {
        "key": "sla",
        "name": "级别及SLA",
        "fields": [
            Field("level", "级别", "string", True, max_length=20, unique=True).__dict__,
            RelatedField("event_type", "事件类型", "string", False, related_name="sla", depend_on="event_type").__dict__,
            Field("resp_time", "响应时间要求", "string").__dict__,
            Field("deal_time", "解决时间要求", "string").__dict__,
            Field("desc", "说明", "string").__dict__,
        ],
    },
]

# 初始化公共服务属性
PUBLIC_PROPERTIES = [
    {
        "key": "service_category",
        "name": "服务分类",
        "is_cascade": True,
        "fields": [
            Field("level", "级别", "int", choices=(1, 2, 3), unique=True).__dict__,
            Field("name", "服务分类名称", "string", True, max_length=20).__dict__,
            Field("desc", "说明", "string", max_length=100).__dict__,
            RelatedField(
                "parent_key", "上级分类", "string", False, related_name="children", depend_on="service_category"
            ).__dict__,
        ],
    }
]

# 初始化请求管理服务属性
REQUEST_PROPERTIES = [
    {
        "key": "request_type",
        "name": "请求管理",
        "fields": [
            Field("level", "请求管理类别", "string", True, unique=True).__dict__,
            Field("desc", "请求管理描述", "string").__dict__,
        ],
    }
]

# 初始化问题管理服务属性
QUESTION_PROPERTIES = [
    {
        "key": "question_type",
        "name": "问题管理",
        "fields": [
            Field("level", "问题管理类别", "string", True, unique=True).__dict__,
            Field("desc", "问题管理描述", "string").__dict__,
        ],
    }
]

# 初始化
PROPERTIES = [
    (CHANGE, CHANGE_PROPERTIES),
    (EVENT, EVENT_PROPERTIES),
    (PUBLIC, PUBLIC_PROPERTIES),
    (REQUEST, REQUEST_PROPERTIES),
    (QUESTION, QUESTION_PROPERTIES),
]

# 初始化服务属性记录
PROPERTIES_RECORDS = [
    # service_property key pk_value data
    # 故障类型内置
    ("event_type", "fault", "故障事件", {"level": 1, "name": "故障事件", "desc": "故障事件描述", "event_type": ""}),
    (
        "event_type",
        "567e174c9c1136bc2c9550f8d843a4be",
        "硬件类",
        {"level": 2, "event_type": "fault", "name": "硬件类", "desc": "硬件类异常事件。"},
    ),
    (
        "event_type",
        "faeecbb37d92a7b4d70306e46a57f091",
        "服务器、交换机等",
        {"desc": "硬件设备类异常。", "event_type": "567e174c9c1136bc2c9550f8d843a4be", "name": "服务器、交换机等", "level": 3},
    ),
    ("plat_type", "business", "业务平台", {"name": "业务平台", "desc": "业务平台描述"}),
    ("plat_type", "cloud", "云平台", {"name": "云平台", "desc": "云平台描述"}),
    # 服务分类内置
    (
        "service_category",
        "b334f1e165782da9d02ae799bc6808e2",
        "基础设施",
        {"desc": "基础性设施", "name": "基础设施", "parent_key": "", "level": 1},
    ),
    (
        "service_category",
        "fe65fd7bbf0cd883f731c5ba4700483d",
        "网络资源",
        {"desc": "资源申请", "name": "网络资源", "parent_key": "b334f1e165782da9d02ae799bc6808e2", "level": 2},
    ),
    (
        "service_category",
        "557bfdd6a2e5f7659abde7f31266c9e6",
        "故障受理",
        {"level": 1, "name": "故障受理", "parent_key": "", "desc": "受理报障或异常处理"},
    ),
    (
        "service_category",
        "3a8a13237c2183cee68062285e4bd454",
        "数据服务",
        {"desc": "数据类的需求", "name": "数据服务", "parent_key": "", "level": 1},
    ),
    # 变更类型内置
    ("change_type", "47e8d8abad78045a23c1339cb285096e", "标准变更", {"desc": "适用日常标准变更场景。", "level": "标准变更"}),
]

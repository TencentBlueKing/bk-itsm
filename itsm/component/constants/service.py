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

from .role import *  # noqa


# 变更服务类型
CHANGE = "change"
# 事件服务类型
EVENT = "event"
# 公共服务类型（虚拟）
PUBLIC = "public"
# 请求服务类型
REQUEST = "request"
# 问题管理类型
QUESTION = "question"

# 服务列表
SERVICE_LIST = [CHANGE, EVENT, REQUEST, QUESTION]
PERMIT_LIST = SERVICE_LIST + ["role", "public"]

SERVICE_CHOICE = [
    (CHANGE, "变更"),
    (EVENT, "事件"),
    (QUESTION, "问题"),
    (REQUEST, "请求"),
]
SERVICE_DICT = dict(SERVICE_CHOICE)
FLOW_TYPE_CHOICE = SERVICE_CHOICE

# 服务展示使用
DISPLAY_CHOICES = [
    (CMDB, "CMDB业务公用角色"),
    (GENERAL, "通用角色表"),
    (OPEN, "不限"),
    (PERSON, "个人"),
    (ORGANIZATION, "组织架构"),
    (INVISIBLE, "不可见"),
    (API, "第三方系统"),
]


CUSTOM = "custom"
SERVICE = "service"
TEMPLATE = "template"

# 服务表单来源
SERVICE_SOURCE_CHOICES = [
    (CUSTOM, "自定义"),
    (SERVICE, "服务"),
    (TEMPLATE, "模版"),
]

# 服务类别
SERVICE_CATEGORY = {
    CHANGE: "变更管理",
    REQUEST: "请求管理",
    EVENT: "事件管理",
    PUBLIC: "服务分类",
    QUESTION: "问题管理",
}

# 服务类别
SERVICE_CATEGORY_DESC = {
    'request_desc': "请求管理类相关服务",
    'change_desc': "变更管理类相关服务",
    'event_desc': "事件管理类相关服务",
    'public_desc': "服务分类类相关服务",
    'question_desc': "问题管理类相关服务",
}

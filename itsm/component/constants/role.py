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


# 可以看到所有工单，但是不能操作
ADMIN_READ_ONLY = "read_only"
# 可以看到，且可以操作所有工单
ADMIN_SUPERUSER = "superuser"
# 可以管理知识库所有文章
WIKI_ADMIN_SUPERUSER = "wiki_superuser"
# 可以看到，和管理自己负责的流程
WORKFLOW_SUPERUSER = "workflow_superuser"

# 蓝鲸管理员
ADMIN_BK_SUPERUSER_KEY = "BK_SUPERUSER"
# 工单统计管理员
ADMIN_STATICS_MANAGER_KEY = "STATICS_MANAGER"
# ITSM超级管理员
ADMIN_SUPERUSER_KEY = "SUPERUSER"
# WIKI超级管理员
WIKI_ADMIN_SUPERUSER_KEY = "WIKI_SUPERUSER"
# 流程管理员
WORKFLOW_SUPERUSER_KEY = "WORKFLOW_MANAGER"

ADMIN_CHOICES = [
    (WORKFLOW_SUPERUSER, "流程管理员"),
    (ADMIN_READ_ONLY, "统计配置"),
    (ADMIN_SUPERUSER, "超级管理员"),
    (WIKI_ADMIN_SUPERUSER, "知识库管理员"),
]
ACCESS_NAMES = dict(ADMIN_CHOICES)

CMDB = "CMDB"
GENERAL = "GENERAL"
OPEN = "OPEN"
PERSON = "PERSON"
STARTER = "STARTER"
STARTER_LEADER = "STARTER_LEADER"
BY_ASSIGNOR = "BY_ASSIGNOR"
ORGANIZATION = "ORGANIZATION"
VARIABLE = "VARIABLE"
INVISIBLE = "INVISIBLE"
IAM = "IAM"
API = "API"
ASSIGN_LEADER = "ASSIGN_LEADER"

PROCESSOR_CHOICES = [
    (CMDB, "CMDB业务公用角色"),
    (GENERAL, "通用角色表"),
    (OPEN, "不限"),
    (PERSON, "个人"),
    (STARTER, "提单人"),
    (STARTER_LEADER, "提单人上级"),
    (ASSIGN_LEADER, "指定节点处理人上级"),
    (BY_ASSIGNOR, "派单人指定"),
    (EMPTY, "无"),
    (ORGANIZATION, "组织架构"),
    (VARIABLE, "引用变量"),
    (IAM, "权限中心角色"),
]

ADMIN = "admin"

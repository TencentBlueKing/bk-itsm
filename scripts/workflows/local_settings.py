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

import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        # 新版插件管理数据库
        "NAME": os.getenv("BK_MYSQL_NAME"),  # 数据库名
        "USER": os.getenv("BK_MYSQL_USER"),
        "PASSWORD": os.getenv("BK_MYSQL_PASSWORD"),
        "HOST": os.getenv("BK_MYSQL_HOST"),
        "PORT": os.getenv("BK_MYSQL_PORT"),
        "OPTIONS": {
            # Tell MySQLdb to connect with 'utf8mb4' character set
            "charset": "utf8",
        },
        "COLLATION": "utf8_general_ci",
        "TEST": {
            "NAME": os.getenv("BK_MYSQL_TEST_NAME"),
            "CHARSET": "utf8",
            "COLLATION": "utf8_general_ci",
        },
    },
}

# 本地开发无需权限中心
BK_IAM_SKIP = True
USE_IAM = True if os.getenv("USE_IAM", "false").lower() == "true" else False
if not USE_IAM:
    BK_IAM_SKIP = True

DEBUG = True

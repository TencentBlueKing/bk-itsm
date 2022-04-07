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

# 社区版/企业版配置

import os

from django.core.files.storage import FileSystemStorage

from . import api as ADAPTER_API  # noqa

ESB_SDK_NAME = "blueking.component.open"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("BKAPP_DB_TEST"),
        "USER": os.environ.get("BKAPP_MYSQL_USER"),
        "PASSWORD": os.environ.get("BKAPP_MYSQL_PASS"),
        "HOST": os.environ.get("BKAPP_MYSQL_IP"),
        "PORT": os.environ.get("BKAPP_MYSQL_PORT"),
    },
}

STORE = FileSystemStorage(location="/")

# 企业微信发送，默认weixin，可配置为企业微信rtx
QY_WEIXIN = os.environ.get("BKAPP_WEIXIN_TYPE", "weixin")

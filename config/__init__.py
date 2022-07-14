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
import sys

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app


def get_env_or_raise(key):
    """Get an environment variable, if it does not exist, raise an exception"""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            (
                'Environment variable "{}" not found, you must set this variable to run this application.'
            ).format(key)
        )
    return value


__all__ = [
    "celery_app",
    "RUN_VER",
    "APP_CODE",
    "SECRET_KEY",
    "BK_URL",
    "BASE_DIR",
    "PROJECT_PATH",
    "PROJECT_ROOT",
    "BASE_DIR",
    "PYTHON_BIN",
    "BK_PAAS_HOST",
    "BK_PAAS_INNER_HOST",
]

# app 基本信息

# SaaS运行版本，如非必要请勿修改
RUN_VER = "open"
# SaaS应用ID
APP_ID = os.environ.get("BKPAAS_APP_ID", "")
# SaaS安全密钥，注意请勿泄露该密钥
APP_TOKEN = os.environ.get("BKPAAS_APP_SECRET", "")
# 蓝鲸SaaS平台URL，例如 http://paas.bking.com
BK_PAAS_HOST = os.environ.get("BKAPP_PAAS_HOST", "")

RUN_VER = os.environ.get("RUN_VER", RUN_VER)
OPEN_VER = "enterprise"
APP_CODE = APP_ID = os.environ.get("APP_ID", APP_ID)
BK_APP_CODE = APP_ID
SECRET_KEY = APP_TOKEN = os.environ.get("APP_TOKEN", APP_TOKEN)
BK_APP_SECRET = SECRET_KEY
BK_URL = BK_PAAS_HOST = os.environ.get("BK_PAAS_HOST", "")
BK_PAAS_INNER_HOST = os.environ.get("BK_PAAS_INNER_HOST", BK_PAAS_HOST)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(
#     __file__)))

# 项目路径
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT, PROJECT_MODULE_NAME = os.path.split(PROJECT_PATH)
BASE_DIR = PROJECT_ROOT
PYTHON_BIN = os.path.dirname(sys.executable)

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
import importlib
from urllib.parse import urljoin

from config import RUN_VER, BK_PAAS_HOST, OPEN_VER  # noqa

if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa

    BK_STATIC_URL = STATIC_URL.rstrip("/")
else:
    from blueapps.patch.settings_paas_services import *  # noqa

    BK_STATIC_URL = "/static"

    # 正式环境 static_url 设置为 https
    STATIC_FRONTEND_URL = os.environ.get("BKAPP_FRONTEND_URL", None)
    if STATIC_FRONTEND_URL is not None:
        STATIC_URL = "%sstatic/" % STATIC_FRONTEND_URL

# 预发布环境
RUN_MODE = "STAGING"
RIO_TOKEN = os.environ.get("RIO_TOKEN", "")

# 正式环境的日志级别可以在这里配置
# V2
# import logging
# logging.getLogger('root').setLevel('INFO')
# V3
# import logging
# logging.getLogger('app').setLevel('INFO')


# 预发布环境数据库可以在这里配置

DATABASES.update(
    {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("BKAPP_DB_TEST"),
            "USER": os.environ.get("BKAPP_MYSQL_USER"),
            "PASSWORD": os.environ.get("BKAPP_MYSQL_PASS"),
            "HOST": os.environ.get("BKAPP_MYSQL_IP"),
            "PORT": os.environ.get("BKAPP_MYSQL_PORT"),
        },
    }
)

ALLOW_CSRF = os.environ.get("BKAPP_ALLOW_CSRF", None) == "1"

# ===============================================================================
# CSRF SETTINGS
# ===============================================================================
if ALLOW_CSRF:
    # 根据环境变量选择性开启跨域功能
    MIDDLEWARE = ("common.middlewares.DisableCSRFCheck",) + MIDDLEWARE

MEDIA_URL = "%smedia/" % SITE_URL
CSRF_COOKIE_NAME = "bkitsm_csrftoken"

# REMOTE_STATIC_URL = "http://127.0.0.1:8000/static/"
# STATIC_URL = "http://127.0.0.1:8000/static/"
# ==============================================================================
# 加载环境差异化配置
# ==============================================================================
ver_settings = importlib.import_module("adapter.config.sites.%s.ver_settings" % RUN_VER)
for _setting in dir(ver_settings):
    if _setting.upper() == _setting:
        locals()[_setting] = getattr(ver_settings, _setting)

ENGINE_REGION = os.environ.get("BKPAAS_ENGINE_REGION", "open")
if ENGINE_REGION == "default":
    default_settings = importlib.import_module(
        "adapter.config.sites.%s.ver_settings" % "v3"
    )
    for _setting in dir(default_settings):
        if _setting.upper() == _setting:
            locals()[_setting] = getattr(default_settings, _setting)

BK_IAM_RESOURCE_API_HOST = os.getenv(
    "BKAPP_IAM_RESOURCE_API_HOST", urljoin(BK_PAAS_INNER_HOST, "/t/{}".format(APP_CODE))
)

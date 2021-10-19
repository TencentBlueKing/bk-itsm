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

from config import RUN_VER, BK_PAAS_HOST, OPEN_VER  # noqa

if RUN_VER == "open":
    # config.default + extra
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 本地开发环境
RUN_MODE = "DEVELOP"

# APP本地静态资源目录
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "static_root/")
BK_STATIC_URL = "/static"

# APP静态资源目录url
# REMOTE_STATIC_URL = '%sremote/' % STATIC_URL

# Celery 消息队列设置 RabbitMQ
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# Celery 消息队列设置 Redis
BROKER_URL = "redis://localhost:6379/0"

DEBUG = True

# 分享链接
# FRONTEND_URL = os.environ.get("BKAPP_FRONTEND_URL", "") or "{}{}".format(BK_PAAS_HOST, SITE_URL)

ALLOW_CSRF = True
# ===============================================================================
# CSRF SETTINGS
# ===============================================================================
if ALLOW_CSRF:
    # 根据环境变量选择性开启跨域功能
    MIDDLEWARE = ("common.middlewares.DisableCSRFCheck",) + MIDDLEWARE

MEDIA_URL = "%smedia/" % SITE_URL

# ==============================================================================
# 加载环境差异化配置
# ==============================================================================
ver_settings = importlib.import_module("adapter.config.sites.%s.ver_settings" % RUN_VER)
for _setting in dir(ver_settings):
    if _setting.upper() == _setting:
        locals()[_setting] = getattr(ver_settings, _setting)

# 针对 paas_v3 容器化铺垫
ENGINE_REGION = os.environ.get("BKPAAS_ENGINE_REGION", "open")
if ENGINE_REGION == "default":
    default_settings = importlib.import_module(
        "adapter.config.sites.%s.ver_settings" % "v3"
    )
    for _setting in dir(default_settings):
        if _setting.upper() == _setting:
            locals()[_setting] = getattr(default_settings, _setting)

# 多人开发时，无法共享的本地配置可以放到新建的 local_settings.py 文件中
# 并且把 local_settings.py 加入版本管理忽略文件中
try:
    from .local_settings import *  # noqa
except ImportError:
    pass

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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

# """Django project settings
# """

import os

try:
    from django.conf import settings

    APP_CODE = settings.APP_ID
    SECRET_KEY = settings.APP_TOKEN
    # COMPONENT_SYSTEM_HOST = settings.BK_PAAS_HOST
    # HTTPS-SUPPORT
    # COMPONENT_SYSTEM_HOST = getattr(
    #     settings,
    #     'BK_PAAS_INNER_HOST',
    #     settings.BK_PAAS_HOST)
    HOST = getattr(settings, "BK_PAAS_INNER_HOST", settings.BK_PAAS_HOST)
    
    # 优先使用网关接口
    # 从 BK_API_URL_TMPL 中提取基础域名
    BK_API_URL_TMPL = os.environ.get("BK_API_URL_TMPL", "")
    if BK_API_URL_TMPL and "{api_name}" in BK_API_URL_TMPL:
        # 移除 /api/{api_name} 部分，保留基础域名
        COMPONENT_SYSTEM_HOST = BK_API_URL_TMPL.split("/api/")[0]
    else:
        COMPONENT_SYSTEM_HOST = os.environ.get("BK_COMPONENT_API_URL", HOST)
    
    DEFAULT_BK_API_VER = getattr(settings, "DEFAULT_BK_API_VER", "v2")
except BaseException:
    APP_CODE = ""
    SECRET_KEY = ""
    COMPONENT_SYSTEM_HOST = ""
    DEFAULT_BK_API_VER = "v2"

CLIENT_ENABLE_SIGNATURE = False

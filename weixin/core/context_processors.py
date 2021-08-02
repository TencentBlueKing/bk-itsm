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
from . import settings as wx_settings


def basic(request):
    return {
        'WX_USER': getattr(request, 'weixin_user', None),
        'BK_USER': getattr(request, 'user', None),
        'WEIXIN_SITE_URL': wx_settings.WEIXIN_SITE_URL,
        'WEIXIN_STATIC_URL': wx_settings.WEIXIN_STATIC_URL,
        'CUSTOM_TITLE': wx_settings.settings.CUSTOM_TITLE or "流程服务",
        "BK_USER_MANAGE_WEIXIN_HOST": os.path.join(wx_settings.WEIXIN_APP_EXTERNAL_HOST, "weixin"),
        # 用户管理的接口，直接用微信外网转发
        "FRONTEND_URL": wx_settings.settings.FRONTEND_URL,
    }

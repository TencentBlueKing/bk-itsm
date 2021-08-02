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

from functools import wraps

from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext_lazy as _

import settings
from weixin.utils import FailResponse


def validate_weixin(view_func):
    @wraps(view_func)
    def __wrapper(request, *args, **kwargs):

        # 必须在微信中打开

        if isinstance(request.weixin_user, AnonymousUser):
            return FailResponse(message=_('请在企业微信中打开链接'), code='1002').json()

        # 必须绑定微信到蓝鲸
        if isinstance(request.user, AnonymousUser):
            return FailResponse(
                message=_('请先登录蓝鲸平台的个人中心({}/console/user_center/)绑定你的微信({})，并访问一次ITSM.').format(
                    settings.BK_PAAS_HOST, getattr(request.weixin_user, 'nickname', '')), code='1003').json()

        return view_func(request, *args, **kwargs)

    return __wrapper

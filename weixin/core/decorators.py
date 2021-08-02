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

# """登录装饰器."""
from functools import wraps

# from django.utils.decorators import available_attrs

from .accounts import WeixinAccount


def weixin_login_exempt(view_func):
    """登录豁免,被此装饰器修饰的action可以不校验登录."""
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.weixin_login_exempt = True
    # return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
    return wraps(view_func)


def weixin_login_required(view_func):
    # @wraps(view_func, assigned=available_attrs(view_func))
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 验证OK
        weixin_account = WeixinAccount()
        if weixin_account.is_weixin_visit(
            request) and not request.weixin_user.is_authenticated:
            return weixin_account.redirect_weixin_login(request)
        return view_func(request, *args, **kwargs)

    return _wrapped_view

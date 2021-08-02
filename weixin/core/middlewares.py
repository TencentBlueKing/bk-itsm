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

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from blueapps.account.models import UserProperty
from common.mymako import render_mako_context
from itsm.component.constants import MOBILE, WEB

from .accounts import WeixinAccount
from .models import BkWeixinUser

logger = logging.getLogger('root')

User = get_user_model()
weixin_account = WeixinAccount()


def get_user(request):
    user = None
    user_id = request.session.get('weixin_user_id')
    if user_id:
        try:
            user = BkWeixinUser.objects.get(pk=user_id)
        except BkWeixinUser.DoesNotExist:
            user = None
    return user or AnonymousUser()


def get_bk_user(request):
    bkuser = None
    if request.weixin_user and not isinstance(request.weixin_user, AnonymousUser):
        user_model = get_user_model()
        try:
            user_property = UserProperty.objects.get(key='wx_userid',
                                                     value=request.weixin_user.userid)
        except UserProperty.DoesNotExist:
            logger.warning('user[wx_userid=%s] not in UserProperty' % request.weixin_user.userid)
        else:
            bkuser = user_model.objects.get(username=user_property.user.username)
    return bkuser or AnonymousUser()


class WeixinProxyPatchMiddleware(MiddlewareMixin):
    """
    解决多级nginx代理下遇到的最外层nginx的`X-Forwarded-Host`设置失效问题
    思路：单独设置一个头，并根据该头覆盖`X-Forwarded-Host`

    # django.http.request +73

    def get_host(self):
        '''Returns the HTTP host using the environment or request headers.'''
        # We try three options, in order of decreasing preference.
        if settings.USE_X_FORWARDED_HOST and (
                'HTTP_X_FORWARDED_HOST' in self.META):
            host = self.META['HTTP_X_FORWARDED_HOST']
            ...
    """

    def process_request(self, request):

        # 非微信访问，跳过中间件
        if not weixin_account.is_weixin_visit(request):
            setattr(request, 'source', WEB)
            setattr(request, 'is_weixin', False)
            return None

        if settings.X_FORWARDED_WEIXIN_HOST in request.META:
            request.META['HTTP_X_FORWARDED_HOST'] = request.META[settings.X_FORWARDED_WEIXIN_HOST]
            setattr(request, 'is_weixin', True)
            setattr(request, 'source', MOBILE)
            return None


class WeixinAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):

        if not getattr(request, 'is_weixin', False):
            return None

        assert hasattr(request, 'session'), (
            "The Weixin authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'weixin.core.middleware.WeixinAuthenticationMiddleware'."
        )
        setattr(request, 'weixin_user', SimpleLazyObject(lambda: get_user(request)))
        setattr(request, 'user', SimpleLazyObject(lambda: get_bk_user(request)))

        # 微信调试豁免
        if settings.WX_USER:
            weixin_user = BkWeixinUser.objects.first()
            if weixin_user:
                request.user = User.objects.first()
                request.weixin_user = weixin_user
                return None

    def process_response(self, request, response):
        """
        将weixin_user_id写入cookies，避免SESSION_COOKIE_AGE时间太短导致session过期
        """

        if not getattr(request, 'is_weixin', False):
            return response

        if request.session.get('weixin_user_id'):
            response.set_cookie('weixin_user_id', request.session['weixin_user_id'])
        return response


class WeixinLoginMiddleware(MiddlewareMixin):
    """weixin Login middleware."""

    def process_view(self, request, view, args, kwargs):
        """process_view."""

        if not getattr(request, 'is_weixin', False):
            return None

        # 微信路径默认取消蓝鲸登录
        setattr(view, 'login_exempt', True)

        # 豁免微信登录装饰器
        if getattr(view, 'weixin_login_exempt', False):
            return None

        # 验证OK
        if request.weixin_user.is_authenticated:
            # 必须绑定微信到蓝鲸 - 返回状态码 438
            if isinstance(request.user, AnonymousUser):
                return render_mako_context(request, '/weixin/438.html',
                                           {"CUSTOM_TITLE": settings.CUSTOM_TITLE})

            return None

        # 微信登录失效或者未通过验证，直接重定向到微信登录
        return weixin_account.redirect_weixin_login(request)

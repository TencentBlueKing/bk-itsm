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

from . import conf
from .client import ComponentClient

logger = logging.getLogger('component')

__all__ = [
    'get_client_by_request',
    'get_client_by_user',
]


def get_client_by_request(request, **kwargs):
    """根据当前请求返回一个client

    :param request: 一个django request实例
    :returns: 一个初始化好的ComponentClint对象
    """

    if request.user.is_authenticated:
        bk_token = request.COOKIES.get('bk_token', '')
    else:
        bk_token = ''

    common_args = {
        'bk_token': bk_token,
    }
    common_args.update(kwargs)
    return ComponentClient(conf.APP_CODE, conf.SECRET_KEY,
                           common_args=common_args)


def get_client_by_user(user, **kwargs):
    """根据user实例返回一个client

    :param user: User实例或者User.username数据
    :returns: 一个初始化好的ComponentClint对象
    """
    try:
        from account.models import BkUser as User
    except BaseException:
        from django.contrib.auth.models import User

    try:
        if isinstance(user, User):
            username = user.username
        else:
            username = user
    except BaseException:
        logger.exception('Failed to get user according to user (%s)' % user)

    common_args = {'bk_username': username}
    common_args.update(kwargs)
    return ComponentClient(conf.APP_CODE, conf.SECRET_KEY,
                           common_args=common_args)

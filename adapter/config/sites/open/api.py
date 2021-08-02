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


def get_batch_users(users, properties='all', is_exact=True, page_params=None):
    """
    批量获取用户信息
    """

    if page_params is None:
        page_params = {}

    from itsm.component.esb.esbclient import client_backend
    if not users:
        # 不带用户的情况下，直接返回空列表
        return []

    params = {"bk_username_list": users}
    default_properties = 'username,display_name,telephone,email,qq,wx_userid,departments'

    data = client_backend.bk_login.get_batch_users(**params)

    if properties == 'all':
        # 展示所有属性
        user_list = [data.get(user) for user in users if data.get(user)]
    else:
        # 根据所传属性提取
        properties = properties if properties else default_properties
        properties = properties.split(',')
        user_list = [
            {_property: data.get(user).get(_property) for _property in properties if _property}
            for user in users
            if data.get(user)
        ]

    return user_list


def get_all_users(users=None):
    """获取所有用户列表"""
    from itsm.component.esb.esbclient import client_backend

    if users is None:
        users = []

    if users:
        res = get_batch_users(users)
    else:
        res = client_backend.bk_login.get_all_users()

    return [
        {
            "id": user["bk_username"],
            "name": '{}({})'.format(user['bk_username'], user['chname']),
            "bk_username": user["bk_username"],
            "chname": user["chname"],
        }
        for user in res
    ]


# 企业/社区版启用用户管理
if os.environ.get("BKAPP_ENABLE_USERMGR") != '0':
    # 默认需要用用户管理
    from adapter.config.sites.ieod.api import get_batch_users  # noqa
    from adapter.config.sites.ieod.api import get_all_users  # noqa

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
from common.log import logger


def get_batch_users(users, properties, is_exact=True, page_params=None, name_type=None):
    """
    批量获取用户信息
    """
    if page_params is None:
        page_params = {}
    from itsm.component.esb.esbclient import client_backend

    if not users:
        # 不带用户的情况下，直接返回空列表
        return []

    # BLAME: fields为空时，exact_lookups查询出来的列表重复
    kwargs = {
        "fields": "username,display_name,telephone,email,qq,wx_userid,time_zone,id,domain,logo,category_id,departments",
    }

    kwargs.update(page_params)

    if not is_exact:
        kwargs["fuzzy_lookups"] = ",".join(users)
    else:
        kwargs["exact_lookups"] = ",".join(users)

    if properties:
        if properties == "all":
            kwargs.pop("fields")
        else:
            kwargs.update(fields=properties)

    all_users = client_backend.usermanage.list_users(kwargs)["results"]
    if name_type:
        all_users = [
            {
                "id": user["username"],
                "name": "{}({})".format(user["username"], user["display_name"]),
                "bk_username": user["username"],
                "chname": user["display_name"],
            }
            for user in all_users
        ]
    return all_users


def get_all_users(users=None):
    """该接口不再支持全量查询，不带用户直接返回None"""

    if not users:
        return []

    normal_users = []
    cross_dir_users = []

    for user in users:
        if "@" in user:
            cross_dir_users.append(user)
        else:
            normal_users.append(user)
    logger.info(
        "[get_all_users]正在获取全部用户,normal_users:{}, cross_dir_users:{}".format(
            normal_users, cross_dir_users
        )
    )
    all_users = query_user_info(normal_users, cross_dir_users)
    logger.info(
        "[get_all_users]获取全部用户结束,all_users:{}, normal_users:{}, cross_dir_users:{}".format(
            all_users, normal_users, cross_dir_users
        )
    )

    all_users = [
        {
            "id": user["username"],
            "name": "{}({})".format(user["username"], user["display_name"]),
            "bk_username": user["username"],
            "chname": user["display_name"],
        }
        for user in all_users
    ]
    return all_users


def query_user_info(normal_users, cross_dir_users):
    from itsm.component.esb.esbclient import client_backend

    # if not cross_dir_users and not normal_users:
    #     all_users = client_backend.usermanage.list_users(
    #         {'fields': 'username,display_name', 'fuzzy_lookups': "", 'no_page': True}
    #     )
    #     return all_users

    all_users = []
    if cross_dir_users:
        for single_user in cross_dir_users:
            single_user_info = client_backend.usermanage.retrieve_user(
                {"fields": "username,display_name", "id": single_user}
            )
            all_users.append(single_user_info)
    if normal_users:
        all_normal_users = client_backend.usermanage.list_users(
            {"fields": "username,display_name", "exact_lookups": ",".join(normal_users)}
        )
        logger.info(
            "[query_user_info] -> esb results return = {}, normal_users={}".format(
                all_normal_users, normal_users
            )
        )
        all_users.extend(all_normal_users["results"])
    return all_users

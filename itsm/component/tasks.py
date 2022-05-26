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

from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
from django.core.cache import cache
from django.conf import settings
from itsm.component.constants import CACHE_10MIN, CACHE_5MIN
from itsm.component.esb.esbclient import client_backend
from itsm.component.utils.lock import share_lock
from itsm.component.exceptions import ComponentCallError

adapter_api = settings.ADAPTER_API


@task
def update_user_cache(cache_key, ret_type="list", name_type="bk_username", users=None):
    """更新用户缓存"""
    bk_users = None
    try:
        res = adapter_api.get_all_users(users)
    except ComponentCallError:
        res = []

    if ret_type == "dict" and name_type == "bk_username":
        bk_users = {user["bk_username"]: user["name"] for user in res}
    if ret_type == "dict" and name_type == "chname":
        bk_users = {user["bk_username"]: user["chname"] for user in res}
    if ret_type == "list":
        bk_users = [user[name_type] for user in res]
    if bk_users:
        cache.set(cache_key, bk_users, CACHE_10MIN)
    return bk_users


@task
def update_bk_business(cache_key, bk_biz_id, role_type):
    """更新CMDB缓存"""

    @share_lock(identify=cache_key)
    def update():
        try:
            search_business_list = client_backend.cc.search_business(
                {
                    "bk_supplier_id": 0,
                    "fields": role_type,
                    "condition": {"bk_biz_id": int(bk_biz_id)},
                    "page": {"start": 0, "limit": 200, "sort": ""},
                }
            ).get("info")
            cache.set(cache_key, search_business_list, CACHE_5MIN)
            return search_business_list
        except ComponentCallError as e:
            print("获取业务角色人员失败: %s" % e)
            return []

    result = update()
    return result if result else []


@task
def update_user_departments(cache_key, username, id_only):
    """更新组织缓存"""

    @share_lock(identify=cache_key)
    def update():
        try:
            res = client_backend.usermanage.list_profile_departments(
                {"id": username, "with_family": True}
            )
        except ComponentCallError as e:
            print("获取组织架构失败：username=%s，error=%s" % (username, str(e)))
            return []

        if not id_only:
            cache.set(cache_key, res, CACHE_10MIN)
            return res

        departments = []
        for sub_dept in res:
            departments.extend(
                [str(dept.get("id")) for dept in sub_dept.get("family", [])]
            )
            departments.append(sub_dept.get("id"))
        cache.set(cache_key, departments, CACHE_10MIN)
        return departments

    result = update()
    return result if result else []


@periodic_task(run_every=crontab(minute=0, hour="0,1,2,3,4"))
def delete_tracker_record():
    pass

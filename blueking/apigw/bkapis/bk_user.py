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

from bkapi_client_core.base import Operation

from bkapi_client_core.django_helper import _get_client_by_settings
from bkapi_client_core.django_helper import get_client_by_request as _get_client_by_request
from bkapi_client_core.django_helper import get_client_by_username as _get_client_by_username
from bkapi_client_core.property import bind_property
from bkapi_client_core.utils import generic_type_partial as _partial

from blueking.apigw.base import ApiProtocol, TenantBaseClient
from blueking.apigw.utils import get_endpoint


class Client(TenantBaseClient):
    """蓝鲸用户管理 API 客户端"""

    # 查询用户的部门信息
    list_user_department = bind_property(
        Operation,
        name="list_user_department",
        method="GET",
        path="api/v3/open/tenant/users/{bk_username}/departments/",
    )
    
    # 查询部门
    list_departments = bind_property(
        Operation,
        name="list_departments",
        method="GET",
        path="api/v3/open/tenant/departments/",
    )
    
    # 查询用户列表
    list_user = bind_property(
        Operation,
        name="list_users",
        method="GET",
        path="api/v3/open/tenant/users/",
        params={"page": 1, "page_size": 100},
    )
    
    # 查询用户信息
    retrieve_user = bind_property(
        Operation,
        name="retrieve_user",
        method="GET",
        path="/api/v3/open/tenant/users/{bk_username}/",
    )
    
    # 根据部门 ID 查询部门下的用户列表
    list_department_user = bind_property(
        Operation,
        name="list_department_user",
        method="GET",
        path="api/v3/open/tenant/departments/{department_id}/users/",
    )
    
    # 查询部门信息
    retrieve_department = bind_property(
        Operation,
        name="retrieve_department",
        method="GET",
        path="api/v3/open/tenant/departments/{department_id}/",
    )


class BkUserApi(ApiProtocol):
    """蓝鲸用户管理 API 协议类"""

    _api_name = "bk-user"

    @classmethod
    def get_client(cls) -> Client:
        """通过 settings 配置获取客户端（无用户上下文）"""
        return _get_client_by_settings(Client, endpoint=get_endpoint(cls._api_name, "prod"))

    @classmethod
    def get_client_by_request(cls, request):
        """通过 request 对象获取客户端（有用户上下文，推荐在视图中使用）"""
        return (_partial(Client, _get_client_by_request)
                (request, endpoint=get_endpoint(cls._api_name, "prod")))

    @classmethod
    def get_client_by_username(cls, username):
        """通过用户名获取客户端（有用户上下文，推荐在后台任务中使用）"""
        return (_partial(Client, _get_client_by_username)
                (username, endpoint=get_endpoint(cls._api_name, "prod")))

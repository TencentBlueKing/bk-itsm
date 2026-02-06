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
    """蓝鲸权限中心 API 客户端"""

    # 权限申请
    application = bind_property(
        Operation,
        name="application",
        method="POST",
        path="/api/v1/open/application/",
    )
    
    # 新建关联授权 - 属性授权
    resource_creator_action_attribute = bind_property(
        Operation,
        name="resource_creator_action_attribute",
        method="POST",
        path="/api/v1/open/authorization/resource_creator_action_attribute/",
    )

class BkIamApi(ApiProtocol):
    """蓝鲸权限中心 API 协议类"""

    _api_name = "bk-iam"

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


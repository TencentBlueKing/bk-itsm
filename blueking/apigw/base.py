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

import logging

from django.conf import settings
from typing_extensions import Protocol
from bkapi_client_core.client import BaseClient

logger = logging.getLogger('component')


class TenantBaseClient(BaseClient):
    """带租户信息的 API 客户端基类"""

    def handle_request(self, operation, context):
        """重写 handle_request，添加租户id"""
        if context is None:
            context = {}
        
        if context.get("headers") is None:
            context["headers"] = {}
        
        tenant_id = getattr(settings, "BKPAAS_APP_TENANT_ID", "")
        if tenant_id and "X-Bk-Tenant-Id" not in context["headers"]:
            context["headers"]["X-Bk-Tenant-Id"] = tenant_id
        
        return super().handle_request(operation, context)


# APIGW
class ApiProtocol(Protocol):
    def get_client_by_request(self, request):
        raise NotImplementedError

    def get_client_by_username(self, username):
        raise NotImplementedError

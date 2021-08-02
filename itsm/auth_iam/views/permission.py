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

# 当前提供给前端获取用户权限链接使用

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from django.conf import settings
from itsm.component.drf.mixins import ApiGenericMixin
from itsm.component.constants.iam import RESOURCES, ACTIONS, BK_IAM_SYSTEM_NAME, PLATFORM_PERMISSION
from itsm.auth_iam.utils import IamRequest


class PermissionViewSet(ApiGenericMixin, ViewSet):
    @action(detail=False, methods=["post"])
    def query_apply_permission_url(self, request):
        """查询用户无权限的申请链接"""
        iam_client = IamRequest(request)
        url = iam_client.generate_apply_url(request.data)

        return Response({"url": url})

    @action(detail=False, methods=["get"])
    def query_system_verify_perms(self, request):
        iam_client = IamRequest(request)
        verify_actions = ['project_create', "operational_data_view"]
        auth_actions = iam_client.resource_multi_actions_allowed(verify_actions, [])

        return Response(auth_actions)

    @action(detail=False, methods=["get"])
    def meta(self, request):
        auth_meta = {
            "system": [{"id": settings.BK_IAM_SYSTEM_ID, "name": BK_IAM_SYSTEM_NAME}],
            "resources": RESOURCES,
            "actions": ACTIONS,
        }
        return Response(auth_meta)

    @action(detail=False, methods=["get"])
    def platform_permission(self, request):
        iam_client = IamRequest(request)
        verify_actions = PLATFORM_PERMISSION
        auth_actions = iam_client.resource_multi_actions_allowed(verify_actions, [])
        
        return Response(auth_actions)

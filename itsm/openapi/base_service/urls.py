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

from rest_framework.routers import DefaultRouter

from itsm.openapi.base_service.views.apigw import ApiGwViewSet
from itsm.openapi.base_service.views.field import FieldViewSet
from itsm.openapi.base_service.views.postman import PostManViewSet
from itsm.openapi.base_service.views.role import RoleTypeModelViewSet
from itsm.openapi.base_service.views.service import ServiceViewSet
from itsm.openapi.base_service.views.state import StateViewSet
from itsm.openapi.base_service.views.ticket import TicketViewSet
from itsm.openapi.base_service.views.transition import TransitionViewSet
from itsm.openapi.base_service.views.workflow import WorkflowViewSet
from itsm.openapi.base_service.views.workflow_version import WorkflowVersionViewSet

routers = DefaultRouter(trailing_slash=True)

routers.register(r"service", ServiceViewSet, basename="service")
routers.register(r"workflow", WorkflowViewSet, basename="workflow")
routers.register(r"state", StateViewSet, basename="state")
routers.register(r"field", FieldViewSet, basename="field")
routers.register(r"transition", TransitionViewSet, basename="transition")
routers.register(r"role_type", RoleTypeModelViewSet, basename="role_type")
routers.register(r"api_gateway", ApiGwViewSet, basename="api_gateway")
routers.register(
    r"workflow_version", WorkflowVersionViewSet, basename="workflow_version"
)
routers.register(r"ticket", TicketViewSet, basename="ticket")
routers.register(r"postman", PostManViewSet, basename="postman")
urlpatterns = routers.urls

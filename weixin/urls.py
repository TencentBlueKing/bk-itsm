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

from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from itsm.misc.views import download, upload
from itsm.gateway.views import get_batch_users
from weixin.views import (
    WXFieldViewSet,
    WXViewSet,
    WXSysDictViewSet,
    WXCategoryViewSet,
    WXServiceViewSet,
    WXSystemSettingsViewSet,
    WXTaskViewSet,
    WXTicketLogViewSet,
    WXUserRoleViewSet,
    WXRoleTypeViewSet,
    WXRpcApiViewSet,
    WXTicketStatusViewSet,
    WXPriorityMatrixViewSet,
)

routers = DefaultRouter(trailing_slash=True)

routers.register(r"ticket/receipts", WXViewSet, basename="wx_ticket")
routers.register(r"ticket/logs", WXTicketLogViewSet, basename="wx_ticket_log")
routers.register(r"sla/matrixs", WXPriorityMatrixViewSet, basename="sla_matrixs")
routers.register(r"ticket/fields", WXFieldViewSet, basename="wx_ticket_fields")
routers.register(
    r"ticket_status/status", WXTicketStatusViewSet, basename="wx_ticket_status"
)
routers.register(r"role/users", WXUserRoleViewSet, basename="wx_user_roles")
routers.register(r"role/types", WXRoleTypeViewSet, basename="wx_role_types")
routers.register(r"service/datadicts", WXSysDictViewSet, basename="wx_datadicts")
routers.register(
    r"service/categories", WXCategoryViewSet, basename="wx_service_categories"
)
routers.register(r"service/projects", WXServiceViewSet, basename="wx_service_projects")
routers.register(
    r"iadmin/system_settings", WXSystemSettingsViewSet, basename="wx_system_settings"
)
routers.register(r"task/tasks", WXTaskViewSet, basename="wx_tasks")

urlpatterns = routers.urls + [
    url(r"^gateway/", include("itsm.gateway.urls")),
    url(r"^upload_file/$", upload),
    url(r"^download_file/$", download),
    url(r"^postman/rpc_api/$", WXRpcApiViewSet.as_view()),
    url(r"^c/compapi/v2/usermanage/fs_list_users/$", get_batch_users),
]

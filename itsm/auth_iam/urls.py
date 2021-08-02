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

from django.conf import settings
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from iam import IAM
from blueapps.account.decorators import login_exempt
from iam.contrib.django.dispatcher import DjangoBasicResourceApiDispatcher
from itsm.auth_iam.resources.field import FieldResourceProvider
from itsm.auth_iam.resources.public_api import PublicApiResourceProvider
from itsm.auth_iam.resources.public_field import PublicFieldResourceProvider
from itsm.auth_iam.resources.role import RoleResourceProvider
from itsm.auth_iam.resources.service import ServiceResourceProvider
from itsm.auth_iam.resources.service_type import ServiceTypeResourceProvider
from itsm.auth_iam.resources.sla_agreement import SlaAgreementResourceProvider
from itsm.auth_iam.resources.sla_calendar import SlaCalenderResourceProvider
from itsm.auth_iam.resources.task_template import TaskSchemaResourceProvider
from itsm.auth_iam.resources.trigger import TriggerResourceProvider
from itsm.auth_iam.resources.user_group import UserGroupResourceProvider
from itsm.auth_iam.resources.workflow import WorkFlowResourceProvider
from itsm.auth_iam.resources.flow_version import WorkflowVersionResourceProvider
from itsm.auth_iam.views import ResourceViewSet, PermissionViewSet
from itsm.auth_iam.resources import ProjectResourceProvider

iam = IAM(settings.APP_CODE, settings.SECRET_KEY, settings.BK_IAM_INNER_HOST, settings.BK_PAAS_HOST)

routers = DefaultRouter(trailing_slash=True)

routers.register(r"__skip__", ResourceViewSet, basename="skip")
routers.register(r"permission", PermissionViewSet, basename="permissions")

# 注册权限资源接口
dispatcher = DjangoBasicResourceApiDispatcher(iam, settings.BK_IAM_SYSTEM_ID)
dispatcher.register("project", ProjectResourceProvider())
dispatcher.register("workflow", WorkFlowResourceProvider())
dispatcher.register("service", ServiceResourceProvider())
dispatcher.register("flow_version", WorkflowVersionResourceProvider())
dispatcher.register("role", RoleResourceProvider())
dispatcher.register("field", FieldResourceProvider())
dispatcher.register("trigger", TriggerResourceProvider())
dispatcher.register("user_group", UserGroupResourceProvider())
dispatcher.register("sla_agreement", SlaAgreementResourceProvider())
dispatcher.register("sla_calendar", SlaCalenderResourceProvider())
dispatcher.register("public_field", PublicFieldResourceProvider())
dispatcher.register("service_type", ServiceTypeResourceProvider())
dispatcher.register("task_template", TaskSchemaResourceProvider())
dispatcher.register("public_api", PublicApiResourceProvider())
urlpatterns = routers.urls + [
    url(r'^resources/v1/$', dispatcher.as_view([login_exempt])),
]

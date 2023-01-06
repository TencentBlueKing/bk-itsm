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

from django.shortcuts import render
from itsm.role.models import BKUserRole, UserRole
from itsm.service.views import SysDictViewSet, CategoryModelViewSet, ServiceViewSet
from itsm.sla.views import PriorityMatrixViewSet
from itsm.ticket.views import FieldViewSet, TicketModelViewSet
from itsm.ticket.views.event import EventLogViewSet
from itsm.ticket_status.views import TicketStatusViewSet
from itsm.task.views import TaskViewSet
from itsm.iadmin.views import SystemSettingsViewSet
from itsm.postman.views import RpcApiViewSet
from itsm.role.views import UserRoleModelViewSet, RoleTypeModelViewSet
from weixin.core.settings import WEIXIN_APP_EXTERNAL_HOST, WEIXIN_STATIC_URL
from weixin.serializers import WXFieldSerializer


# 目前H5支持的字段类型列表

# H5_FIELD_TYPES = ["STRING", "TEXT", "INT", "DATE", "DATETIME",
#                   "SELECT", "CHECKBOX", "RADIO"]


def index(request):
    """
    首页
    """
    UserRole.update_cmdb_common_roles()
    BKUserRole.get_or_update_user_roles(request.user.username)

    site_url = settings.SITE_URL

    if WEIXIN_APP_EXTERNAL_HOST:
        static_url = "{}static/weixin".format(WEIXIN_APP_EXTERNAL_HOST)
    else:
        static_url = WEIXIN_STATIC_URL.rstrip("/")

    return render(
        request,
        "index_mobile.html",
        {"WEIXIN_STATIC_URL": static_url, "SITE_URL": site_url},
    )


class WXViewSet(TicketModelViewSet):
    pass


class WXFieldViewSet(FieldViewSet):
    serializer_class = WXFieldSerializer


class WXSysDictViewSet(SysDictViewSet):
    pass


class WXCategoryViewSet(CategoryModelViewSet):
    pass


class WXServiceViewSet(ServiceViewSet):
    pass


class WXSystemSettingsViewSet(SystemSettingsViewSet):
    pass


class WXTaskViewSet(TaskViewSet):
    pass


class WXTicketLogViewSet(EventLogViewSet):
    pass


class WXPriorityMatrixViewSet(PriorityMatrixViewSet):
    pass


class WXUserRoleViewSet(UserRoleModelViewSet):
    pass


class WXRoleTypeViewSet(RoleTypeModelViewSet):
    pass


class WXRpcApiViewSet(RpcApiViewSet):
    pass


class WXTicketStatusViewSet(TicketStatusViewSet):
    pass

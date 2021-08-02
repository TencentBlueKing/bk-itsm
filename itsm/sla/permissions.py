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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

from django.utils.translation import ugettext as _
from rest_framework import permissions

from itsm.component.drf.permissions import IamAuthPermit, IamAuthWithoutResourcePermit
from itsm.role.models import UserRole


class IsAdmin(permissions.BasePermission):
    """
    判断登陆人员是否有对应的权限
    """

    message = _("您没有该模块的权限")

    def has_permission(self, request, view):

        if UserRole.is_itsm_superuser(request.user.username):
            return True

        # 对GET方法豁免，存在接口信息越权的问题！
        if request.method in permissions.SAFE_METHODS:
            return True

        # 提单环节拉取优先级
        if view.action in ['priority_value']:
            return True

        return False

    def has_object_permission(self, request, view, obj):

        if UserRole.is_itsm_superuser(request.user.username):
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return False


class SlaPermit(IamAuthPermit):

    def has_object_permission(self, request, view, obj, **kwargs):
        # 关联实例的请求，需要针对对象进行鉴权
        if view.action in getattr(view, "permission_free_actions", []):
            return True

        if view.action in ["retrieve"]:
            apply_actions = ["sla_agreement_view"]
        elif view.action in ["destroy"]:
            apply_actions = ["sla_agreement_delete"]
        elif view.action in ["update"]:
            apply_actions = ["sla_agreement_edit"]

        return self.iam_auth(request, apply_actions, obj)
    
    
class SchedulePermit(IamAuthPermit):
    
    def has_object_permission(self, request, view, obj, **kwargs):
        # 关联实例的请求，需要针对对象进行鉴权
        if view.action in getattr(view, "permission_free_actions", []):
            return True

        if view.action in ["retrieve"]:
            apply_actions = ["sla_calendar_view"]
        elif view.action in ["destroy"]:
            apply_actions = ["sla_calendar_delete"]
        elif view.action in ["update"]:
            apply_actions = ["sla_calendar_edit"]

        return self.iam_auth(request, apply_actions, obj)
    
    
class SlaMatrixPermit(IamAuthWithoutResourcePermit):
    def has_permission(self, request, view):
        if view.action == "matrix_of_service_type":
            apply_actions = ["sla_priority_view", "platform_manage_access"]
        else:
            apply_actions = ["sla_priority_manage"]
        
        return self.iam_auth(request, apply_actions)
    
    
    
    
    

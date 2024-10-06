# coding=utf-8
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

from functools import wraps

from django.utils.translation import ugettext as _
from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed

from common.mymako import render_mako
from itsm.component.constants import PUBLIC_PROJECT_PROJECT_KEY
from itsm.component.drf.permissions import IamAuthWithoutResourcePermit, IamAuthPermit
from itsm.project.models import Project
from itsm.role.models import UserRole


class IsSuperuser(permissions.BasePermission):
    """
    判断登陆人员是否有对应的权限
    """

    message = _("您没有该模块的权限")

    def has_permission(self, request, view):
        return UserRole.is_itsm_superuser(request.user.username)


class IsSuperOperator(permissions.BasePermission):
    """
    判断登陆人员是否有对应的权限
    """

    message = _("您没有该模块的操作权限")

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return UserRole.is_itsm_superuser(request.user.username)


class IsMigrateSuperuser(permissions.BasePermission):
    """
    判断登陆人员是否有对应的权限
    """

    message = _("您没有权限")

    def has_permission(self, request, view):

        if UserRole.is_itsm_superuser(request.user.username):
            return True

        # 对GET方法豁免，存在接口信息越权的问题！
        if request.method in permissions.SAFE_METHODS:
            return True

        return False


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

        return False

    def has_object_permission(self, request, view, obj):

        if UserRole.is_itsm_superuser(request.user.username):
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return False


def superuser_permissions(view_func):
    """
    判断登陆人员是否有对应的权限
    """

    @wraps(view_func)
    def __wrapper(request, *args, **kwargs):
        if not UserRole.is_itsm_superuser(request.user.username):
            return render_mako("403.html")

        return view_func(request, *args, **kwargs)

    return __wrapper


class SystemSettingPermit(IamAuthWithoutResourcePermit):
    def has_permission(self, request, view):
        if view.action == "list":
            apply_actions = []
        else:
            apply_actions = ["global_settings_manage", "platform_manage_access"]

        return self.iam_auth(request, apply_actions)


class CustomNotifyPermit(IamAuthPermit):
    def has_permission(self, request, view):
        if view.action in getattr(view, "permission_free_actions", []):
            return True
        
        # 获取项目标识
        if view.action in ["list"]:
            project_key = request.query_params.get("project_key", PUBLIC_PROJECT_PROJECT_KEY)
        elif view.action in ["destroy"]:
            instance = view.get_object()
            project_key = instance.project_key
        else:
            project_key = request.data.get("project_key", PUBLIC_PROJECT_PROJECT_KEY)
            
        # 平台管理
        if project_key == PUBLIC_PROJECT_PROJECT_KEY:
            # 平台管理限制创建新通知规则
            if view.action == "create":
                raise MethodNotAllowed(request.method)
            apply_actions = ["notification_view", "platform_manage_access"]
            return self.iam_auth(request, apply_actions)
        
        # 项目管理
        project = Project.objects.get(pk=project_key)
        apply_actions = ["system_settings_manage"]
        return self.iam_auth(request, apply_actions, project)

    def has_object_permission(self, request, view, obj, **kwargs):
        # 平台管理：通知配置
        if obj.project_key == PUBLIC_PROJECT_PROJECT_KEY:
            # 平台管理限制删除
            if view.action in ["destroy"]:
                raise MethodNotAllowed(request.method)
            
            apply_actions = ["notification_view", "platform_manage_access"]
            if view.action in ["update"]:
                apply_actions.append("notification_manage")
            return self.iam_auth(request, apply_actions)
        
        # 项目：通知配置
        project = Project.objects.filter(pk=obj.project_key).first()
        return super().has_object_permission(request, view, project, **kwargs)

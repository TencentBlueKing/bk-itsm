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

from django.utils.translation import ugettext as _
from rest_framework import permissions

from iam import Subject, Action, Resource
from iam.exceptions import AuthFailedException
from itsm.component.constants import (
    DEFAULT_PROJECT_PROJECT_KEY,
    PUBLIC_PROJECT_PROJECT_KEY,
)
from itsm.component.constants.iam import BK_IAM_SYSTEM_ID
from itsm.auth_iam.utils import IamRequest
from itsm.component.exceptions import ProjectNotFound
from itsm.project.models import Project
from itsm.role.models import UserRole
from itsm.workflow.models import TemplateField


class IsAdmin(permissions.BasePermission):
    """
    放开查询接口，其他方法仅限管理员
    """

    message = _("您没有该模块的权限")

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if UserRole.is_itsm_superuser(request.user.username):
            return True

        return False


class IsManager(permissions.BasePermission):
    """
    给流程管理员和资源负责人豁免权限
    """

    message = _("您没有该模块的权限")

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if UserRole.is_itsm_superuser(request.user.username):
            return True

        return UserRole.is_workflow_manager(request.user.username)

    def has_object_permission(self, request, view, obj):
        if UserRole.is_itsm_superuser(request.user.username):
            return True

        return obj.is_obj_manager(request.user.username)


class IamAuthPermit(permissions.BasePermission):
    """
    权限中心鉴权
    """

    message = _("您没有该模块的权限")

    def has_permission(self, request, view):
        # 不关联实例的资源，任何请求都要提前鉴权
        # 当前系统内，如果没有project_view的权限，无法进入系统
        if view.action in getattr(view, "permission_free_actions", []):
            return True

        # apply_actions = ["project_view"]
        apply_actions = []
        resource_type = getattr(view.queryset.model, "auth_resource", {}).get(
            "resource_type"
        )

        if view.action == "create":
            apply_actions.append("{}_create".format(resource_type))
            if "project_key" in request.data:
                return self.iam_create_auth(request, apply_actions)

        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        # 关联实例的请求，需要针对对象进行鉴权
        if view.action in getattr(view, "permission_free_actions", []):
            return True

        apply_actions = obj.resource_operations
        return self.iam_auth(request, apply_actions, obj)

    def iam_auth(self, request, apply_actions, obj=None):

        resources = []
        if obj:
            if isinstance(obj, Project):
                resource_id = (str(getattr(obj, "key")),)
            else:
                resource_id = str(getattr(obj, "id"))

            resource_type = obj.auth_resource["resource_type"]

            if isinstance(obj, TemplateField):
                if obj.project_key == PUBLIC_PROJECT_PROJECT_KEY:
                    resource_type = "public_field"
            resources.append(
                {
                    "resource_id": resource_id,
                    "resource_name": getattr(obj, "name"),
                    "resource_type": resource_type,
                    "creator": obj.creator,
                }
            )

        iam_client = IamRequest(request)

        project_key = DEFAULT_PROJECT_PROJECT_KEY

        if resources:
            if hasattr(obj, "project_key"):
                project_key = getattr(obj, "project_key")
            auth_actions = iam_client.batch_resource_multi_actions_allowed(
                set(apply_actions), resources, project_key=project_key
            )
            auth_actions = auth_actions.get(resources[0]["resource_id"], {})
        else:
            auth_actions = iam_client.resource_multi_actions_allowed(apply_actions, [])

        if self.auth_result(auth_actions, apply_actions):
            return True

        if resources:
            if hasattr(obj, "project_key"):
                project_key = getattr(obj, "project_key")

        resources = [
            Resource(
                BK_IAM_SYSTEM_ID,
                resource["resource_type"],
                str(resource["resource_id"]),
                {
                    "iam_resource_owner": resource.get("creator", ""),
                    "_bk_iam_path_": "/project,{}/".format(project_key)
                    if resource["resource_type"] != "project"
                    else "",
                    "name": resource.get("resource_name", ""),
                },
            )
            for resource in resources
        ]

        no_permission_actions = [
            action for action, result in auth_actions.items() if not result
        ]

        raise AuthFailedException(
            BK_IAM_SYSTEM_ID,
            Subject("user", request.user.username),
            Action(no_permission_actions[0]),
            resources,
        )

    def iam_create_auth(self, request, apply_actions):
        resources = []
        project_key = request.data["project_key"]
        project = self.get_project(project_key)
        resources.append(
            {
                "resource_id": project_key,
                "resource_name": self.get_project(project_key=project_key).name,
                "resource_type": "project",
                "creator": project.creator,
            }
        )
        iam_client = IamRequest(request)
        auth_actions = iam_client.batch_resource_multi_actions_allowed(
            set(apply_actions), resources, project_key
        )
        auth_actions = auth_actions.get(resources[0]["resource_id"], {})

        if self.auth_result(auth_actions, apply_actions):
            return True

        bk_iam_path = "/project,{}/".format(project_key)

        resources = [
            Resource(
                BK_IAM_SYSTEM_ID,
                resource["resource_type"],
                str(resource["resource_id"]),
                {
                    "iam_resource_owner": resource.get("creator", ""),
                    "_bk_iam_path_": bk_iam_path
                    if resource["resource_type"] != "project"
                    else "",
                    "name": resource.get("resource_name", ""),
                },
            )
            for resource in resources
        ]

        no_permission_actions = [
            action for action, result in auth_actions.items() if not result
        ]

        raise AuthFailedException(
            BK_IAM_SYSTEM_ID,
            Subject("user", request.user.username),
            Action(no_permission_actions[0]),
            resources,
        )

    @staticmethod
    def auth_result(auth_actions, actions):
        """
        认证结果解析
        """
        denied_actions = []
        for action, result in auth_actions.items():
            if action in actions and result is False:
                denied_actions.append(action)
        return len(denied_actions) == 0

    @staticmethod
    def is_safe_method(request, view):
        return (
            getattr(view, "enable_safe_method", True)
            and request.method in permissions.SAFE_METHODS
        )

    def get_project(self, project_key):
        try:
            return Project.objects.get(key=project_key)
        except Exception:
            raise ProjectNotFound()


class IamAuthWithoutResourcePermit(IamAuthPermit):
    def has_permission(self, request, view):
        if self.is_safe_method(request, view) and view.detail is False:
            # 非详情内容，可以直接通过
            return True

        apply_actions = ["project_view"]
        auth_resource = getattr(view.queryset.model, "auth_resource", {})
        if auth_resource:
            apply_actions.append("{}_manage".format(auth_resource.get("resource_type")))

        return self.iam_auth(request, apply_actions)

    def has_object_permission(self, request, view, obj):
        return True


class IamAuthProjectViewPermit(IamAuthPermit):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "project_key"):
            project_key = obj.project_key
            apply_actions = ["project_view"]
            return self.has_project_view_permission(request, project_key, apply_actions)

        return True

    def has_project_view_permission(self, request, project_key, apply_actions):
        resources = []
        project = self.get_project(project_key)
        resources.append(
            {
                "resource_id": project_key,
                "resource_name": project.name,
                "resource_type": "project",
                "creator": project.creator,
            }
        )
        iam_client = IamRequest(request)
        auth_actions = iam_client.batch_resource_multi_actions_allowed(
            set(apply_actions), resources, project_key
        )
        auth_actions = auth_actions.get(resources[0]["resource_id"], {})

        if self.auth_result(auth_actions, apply_actions):
            return True

        bk_iam_path = "/project,{}/".format(project_key)

        resources = [
            Resource(
                BK_IAM_SYSTEM_ID,
                resource["resource_type"],
                str(resource["resource_id"]),
                {
                    "iam_resource_owner": resource.get("creator", ""),
                    "_bk_iam_path_": bk_iam_path
                    if resource["resource_type"] != "project"
                    else "",
                    "name": resource.get("resource_name", ""),
                },
            )
            for resource in resources
        ]

        no_permission_actions = [
            action for action, result in auth_actions.items() if not result
        ]

        raise AuthFailedException(
            BK_IAM_SYSTEM_ID,
            Subject("user", request.user.username),
            Action(no_permission_actions[0]),
            resources,
        )


class IamAuthSystemPermit(IamAuthWithoutResourcePermit):
    """
    系统权限鉴权
    """

    def has_permission(self, request, view):
        apply_actions = ["operational_data_view"]
        return self.iam_auth(request, apply_actions)

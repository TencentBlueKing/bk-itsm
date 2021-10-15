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

from itsm.component.constants import PUBLIC_PROJECT_PROJECT_KEY
from itsm.component.drf.permissions import IamAuthPermit
from itsm.role.models import UserRole
from itsm.service.models import Service


class IsTableAdmin(permissions.BasePermission):
    """
    基础模型权限，目前为管理员权限
    """

    message = _("抱歉，您没有基础模型编辑的权限，请联系管理员添加")

    def has_object_permission(self, request, view, obj):
        username = request.user.username
        return UserRole.is_itsm_superuser(username)


class IsWorkflowAdmin(permissions.BasePermission):
    """
    建流程权限
    """

    message = _("抱歉，您没有流程编辑的权限，请联系管理员添加")

    def has_object_permission(self, request, view, obj):
        username = request.user.username

        if UserRole.is_itsm_superuser(username):
            return True

        # 流程创建者和负责人
        return obj.is_obj_manager(username)


class IsStateFieldAdmin(permissions.BasePermission):
    """
    配置节点/节点字段的权限,依据是是否有该服务流程的创建权限
    """

    message = _("对不起，您未拥有相应权限，请联系管理员添加")

    def has_object_permission(self, request, view, obj):
        username = request.user.username

        if UserRole.is_itsm_superuser(username):
            return True

        if view.action == "download_file":
            # 下载文件不需要做对应的权限校验
            return True

        return obj.workflow.is_obj_manager(username)


class BaseWorkflowElementIamAuth(IamAuthPermit):
    """
    对应流程下的字段、线条和节点的权限控制
    """

    def has_permission(self, request, view):
        # apply_actions = ["service_manage", "service_view"]
        #
        # # 节点和字段的查看，首先必须有当前流程的管理权限
        # if not view.action == 'list':
        #     # 非列表请求，通过object鉴权
        #     return True
        #
        # workflow_id = request.query_params.get("workflow")
        # if workflow_id is None:
        #     return False
        # try:
        #     flow = Workflow.objects.get(id=workflow_id)
        # except Workflow.DoesNotExist:
        #     return False
        # service_obj = flow.service
        #
        # return self.iam_auth(request, apply_actions, service_obj)
        return True

    def has_object_permission(self, request, view, obj):
        """
        操作单个资源的权限
        :param request:
        :param view:
        :param obj:
        :return:
        """
        # apply_actions = ["service_manage", "service_view"]
        # service_obj = obj.workflow
        # return self.iam_auth(request, apply_actions, service_obj)
        return True


class ServiceViewPermit(IamAuthPermit):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        # if view.action in ["deploy", "update"]:
        #     apply_actions = ["service_manage", "service_view"]
        #     service_obj = obj.service
        #     return self.iam_auth(request, apply_actions, service_obj)

        return True


class WorkflowIamAuth(ServiceViewPermit):
    pass


class VersionDeletePermit(permissions.BasePermission):
    """
    流程版本删除校验
    """

    message = _("流程版本占用中，请到服务中解绑后再删除")

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        # 以下逻辑是属于校验的内容，但是居然写到了权限里边[捂脸]

        if view.action == "batch_delete":
            id_list = [i for i in request.data.get("id").split(",") if i.isdigit()]
            return not Service.objects.filter(workflow__in=id_list).exists()

        if view.action == "destroy":
            return not Service.objects.filter(
                workflow=request.parser_context["kwargs"].get("pk")
            ).exists()

        return True

    def has_object_permission(self, request, view, obj):
        return True


class FlowVersionIamAuth(ServiceViewPermit):
    def has_object_permission(self, request, view, obj):
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        #
        # apply_actions = ["service_manage", "service_view"]
        # service_obj = Workflow.objects.get(obj.workflow_id).service
        # return self.iam_auth(request, apply_actions, service_obj)
        return True


class IsSuperuser(permissions.BasePermission):
    """
    判断登陆人员是否有对应的权限
    """

    message = _("您没有该模块的权限")

    def has_permission(self, request, view):
        return UserRole.is_itsm_superuser(request.user.username)


class TemplateFieldPermissionValidate(IamAuthPermit):
    def has_permission(self, request, view):
        # 不关联实例的资源，任何请求都要提前鉴权
        # 当前系统内，如果没有project_view的权限，无法进入系统
        if view.action in getattr(view, "permission_free_actions", []):
            return True

        apply_actions = []
        resource_type = getattr(view.queryset.model, "auth_resource", {}).get(
            "resource_type"
        )

        if view.action == "create":
            if request.data.get("project_key", None) == PUBLIC_PROJECT_PROJECT_KEY:
                apply_actions.append("public_field_create")
                return self.iam_auth(request, apply_actions)
            else:
                apply_actions.append("{}_create".format(resource_type))
            if "project_key" in request.data:
                return self.iam_create_auth(request, apply_actions)

        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        # 关联实例的请求，需要针对对象进行鉴权
        if view.action in getattr(view, "permission_free_actions", []):
            return True

        fields_action_map = {
            "retrieve": ["field_view"],
            "destroy": ["field_delete"],
            "update": ["field_edit"],
        }

        public_fields_action_map = {
            "retrieve": ["public_field_view"],
            "destroy": ["public_field_delete"],
            "update": ["public_field_edit"],
        }
        apply_actions = []
        if view.action in ["retrieve", "destroy", "update"]:
            apply_actions = fields_action_map[view.action]
            if obj.project_key == PUBLIC_PROJECT_PROJECT_KEY:
                apply_actions = public_fields_action_map[view.action]

        return self.iam_auth(request, apply_actions, obj)


class TaskSchemaPermit(IamAuthPermit):
    def has_permission(self, request, view):

        apply_actions = []
        if view.action == "create":
            apply_actions = ["task_template_create"]

        return self.iam_auth(request, apply_actions)

    def has_object_permission(self, request, view, obj, **kwargs):

        if view.action == "retrieve":
            apply_actions = ["task_template_view"]
        else:
            apply_actions = ["task_template_manage"]

        return self.iam_auth(request, apply_actions, obj)

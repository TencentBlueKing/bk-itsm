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

from itsm.component.constants import PUBLIC_PROJECT_PROJECT_KEY
from itsm.component.drf import permissions as perm
from itsm.component.exceptions import ValidateError
from itsm.postman.models import RemoteSystem, RemoteApi, RemoteApiInstance
from django.utils.translation import gettext as _

from itsm.project.models import Project
from itsm.workflow.models import Workflow
from itsm.workflow.permissions import WorkflowElementManagePermission

# 流程编排型 RPC 组件的 source_uri 集合，这些组件依赖 workflow 上下文
WORKFLOW_RPC_SOURCES = frozenset(["state_fields", "table_fields", "flow_states"])


class IsObjManager(perm.IsManager):
    """
    负责人
    """

    pass


class RpcApiPermit(perm.IamAuthPermit):
    """
    /api/postman/rpc_api/ 权限控制：
    - GET：登录态可读（获取 RPC 组件列表，无敏感数据）
    - POST：
        - source_uri 属于流程编排型（state_fields / table_fields / flow_states）
          且 trigger_source_type=workflow 时，校验对应 workflow 的 service_manage 权限
        - 其他 source_uri（ticket_status / service_catalog 等）：登录态可访问
    """

    def has_permission(self, request, view):
        # GET 请求：登录态可读
        if request.method in ("GET",):
            return True

        # POST 请求：按 source_uri 分类鉴权
        source_uri = request.data.get("source_uri", "")

        # 非流程编排型组件，登录态可访问
        if source_uri not in WORKFLOW_RPC_SOURCES:
            return True

        # 流程编排型组件：必须带 trigger_source_type=workflow + trigger_source_id
        trigger_source_type = request.data.get("trigger_source_type", "")
        trigger_source_id = request.data.get("trigger_source_id")

        if trigger_source_type != "workflow" or not trigger_source_id:
            # 参数不合法，直接拒绝，避免绕过鉴权
            return False

        try:
            flow = Workflow.objects.get(id=trigger_source_id)
        except Workflow.DoesNotExist:
            return False

        return self.iam_auth(request, ["service_manage"], flow.get_iam_resource())


class RemoteApiPermit(WorkflowElementManagePermission):
    def has_permission(self, request, view):
        if view.action in getattr(view, "permission_action_mapping", {}):
            # 项目查看的权限
            project_key = request.query_params.get(
                "project_key", PUBLIC_PROJECT_PROJECT_KEY
            )
            if project_key == PUBLIC_PROJECT_PROJECT_KEY:
                return True
            project = Project.objects.get(pk=project_key)
            apply_actions = self.get_view_iam_actions(view)
            return self.iam_auth(request, apply_actions, project)

        if view.action in getattr(view, "permission_create_action", ["create"]):
            if "remote_system" in request.data:
                remote_system_id = request.data["remote_system"]
                project_key = RemoteSystem.objects.get(id=remote_system_id).project_key
                # 平台公共API管理
                if project_key == PUBLIC_PROJECT_PROJECT_KEY:
                    return self.iam_auth(request, ["public_apis_manage"])

                # 项目管理
                apply_actions = ["system_settings_manage"]
                project = Project.objects.get(pk=project_key)
                return self.iam_auth(request, apply_actions, project)

        if view.action == "batch_delete":
            api_ids = request.data["id"].split(",")
            api_instances = RemoteApi.objects.filter(pk__in=api_ids)
            project_keys = set([i.remote_system.project_key for i in api_instances])
            if len(project_keys) != 1:
                raise ValidateError(_("API 所属项目异常"))
            project_key = project_keys.pop()

            # 平台公共API管理
            if project_key == PUBLIC_PROJECT_PROJECT_KEY:
                return self.iam_auth(request, ["public_apis_manage"])

            # 项目
            project = Project.objects.get(pk=project_key)
            return self.iam_auth(request, ["system_settings_manage"], project)

        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        if view.action in getattr(view, "permission_free_actions", []):
            return True

        if obj:
            # retrieve / run_api：调试与查看动作走最低门槛
            #   - 平台公共 API：登录态可读/可调试（不要求 public_apis_manage）
            #   - 项目 API：要求 project_view，避免他项目成员越权调用项目的第三方接口
            view_like_actions = ("retrieve", "run_api")

            # 平台公共 API 管理
            if obj.remote_system.project_key == PUBLIC_PROJECT_PROJECT_KEY:
                if view.action in view_like_actions:
                    return True
                return self.iam_auth(request, ["public_apis_manage"])

            # 项目管理
            project_key = obj.remote_system.project_key
            project = Project.objects.get(pk=project_key)
            apply_actions = ["system_settings_manage"]
            if view.action in view_like_actions:
                apply_actions = ["project_view"]
                return self.iam_auth(request, apply_actions, project)
        return True


class RemoteApiInstancePermit(RemoteApiPermit):
    def has_permission(self, request, view):
        if view.action in getattr(view, "permission_create_action", ["create"]):
            remote_api_id = request.data.get("remote_api") or request.data.get(
                "remote_api_id"
            )
            if remote_api_id:
                remote_api = RemoteApi.objects.get(id=remote_api_id)
                obj = RemoteApiInstance(remote_api=remote_api)
                return self.has_object_permission(request, view, obj)

        return super(RemoteApiInstancePermit, self).has_permission(request, view)

    def has_object_permission(self, request, view, obj, **kwargs):
        remote_api = None
        if obj:
            remote_api = getattr(obj, "remote_api", None) or obj

        if remote_api is None:
            return True

        return super(RemoteApiInstancePermit, self).has_object_permission(
            request, view, remote_api, **kwargs
        )

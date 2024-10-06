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

from itsm.component.constants import PUBLIC_PROJECT_PROJECT_KEY
from itsm.component.drf import permissions as perm
from itsm.component.exceptions import ValidateError
from itsm.postman.models import RemoteSystem, RemoteApi
from django.utils.translation import ugettext as _

from itsm.project.models import Project
from itsm.workflow.permissions import WorkflowElementManagePermission


class IsObjManager(perm.IsManager):
    """
    负责人
    """

    pass


class RemoteApiPermit(WorkflowElementManagePermission):
    def has_permission(self, request, view):
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
            # 平台公共 API 管理
            if obj.remote_system.project_key == PUBLIC_PROJECT_PROJECT_KEY:
                if view.action == "retrieve":
                    return True
                return self.iam_auth(request, ["public_apis_manage"])
            
            # 项目管理
            project_key = obj.remote_system.project_key
            project = Project.objects.get(pk=project_key)
            return self.iam_auth(request, ["system_settings_manage"], project)
        return True

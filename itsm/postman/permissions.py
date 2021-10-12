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
from itsm.postman.models import RemoteSystem


class IsObjManager(perm.IsManager):
    """
    负责人
    """

    pass


class RemoteApiPermit(perm.IamAuthProjectViewPermit):
    def has_permission(self, request, view):
        if view.action == "create":
            if "remote_system" in request.data:
                remote_system_id = request.data["remote_system"]
                project_key = RemoteSystem.objects.get(id=remote_system_id).project_key
                if project_key == PUBLIC_PROJECT_PROJECT_KEY:
                    apply_actions = ["public_api_view"]
                    return self.iam_auth(request, apply_actions)
        return True

    def has_object_permission(self, request, view, obj):
        if obj is not None:
            # 如果是公共api需要单独鉴权
            if obj.remote_system.project_key == PUBLIC_PROJECT_PROJECT_KEY:
                if view.action == "retrieve":
                    apply_actions = []
                else:
                    apply_actions = ["public_api_manage"]
                return self.iam_auth(request, apply_actions, obj)
            else:
                # 项目
                project_key = obj.remote_system.project_key
                apply_actions = ["project_view"]
                return self.has_project_view_permission(
                    request, project_key, apply_actions
                )
        return True

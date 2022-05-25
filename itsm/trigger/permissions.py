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

from django.http import Http404
from itsm.component.drf.permissions import IamAuthPermit
from itsm.component.constants.trigger import SOURCE_WORKFLOW
from itsm.workflow.models import Workflow


class WorkflowTriggerPermit(IamAuthPermit):
    @staticmethod
    def get_flow_or_raise_error(workflow_id):
        try:
            return Workflow.objects.get(id=workflow_id)
        except Workflow.DoesNotExist:
            raise Http404("对应的流程不存在，无法操作")

    @staticmethod
    def create_trigger_from_workflow(request, view):
        return (
            view.action == "create"
            and request.data.get("source_type") == SOURCE_WORKFLOW
        )

    @staticmethod
    def clone_trigger_to_workflow(request, view):
        return (
            view.action == "clone"
            and request.data.get("dst_source_type") == SOURCE_WORKFLOW
        )

    def has_permission(self, request, view):
        if self.is_safe_method(request, view) and view.detail is False:
            # 非详情内容，可以直接通过
            return True

        if view.action in ["clone", "create"]:
            # 其他的引用和创建，都需要尽心给流程元素的鉴权:
            return self.iam_create_auth(request, apply_actions=["triggers_create"])

        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        # 关联实例的请求，需要针对对象进行鉴权
        if view.action in getattr(view, "permission_free_actions", []):
            return True
        if view.action in ["create_or_update_rules", "update", "destroy"]:
            return True

        apply_actions = ["triggers_manage"]

        return self.iam_auth(request, apply_actions, obj)

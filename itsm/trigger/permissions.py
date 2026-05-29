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

from django.http import Http404
from rest_framework import permissions

from itsm.component.constants import PUBLIC_PROJECT_PROJECT_KEY
from itsm.component.constants.trigger import SOURCE_WORKFLOW, SOURCE_TASK
from itsm.component.drf.permissions import IamAuthPermit
from itsm.project.models import Project
from itsm.ticket.models import Ticket
from itsm.ticket.permissions import TicketPermissionValidate
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

    def _check_target_write_permission(self, request, dst_source_type, dst_source_id):
        """clone 的目标侧写入权限：要求对 dst 资源具备管理权限。"""
        if dst_source_type == SOURCE_WORKFLOW:
            try:
                workflow = Workflow.objects.get(id=dst_source_id)
            except Workflow.DoesNotExist:
                raise Http404("对应的流程不存在，无法操作")
            return self.iam_auth(
                request, ["service_manage"], workflow.get_iam_resource()
            )
        if dst_source_type == SOURCE_TASK:
            return self.iam_auth(request, ["public_task_template_manage"])
        return self.iam_create_auth(request, apply_actions=["triggers_create"])

    def _check_source_read_permission(self, request, view, src_trigger_ids):
        """clone 的源侧读取权限：逐个 trigger 复用 retrieve 分支语义。"""
        from itsm.trigger.models import Trigger

        if not src_trigger_ids:
            return False
        triggers = list(Trigger.objects.filter(id__in=src_trigger_ids))
        if len(triggers) != len(set(src_trigger_ids)):
            return False
        for trigger in triggers:
            if trigger.source_type == SOURCE_WORKFLOW:
                try:
                    workflow = Workflow.objects.get(id=trigger.source_id)
                except Workflow.DoesNotExist:
                    return False
                if not self.iam_auth(
                    request, ["service_manage"], workflow.get_iam_resource()
                ):
                    return False
                continue
            if trigger.source_type == SOURCE_TASK:
                if not self.iam_auth(request, ["public_task_template_manage"]):
                    return False
                continue
            if not self.iam_auth(request, ["triggers_view"], trigger):
                return False
        return True

    def has_permission(self, request, view):
        if view.action in getattr(view, "permission_action_mapping", {}):
            # 项目查看的权限
            project_key = request.query_params.get("project_key") or PUBLIC_PROJECT_PROJECT_KEY
            project = Project.objects.get(pk=project_key)
            apply_actions = self.get_view_iam_actions(view)
            return self.iam_auth(request, apply_actions, project)

        if view.action == "clone":
            # clone 接口 payload 与 create 不同：dst_source_type / dst_source_id / src_trigger_ids。
            # 必须分别校验"目标侧写权限"和"源侧读权限"，避免任意登录用户向他人流程注入触发器。
            dst_source_type = request.data.get("dst_source_type")
            dst_source_id = request.data.get("dst_source_id")
            src_trigger_ids = request.data.get("src_trigger_ids") or []
            if not self._check_target_write_permission(
                request, dst_source_type, dst_source_id
            ):
                return False
            return self._check_source_read_permission(request, view, src_trigger_ids)

        if view.action == "create":
            # 通过流程配置需要有对应服务的管理权限
            source_type = request.data.get("source_type")
            if source_type == SOURCE_WORKFLOW:
                # 修复点（H7）：原实现 `Workflow.objects.get(id=...)` 未捕获 DoesNotExist，
                # 任意登录用户传入随机 source_id 即可让接口抛 500，且响应体可能携带
                # 模型/字段细节；同时缺少"项目归属"语义（仅靠 IAM service_manage 兜底）。
                # 这里改为：
                #   1) 通过 get_flow_or_raise_error 统一返回 Http404，避免存在性差异；
                #   2) 借助 workflow.get_iam_resource() 走 IAM service_manage 校验。
                workflow = self.get_flow_or_raise_error(request.data.get("source_id"))
                apply_actions = ["service_manage"]
                return self.iam_auth(
                    request, apply_actions, workflow.get_iam_resource()
                )

            # 通过任务模板创建
            if source_type == SOURCE_TASK:
                apply_actions = ["public_task_template_manage"]
                return self.iam_auth(request, apply_actions)

            # 其他的引用和创建，都需要尽心给流程元素的鉴权:
            return self.iam_create_auth(request, apply_actions=["triggers_create"])

        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        # 关联实例的请求，需要针对对象进行鉴权
        if view.action in getattr(view, "permission_free_actions", []):
            return True

        if view.action in ["retrieve"]:
            apply_actions = ["triggers_view"]
        else:
            # 通过流程配置需要有对应服务的管理权限
            is_workflow = False
            workflow_id = None
            if obj.source_type == SOURCE_WORKFLOW:
                is_workflow = True
                workflow_id = obj.source_id

            if is_workflow:
                # 修复点（H7）：与 has_permission 一致，统一通过 get_flow_or_raise_error
                # 转 404，避免 DoesNotExist 直透到响应体。
                workflow = self.get_flow_or_raise_error(workflow_id)
                apply_actions = ["service_manage"]
                return self.iam_auth(
                    request, apply_actions, workflow.get_iam_resource()
                )

            # 通过任务模板创建
            if obj.source_type == SOURCE_TASK:
                apply_actions = ["public_task_template_manage"]
                return self.iam_auth(request, apply_actions)

            apply_actions = ["triggers_manage"]

        return self.iam_auth(request, apply_actions, obj)


class TicketTriggerPermit(TicketPermissionValidate):
    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request, view, obj, **kwargs):
        if obj.source_type != "ticket":
            return True
        
        ticket = Ticket.objects.get(id=obj.source_id)
        # 查看权限校验
        username = request.user.username
        if request.method in permissions.SAFE_METHODS or view.action in ["params"]:
            if ticket.can_view(username):
                return True
            return self.iam_ticket_view_auth(request, ticket)
        
        # 操作权限：非 can_operate 角色一律拒绝写动作，避免任意登录用户改单据触发器
        if ticket.can_operate(username):
            return True

        return False

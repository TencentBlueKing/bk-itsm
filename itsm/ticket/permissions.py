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
from django.conf import settings
from rest_framework import permissions
from rest_framework.serializers import ValidationError

from iam import Action, Resource, Subject
from iam.exceptions import AuthFailedException
from itsm.auth_iam.utils import IamRequest
from itsm.role.models import UserRole
from itsm.service.models import Service

from .models import Ticket
from ..project.models import Project


class SuperuserPermissionValidate(permissions.BasePermission):
    """
    超级管理员查看权限
    """

    def __init__(self):
        self.message = _("抱歉，您无权查看和操作")

    def has_object_permission(self, request, view, obj):
        username = request.user.username
        if UserRole.is_itsm_superuser(username):
            return True
        return False


class TicketPermissionValidate(permissions.BasePermission):
    """
    工单查看权限
    """

    def __init__(self):
        self.message = _("抱歉，您无权查看该单据")

    def has_object_permission(self, request, view, obj):

        username = request.user.username

        # 函数内实现的，超级管理员的放最前面
        # 单据正常处理/撤销/通知关注人的权限在函数体内实现, 超级管理员直接返回，不需要鉴权
        if view.action in [
            "proceed",
            "withdraw",
            "notify",
            "send_sms",
            "send_email",
            "master_or_slave",
            "add_follower",
            "can_exception_distribute",
        ]:
            return True

        if request.method not in permissions.SAFE_METHODS and (
            obj.is_slave or obj.status_instance.is_over
        ):
            # 单据无法操作的情况暂时放在这里
            raise ValidationError(_("抱歉，当前单据无法操作"))

        # 权限校验 与 业务逻辑校验混在了一起
        if view.action == "close" and obj.can_close(username):
            return True

        iam_ticket_manage_auth = self.iam_ticket_manage_auth(request, obj)

        if view.action == "exception_distribute":
            if not iam_ticket_manage_auth:
                self.message = _("抱歉，您无权执行此操作，因为您该服务没有工单管理的权限")
                return False
            else:
                return True

        if view.action == "operate":
            try:
                node = obj.node_status.get(state_id=request.data.get("state_id"))
            except Exception:
                # 异常情况直接返回
                return False
            state_permission = StatePermissionValidate().has_object_permission(
                request, node
            )

            return any([state_permission, iam_ticket_manage_auth])

        if view.action == "get_ticket_output":
            return True

        if view.action == "is_processor":
            return True

        # 查看权限校验
        if request.method in permissions.SAFE_METHODS:

            if obj.can_view(username):
                return True

            # 单据带token请求，则判断
            token = request.query_params.get("token")
            if token and obj.is_token_accessible(username, token):
                return True

            return self.iam_ticket_view_auth(request, obj)

        # 处理权限校验
        self.message = _("抱歉，您无权操作该单据")

        if view.action == "supervise":
            return obj.can_supervise(username)

        # 修改公共字段权限
        if view.action == "edit_field" and Service.is_service_owner(
            obj.service_id, username
        ):
            return True
        return any([obj.can_operate(username)])

    def iam_ticket_manage_auth(self, request, obj):
        # 本地开发环境，不校验单据管理权限
        if settings.ENVIRONMENT == "dev":
            return True

        iam_client = IamRequest(request)
        resource_info = {
            "resource_id": str(obj.service_id),
            "resource_name": obj.service_name,
            "resource_type": "service",
        }

        apply_actions = ["ticket_management"]
        auth_actions = iam_client.resource_multi_actions_allowed(
            apply_actions, [resource_info], project_key=obj.project_key
        )

        if auth_actions.get("ticket_management"):
            return True

        return False

    def iam_ticket_view_auth(self, request, obj):
        iam_client = IamRequest(request)
        project_name = Project.objects.get(key=obj.project_key).name
        resource_info = {
            "resource_id": str(obj.service_id),
            "resource_name": obj.service_name,
            "resource_type": "service",
        }

        apply_actions = ["ticket_view"]
        auth_actions = iam_client.resource_multi_actions_allowed(
            apply_actions, [resource_info], project_key=obj.project_key
        )
        if auth_actions.get("ticket_view"):
            return True

        resource_list = [
            {
                "resource_id": obj.project_key,
                "resource_name": project_name,
                "resource_type": "project",
            },
            resource_info,
        ]

        bk_iam_path = "/project,{}/".format(obj.project_key)
        resources = [
            Resource(
                settings.BK_IAM_SYSTEM_ID,
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
            for resource in resource_list
        ]

        raise AuthFailedException(
            settings.BK_IAM_SYSTEM_ID,
            Subject("user", request.user.username),
            Action(apply_actions[0]),
            resources,
        )


class StatePermissionValidate(permissions.BasePermission):
    def __init__(self):
        self.message = _("抱歉，您无权操作当前单据任务")

    def has_object_permission(self, request, obj):
        if (
            request.data.get("action_type") == "EXCEPTION_DISTRIBUTE"
            and request.user.is_superuser
        ):
            return True
        return obj.can_operate(request.user.username)


class EventLogPermissionValidate(permissions.BasePermission):
    def __init__(self):
        self.message = _("抱歉，您无权查看该单据的日志")

    def has_permission(self, request, view):

        if UserRole.is_itsm_superuser(request.user.username):
            return True

        if view.action in ["get_index_ticket_event_log", "get_my_deal_time"]:
            return True

        ticket_id = request.query_params.get("ticket")
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            self.message = _("单据不存在：%s，请检查") % ticket_id
            return False

        return TicketPermissionValidate().has_object_permission(request, view, ticket)


class TicketFieldPermissionValidate(permissions.BasePermission):
    """
    目前FieldViewSet只使用了api_field_choices的方法
    """

    def __init__(self):
        self.message = _("抱歉，您无权限查看此信息")

    def has_permission(self, request, view):
        if UserRole.is_itsm_superuser(request.user.username):
            return True
        if view.action in ["api_field_choices", "download_file"]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if UserRole.is_itsm_superuser(request.user.username):
            return True
        if view.action in ["api_field_choices", "download_file"]:
            return True
        return False


class FollowersNotifyLogPermissionValidate(permissions.BasePermission):
    def __init__(self):
        self.message = _("抱歉，您无权查看该单据的日志信息")

    def has_permission(self, request, view):
        params = request.query_params if request.method == "GET" else request.data

        ticket_id = params.get("ticket_id")
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            self.message = _("抱歉，单据不存在：%s，请检查") % ticket_id
            return False

        return TicketPermissionValidate().has_object_permission(request, view, ticket)


class CommentPermissionValidate(permissions.BasePermission):
    def __init__(self):
        self.message = _("抱歉，您无权查看该单据的评价信息")

    def has_object_permission(self, request, view, obj):

        username = request.user.username

        if UserRole.is_itsm_superuser(username):
            return True

        if request.method in permissions.SAFE_METHODS:
            token = request.query_params.get("token")
            # 提单人或邀请评价能查看
            if obj.ticket.creator == username:
                return True
            if token and obj.ticket.is_email_invite_token(username, token):
                return True

        # 提单人或邀请评价才能从web评价
        if view.action == "update":
            token = request.data.get("token")
            self.message = _("抱歉，您不是该单据的提单人，无法评价")
            if obj.ticket.creator == username:
                return True
            if token and obj.ticket.is_email_invite_token(username, token):
                return True

        return False


class OperationalDataPermission(permissions.BasePermission):
    """运营数据权限，ITSM管理员，工单统计管理员"""

    def __init__(self):
        self.message = _("对不起，您没有模块的权限，请联系管理员。")

    def has_permission(self, request, view):
        username = request.user.username
        if UserRole.is_itsm_superuser(username) or UserRole.is_statics_manager(
            username
        ):
            return True
        return False

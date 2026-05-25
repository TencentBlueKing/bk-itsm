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

from django.utils.translation import gettext as _
from rest_framework import permissions

from itsm.role.models import UserRole

# 任务对象级权限说明：
# - proceed：节点处理人（沿用 task.can_process）
# - 写动作（update / partial_update / destroy / retry / skip）：要求所属单据创建人 / 当前处理人 / can_operate / 超管
# - 只读动作（retrieve / fields / get_task_status）：要求 can_view 或超管
TASK_WRITE_ACTIONS = {"update", "partial_update", "destroy", "retry", "skip"}
TASK_READ_ACTIONS = {"retrieve", "fields", "get_task_status"}


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


class TaskPermissionValidate(permissions.BasePermission):
    """
    任务操作权限
    """

    def __init__(self):
        self.message = _("抱歉，您无权处理该任务")

    def has_object_permission(self, request, view, obj):

        username = request.user.username
        if view.action == "proceed":
            return obj.can_process(username)

        if UserRole.is_itsm_superuser(username):
            return True

        if view.action not in TASK_WRITE_ACTIONS and view.action not in TASK_READ_ACTIONS:
            return True

        from itsm.ticket.models import Ticket
        ticket = Ticket.objects.filter(pk=obj.ticket_id).first()
        if ticket is None:
            return False

        if view.action in TASK_WRITE_ACTIONS:
            return (
                ticket.creator == username
                or username in ticket.real_current_processors
                or ticket.can_operate(username)
            )

        # TASK_READ_ACTIONS
        return ticket.can_view(username)

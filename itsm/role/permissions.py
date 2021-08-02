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
from itsm.component.drf import permissions as perm
from itsm.component.drf.permissions import IamAuthPermit


class IsUserRoleManager(perm.IsManager):
    """
    通用角色配置权限
    """

    message = _("您没有操作角色配置的权限")


class UserGroupPermission(IamAuthPermit):
    
    def has_object_permission(self, request, view, obj, **kwargs):
        # 关联实例的请求，需要针对对象进行鉴权
        if view.action in getattr(view, "permission_free_actions", []):
            return True
        
        if view.action in ["retrieve"]:
            apply_actions = ["user_group_view"]
        elif view.action in ["destroy"]:
            apply_actions = ["user_group_delete"]
        elif view.action in ["update"]:
            apply_actions = ["user_group_edit"]

        return self.iam_auth(request, apply_actions, obj)

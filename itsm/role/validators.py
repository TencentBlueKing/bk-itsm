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
from rest_framework import serializers

from itsm.component.constants import DEFAULT_PROJECT_PROJECT_KEY
from itsm.component.utils.basic import list_by_separator
from itsm.component.utils.client_backend_query import get_bk_users
from itsm.role.models import RoleType, UserRole


class UserRoleValidator(object):
    def __init__(self, role=None):
        self.role = role

    def __call__(self, value):

        role_type = value.get("role_type", "")
        role_key = value.get("role_key", "")
        name = value.get("name", "")
        access = value.get("access", "")
        project_key = value.get("project_key", DEFAULT_PROJECT_PROJECT_KEY)
        members = list_by_separator(value.get("members", ""))

        if not RoleType.objects.filter(type=role_type).exists():
            raise serializers.ValidationError(_("{}角色类型不存在").format(role_type))

        if (
            UserRole.objects.filter(
                name=name, role_type=role_type, project_key=project_key
            )
            .exclude(pk__in=[self.role.id] if self.role else [])
            .exists()
        ):
            raise serializers.ValidationError(_("该角色名称已存在"))

        # 不允许修改特殊角色的名称和权限范围
        if self.role and role_key in ["STATICS_MANAGER", "SUPERUSER", "WIKI_SUPERUSER"]:
            if self.role.access != access:
                raise serializers.ValidationError(_("该管理员权限页面不允许修改"))
            if self.role.name != name:
                raise serializers.ValidationError(_("该管理员角色名不允许修改"))

        bk_users = get_bk_users(users=members)
        if not set(members).issubset(set(bk_users)):
            raise serializers.ValidationError(
                _("【{}】用户不存在").format(
                    ",".join(list(set(members).difference(set(bk_users))))
                )
            )


def delete_user_role_validate(instance):
    """删除时校验"""
    if instance.role_key in ["STATICS_MANAGER", "SUPERUSER", "WIKI_SUPERUSER"]:
        raise serializers.ValidationError(_("该角色不能删除"))

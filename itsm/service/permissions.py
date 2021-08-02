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

from itsm.component.drf import permissions as perm
from itsm.role.models import UserRole
from itsm.service.models import CatalogService


class IsObjManager(perm.IsManager):
    """
    负责人
    """

    pass


class IsDictDataManager(permissions.BasePermission):
    """
    负责人
    """

    from itsm.service.models import SysDict

    SAFE_METHODS = permissions.SAFE_METHODS + ('DELETE',)

    def has_permission(self, request, view):
        if request.method in self.SAFE_METHODS:
            return True

        if UserRole.is_itsm_superuser(request.user.username):
            return True

        dict_table = request.data.get('dict_table')
        try:
            sys_dict = self.SysDict.objects.get(id=dict_table)
            return sys_dict.is_obj_manager(request.user.username)
        except self.SysDict.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        if request.method in self.SAFE_METHODS:
            return True

        if UserRole.is_itsm_superuser(request.user.username):
            return True

        return obj.dict_table.is_obj_manager(request.user.username)


class ServiceDeletePermit(permissions.BasePermission):
    """
    流程版本删除校验
    """

    message = _("服务占用中，请到服务目录中解绑后再删除")

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action == 'batch_delete':
            id_list = [i for i in request.data.get('id').split(',') if i.isdigit()]
            return not CatalogService.objects.filter(service_id__in=id_list).exists()

        return True

    def has_object_permission(self, request, view, obj):

        if view.action == 'destroy':
            return not CatalogService.objects.filter(service_id=request.parser_context['kwargs'].get('pk')).exists()

        return True

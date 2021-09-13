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

from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.constants import ADMIN_CHOICES, DEFAULT_PROJECT_PROJECT_KEY
from itsm.component.drf.mixins import DynamicListModelMixin
from itsm.component.drf.viewsets import (
    GenericViewSet,
    ReadOnlyModelViewSet,
    AuthModelViewSet,
)
from itsm.iadmin.contants import ORGANIZATION_KEY, SWITCH_OFF
from itsm.iadmin.models import SystemSettings
from itsm.role.models import RoleType, UserRole
from itsm.component.drf import permissions as perm
from itsm.role.permissions import UserGroupPermission
from itsm.role.serializers import RoleTypeSerializer, UserRoleSerializer
from itsm.role.utils import translate_constant_2
from itsm.role.validators import delete_user_role_validate


class RoleTypeModelViewSet(ReadOnlyModelViewSet):
    """角色类型视图集合"""

    serializer_class = RoleTypeSerializer
    queryset = RoleType.objects.all()
    pagination_class = None

    # IsAdmin:角色配置权限,只有超级管理员才有角色配置的权限,其他可用安全方法访问：GET,HEAD,OPTION
    permission_classes = (perm.IamAuthWithoutResourcePermit,)

    filter_fields = {
        "is_display": ["exact", "in"],
        "is_processor": ["exact", "in"],
        "type": ["exact", "in"],
        "name": ["exact", "contains", "startswith"],
    }

    def get_queryset(self):
        queryset = super(RoleTypeModelViewSet, self).get_queryset()
        if SystemSettings.objects.get(key=ORGANIZATION_KEY).value == SWITCH_OFF:
            return queryset.exclude(type="ORGANIZATION")
        return queryset


class UserRoleModelViewSet(DynamicListModelMixin, AuthModelViewSet):
    """用户组视图集"""

    serializer_class = UserRoleSerializer
    queryset = UserRole.objects.all().order_by("-create_at")
    pagination_class = None
    permission_free_actions = ["list"]
    permission_classes = (UserGroupPermission,)

    filter_fields = {
        "role_key": ["exact", "in"],
        "role_type": ["exact", "in"],
        "name": ["exact", "contains", "startswith", "icontains"],
    }

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None
        query_set = super(UserRoleModelViewSet, self).get_queryset().filter()
        return query_set

    def list(self, request, *args, **kwargs):
        """
        获取用户组列表
        """
        project_key = request.query_params.get(
            "project_key", DEFAULT_PROJECT_PROJECT_KEY
        )
        queryset = self.filter_queryset(self.get_queryset()).filter(
            project_key=project_key
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """BEP: 根据字段名生成字段role_key，并补充到field
        适合补充一些表单外的数据，且仅针对保存操作
        如果更新时也需要做相同的处理，建议放到系列化类的to_internal_value
        """

        role_type = serializer.validated_data["role_type"]
        role_key = "{}_{}".format(role_type, UserRole.objects.count() + 1)

        serializer.validated_data["role_key"] = role_key

        super(UserRoleModelViewSet, self).perform_create(serializer)

    def perform_destroy(self, instance):
        """删除时校验"""
        delete_user_role_validate(instance)
        instance.delete()


class UserRoleExtraViewSet(GenericViewSet):
    """用户角视图集"""

    serializer_class = UserRoleSerializer
    queryset = UserRole.objects.all()
    pagination_class = None

    @action(detail=False, methods=["get"])
    def get_access_by_user(self, request):
        """查询用户有权访问的模块标识列表"""

        all_access = UserRole.get_access_by_user(request.user.username)

        return Response(all_access)

    @action(detail=False, methods=["get"])
    def get_global_choices(self, request):
        """查询全局选项列表信息"""

        return Response(
            {
                "admin_choices": translate_constant_2(ADMIN_CHOICES),
            }
        )

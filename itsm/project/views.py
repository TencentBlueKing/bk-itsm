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

# 当前提供给前端获取用户权限链接使用
from django.db.models import Q
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action

from itsm.component.constants import LESSCODE_PROJECT_KEY
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.constants.iam import ACTIONS
from itsm.auth_iam.utils import IamRequest
from itsm.component.exceptions import ProjectSettingsNotFound, DeleteError
from itsm.project.handler.migration_handler import MigrationHandlerDispatcher
from itsm.project.models import (
    Project,
    ProjectSettings,
    UserProjectAccessRecord,
    CostomTab,
    PUBLIC_PROJECT_PROJECT_KEY,
)
from itsm.project.serializers import (
    ProjectSerializer,
    ProjectSettingSerializer,
    ProjectMigrateSerializer,
    CostomTabSerializer,
)


class ProjectViewSet(component_viewsets.AuthModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.filter(
        ~Q(key__in=[PUBLIC_PROJECT_PROJECT_KEY, LESSCODE_PROJECT_KEY]), is_deleted=False
    )

    filter_fields = {
        "name": ["exact", "contains", "startswith", "icontains"],
    }

    permission_free_actions = ["all"]
    permission_action_default = ["project_edit"]
    permission_action_mapping = {
        "retrieve": ["project_view"],
        "update_project_record": ["project_view"],
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        raise DeleteError(_("删除失败，项目目前不允许删除！"))

    @action(detail=False, methods=["get"])
    def all(self, request, *args, **kwargs):
        """
        查询当前用户所有项目依赖的权限
        @return: 所有项目的信息以及对应项目下当前用户依赖的权限
        """
        serializer = self.get_serializer(self.get_queryset(), many=True)
        serializer.context["request"] = request
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def info(self, request, *args, **kwargs):
        """查询用户依赖当前项目的权限"""
        iam_client = IamRequest(request)
        apply_actions = []

        project_instance = self.get_object()

        # 默认项目信息
        project_info = {
            "resource_id": project_instance.key,
            "resource_name": project_instance.name,
            "resource_type": "project",
            "resource_type_name": "项目",
        }
        for action_info in ACTIONS:
            if "project" in action_info["relate_resources"]:
                apply_actions.append(action_info["id"])

        auth_actions = iam_client.batch_resource_multi_actions_allowed(
            apply_actions, [project_info]
        ).get("0", {})

        auth_actions = [
            action_id for action_id, result in auth_actions.items() if result
        ]

        project_info["auth_actions"] = auth_actions
        return Response(project_info)

    @action(detail=True, methods=["get"])
    def project_settings(self, request, *args, **kwargs):
        instance = self.get_object()
        settings = ProjectSettings.objects.filter(project=instance)
        project_serializer = ProjectSettingSerializer(instance=settings, many=True)
        return Response(project_serializer.data)

    @action(detail=True, methods=["post"])
    def update_settings(self, request, *args, **kwargs):
        # 必须落在路径上的 project 范围内，避免借本项目 project_edit 改他项目 settings。
        project = self.get_object()
        ser = ProjectSettingSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        project_settings = ProjectSettings.objects.filter(
            id=ser.validated_data["id"], project_id=project.key
        ).first()
        if project_settings is None:
            raise ProjectSettingsNotFound()
        project_settings.value = ser.validated_data["value"]
        project_settings.save()
        return Response()

    @action(detail=True, methods=["post"])
    def update_project_record(self, request, *args, **kwargs):
        instance = self.get_object()
        username = request.user.username
        user_project_record = UserProjectAccessRecord.objects.filter(
            username=username
        ).first()
        if user_project_record is None:
            UserProjectAccessRecord.create_record(username, instance.key)
        else:
            user_project_record.update_record(instance.key)

        return Response()

    @action(detail=False, methods=["post"])
    def migration_project(self, request, *args, **kwargs):
        """
        request: data
        {
            "resource_type": "service",
            "resource_id":2,
            "old_project_key":0,
            "new_project_key":"test_project"

        }
        """
        ser = ProjectMigrateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # 资源迁移要求源/目标项目都具备 project_edit；否则可借本项目 edit 权限把资源迁入/迁出他项目。
        project_keys = [data["old_project_key"], data["new_project_key"]]
        projects = Project.objects.filter(key__in=project_keys)
        if projects.count() != len(set(project_keys)):
            self.permission_denied(request, message=_("源项目或目标项目不存在"))

        iam_client = IamRequest(request)
        resources = [
            {
                "resource_id": p.key,
                "resource_name": p.name,
                "resource_type": "project",
                "creator": getattr(p, "creator", ""),
            }
            for p in projects
        ]
        allowed = iam_client.batch_resource_multi_actions_allowed(
            ["project_edit"], resources
        )
        if not all(item.get("project_edit") for item in allowed.values()):
            self.permission_denied(request, message=_("源项目或目标项目缺少编辑权限"))

        MigrationHandlerDispatcher(resource_type=data["resource_type"]).migrate(
            data["resource_id"],
            data["old_project_key"],
            data["new_project_key"],
            request,
        )

        return Response()


class CostomTabViewSet(component_viewsets.ModelViewSet):
    serializer_class = CostomTabSerializer
    queryset = CostomTab.objects.filter(is_deleted=False).order_by("order")

    def get_queryset(self):
        # 个人范畴资源：所有读写均限定为当前登录用户创建的 tab。
        # 这样 get_object()/destroy/move 等通过 pk 查询时，跨用户访问会自然 404。
        return self.queryset.filter(creator=self.request.user.username)

    def get_personal_queryset(self):
        return self.get_queryset()

    def list(self, request, *args, **kwargs):
        project_key = self.request.query_params.get("project_key", "")
        if not project_key:
            raise ValidationError(_("project_key:该字段是必填项"))
        queryset = self.get_personal_queryset().filter(project_key=project_key)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        删除tab
        """
        # 1.获取当前tab的序号
        instance = self.get_object()
        order = instance.order
        project_key = instance.project_key
        # 2.删除当前tab
        self.perform_destroy(instance)
        # 3.将序号>当前序号的tab的序号批量-1
        tabs = self.get_personal_queryset().filter(
            order__gt=order, project_key=project_key
        )
        for tab in tabs:
            tab.order -= 1
        CostomTab.objects.bulk_update(tabs, ["order"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def move(self, request, *args, **kwargs):
        """
        移动tab到指定位置
        """
        # 1.获取移动目标序号
        new_order = request.data.get("new_order")
        instance = self.get_object()
        # 向前移动
        if instance.order > new_order:
            # 2.将[new_order, pk)的tab的序号批量+1
            tabs = self.get_personal_queryset().filter(
                order__gte=new_order,
                order__lt=instance.order,
                project_key=instance.project_key,
            )
            for tab in tabs:
                tab.order += 1
            CostomTab.objects.bulk_update(tabs, ["order"])
        # 向后移动
        elif instance.order < new_order:
            # 2.将(pk, new_order]的tab的序号批量-1
            tabs = self.get_personal_queryset().filter(
                order__gt=instance.order,
                order__lte=new_order,
                project_key=instance.project_key,
            )
            for tab in tabs:
                tab.order -= 1
            CostomTab.objects.bulk_update(tabs, ["order"])
        # 不改变顺序
        else:
            return Response()
        # 3.将当前tab的序号置为目标序号
        instance.order = new_order
        instance.save()
        return Response()

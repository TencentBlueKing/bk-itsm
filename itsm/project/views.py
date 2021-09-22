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

# 当前提供给前端获取用户权限链接使用

from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework.response import Response
from rest_framework.decorators import action
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.constants.iam import ACTIONS
from itsm.auth_iam.utils import IamRequest
from itsm.component.exceptions import ProjectSettingsNotFound, DeleteError
from itsm.project.handler.migration_handler import MigrationHandlerDispatcher
from itsm.project.models import Project, ProjectSettings, UserProjectAccessRecord
from itsm.project.serializers import (
    ProjectSerializer,
    ProjectSettingSerializer,
    ProjectMigrateSerializer,
)


class ProjectViewSet(component_viewsets.AuthModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.filter(~Q(key="public"), is_deleted=False)

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
        ser = ProjectSettingSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        project_settings = ProjectSettings.objects.get(id=ser.validated_data["id"])
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
        MigrationHandlerDispatcher(resource_type=data["resource_type"]).migrate(
            data["resource_id"],
            data["old_project_key"],
            data["new_project_key"],
            request,
        )

        return Response()

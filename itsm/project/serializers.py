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

import copy
import re

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from itsm.auth_iam.utils import IamRequest
from itsm.component.constants import CATALOG, FIRST_ORDER
from itsm.project.models import Project, ProjectSettings, CostomTab

project_name_pattern = re.compile("^[0-9a-zA-Z_-]{1,}$")


class ProjectSerializer(ModelSerializer):
    def validate_project(self, attrs):
        """
        检验项目名是否符合规范
        """
        if Project.objects.filter(name=attrs["name"], is_deleted=False).exists():
            raise serializers.ValidationError(
                "创建失败: 已存在项目名称为{}的项目".format(attrs["name"])
            )

        project_key = attrs.get("key", "")
        if len(project_key) > 0:
            if not project_key[0].isalpha():
                raise serializers.ValidationError("项目代号只允许英文字母开头")

        if not project_name_pattern.search(project_key):
            raise serializers.ValidationError("创建失败: 项目代号只允许包含数字，英文字母, 英文横线- 和下划线_")

    def create(self, validated_data):
        """改写post方法,提供update_or_create逻辑"""
        self.validate_project(validated_data)

        instance = super(ProjectSerializer, self).create(validated_data)
        catalogs = copy.deepcopy(CATALOG)
        for catalog in catalogs:
            catalog["key"] = "{}_{}".format(instance.key, catalog["key"])
            catalog["parent_key"] = "{}_{}".format(instance.key, catalog["parent_key"])
        instance.init_service_catalogs(catalogs)
        instance.init_project_settings()
        instance.init_project_sla()
        instance.init_custom_notify_template()
        return instance

    def to_representation(self, instance):
        data = super(ProjectSerializer, self).to_representation(instance)
        return self.update_auth_actions(instance, data)

    def update_auth_actions(self, instance, data):
        """
        更新权限信息
        """
        # 默认项目信息
        request = self.context["request"]

        iam_client = IamRequest(request)

        project_info = {
            "resource_id": instance.key,
            "resource_name": instance.name,
            "resource_type": "project",
            "resource_type_name": "项目",
        }
        apply_actions = self.Meta.model.resource_operations
        auth_actions = iam_client.batch_resource_multi_actions_allowed(
            apply_actions, [project_info], project_key=instance.key
        ).get(instance.key, {})
        auth_actions = [
            action_id for action_id, result in auth_actions.items() if result
        ]

        data["auth_actions"] = auth_actions
        return data

    class Meta:
        model = Project
        fields = ("name", "desc", "key", "logo", "color") + model.FIELDS
        read_only_fields = model.FIELDS


class ProjectSettingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    type = serializers.CharField(required=True, max_length=32)
    key = serializers.CharField(required=True, max_length=32)
    value = serializers.CharField(required=True, max_length=32)
    project_key = serializers.CharField(
        required=True, max_length=32, source="project_id"
    )
    project = ProjectSerializer(required=False)

    class Meta:
        model = ProjectSettings
        fields = "__all__"


class ProjectMigrateSerializer(serializers.Serializer):
    # 迁移类型
    CHOICES = [
        ("service", "服务"),
        ("user_group", "用户组"),
    ]

    resource_type = serializers.ChoiceField(choices=CHOICES, required=True)
    resource_id = serializers.IntegerField(required=True)
    old_project_key = serializers.CharField(required=True)
    new_project_key = serializers.CharField(required=True)


class CostomTabSerializer(serializers.ModelSerializer):
    # 自定义单据序列化
    conditions = serializers.JSONField(required=False)

    class Meta:
        model = CostomTab
        fields = ("id", "name", "desc", "project_key", "conditions", "order")

    def create(self, validated_data):
        # 1.获取当前项目key
        project_key = validated_data.get("project_key", "")
        creator = validated_data.get("creator", "")
        name = validated_data.get("name", "")
        tab_list = CostomTab.objects.filter(
            project_key=project_key, creator=creator, is_deleted=False
        )
        # 2.判断当前项目下该用户的tab是否已经存在
        tab_names = list(tab_list.values_list("name", flat=True))
        if name in tab_names:
            raise serializers.ValidationError("当前tab名称已存在")
        # 3.获取当前项目下该用户的tab数量
        order = tab_list.count()
        # 4.当前新增的tab序号为tab数量+1
        validated_data["order"] = order + FIRST_ORDER
        return super(CostomTabSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        project_key = validated_data.get("project_key", "")
        creator = validated_data.get("updated_by", "")
        name = validated_data.get("name", "")
        if CostomTab.objects.filter(
            project_key=project_key, creator=creator, name=name, is_deleted=False
        ).exists():
            raise serializers.ValidationError("当前tab名称已存在")
        return super(CostomTabSerializer, self).update(instance, validated_data)

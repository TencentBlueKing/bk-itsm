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

import json

from itsm.workflow.models.task import TaskSchema, TaskFieldSchema
from rest_framework import serializers
from itsm.component.constants import EMPTY_STRING, LEN_NORMAL, TASK_COMPONENT_CHOICE, TASK_STAGE_CHOICE, LEN_XX_LONG
from itsm.workflow.serializers import TemplateFieldSerializer, DynamicFieldsModelSerializer, dotted_name, normal_name


class TaskSchemaSerializer(DynamicFieldsModelSerializer):
    """任务配置信息序列化"""

    name = serializers.CharField(
        required=True, initial=EMPTY_STRING, max_length=LEN_NORMAL, allow_blank=True, allow_null=True
    )
    desc = serializers.CharField(required=False, initial=EMPTY_STRING, max_length=LEN_NORMAL, allow_blank=True)
    component_type = serializers.ChoiceField(required=True, choices=TASK_COMPONENT_CHOICE)
    owners = serializers.CharField(required=False, max_length=LEN_XX_LONG, allow_blank=True)
    is_draft = serializers.BooleanField(required=True)

    class Meta:
        model = TaskSchema
        fields = model.fields + model.FIELDS
        read_only_fields = model.FIELDS + ('is_builtin',)

    def to_internal_value(self, data):
        data = super(TaskSchemaSerializer, self).to_internal_value(data)
        if "owners" in data:
            data["owners"] = dotted_name(data["owners"])
        return data

    def to_representation(self, instance):
        data = super(TaskSchemaSerializer, self).to_representation(instance)
        data["owners"] = normal_name(data.get("owners"))
        return data


class TaskFieldSchemaSerializer(TemplateFieldSerializer):
    task_schema_id = serializers.IntegerField(required=True,)
    stage = serializers.ChoiceField(required=True, choices=TASK_STAGE_CHOICE)

    class Meta:
        model = TaskFieldSchema
        fields = (
            "id",
            "key",
            "name",
            "source_type",
            "source_uri",
            "type",
            "desc",
            "is_builtin",
            "is_readonly",
            "meta",
            "api_instance_id",
            "related_fields",
            "layout",
            "validate_type",
            "regex",
            "regex_config",
            "custom_regex",
            "choice",
            "kv_relation",
            "default",
            "api_info",
            "is_tips",
            "tips",
            "show_type",
            "show_conditions",
            "sequence",
            "task_schema_id",
            "stage",
        ) + model.FIELDS
        read_only_fields = ("is_builtin", "key") + model.FIELDS

    def get_related_fields(self, api_instance, validated_data):
        related_fields = []
        api_config = api_instance.get_config()
        task_fields_schema = TaskFieldSchema.objects.filter(
            task_schema_id=validated_data["task_schema_id"], stage=validated_data["stage"]
        )
        for key in task_fields_schema.values_list("key", flat=True):
            if "${params_%s}" % key in json.dumps(api_config["query_params"]):
                related_fields.append(key)
        return {"rely_on": related_fields}

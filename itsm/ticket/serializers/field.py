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

from rest_framework import serializers

from itsm.ticket.models import TicketField, TaskField
from itsm.workflow.models import State


class FieldSerializer(serializers.ModelSerializer):
    """单据字段序列化"""

    meta = serializers.JSONField(required=False, initial={})
    choice = serializers.JSONField(required=False, initial=[])
    kv_relation = serializers.JSONField(required=False, initial={})
    related_fields = serializers.JSONField(required=False, initial={})
    show_conditions = serializers.JSONField(required=False, initial={})
    regex_config = serializers.JSONField(required=False, initial={})

    class Meta:
        model = TicketField
        fields = (
            'id',
            'key',
            'type',
            'choice',
            'name',
            'value',
            'display',
            'display_value',
            'related_fields',
            'meta',
            'source_type',
            'source_uri',
            'kv_relation',
            'validate_type',
            'api_instance_id',
            'regex',
            'regex_config',
            'custom_regex',
            'default',
            'desc',
            'tips',
            'is_tips',
            'layout',
            'is_valid',
            'is_builtin',
            'ticket_id',
            'state_id',
            'show_conditions',
            'show_type',
            'is_readonly',
            'source',
            'workflow_field_id'
        ) + model.FIELDS

    def to_representation(self, instance):
        data = super(FieldSerializer, self).to_representation(instance)
        data['workflow_id'] = instance.ticket.flow.workflow_id
        # 是否展示全部字段（条件隐藏）
        data['show_result'] = instance.show_result(self.context.get('show_all_fields', True))

        return data


class FieldSimpleSerializer(serializers.ModelSerializer):
    """特殊日志接口使用"""

    class Meta:
        model = TicketField
        fields = ('name', '_display_value', 'ticket', 'key')


class FieldExportSerializer(serializers.Serializer):
    """导出工单使用"""

    name = serializers.CharField(read_only=True)
    display_value = serializers.CharField(read_only=True)
    ticket_id = serializers.PrimaryKeyRelatedField(read_only=True)
    key = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        data = super(FieldExportSerializer, self).to_representation(instance)
        state_name = ''
        if instance.state_id:
            state = State.objects.filter(id=instance.state_id).first()
            state_name = state.name if state else ''
        data.update({'state_name': state_name})
        return data


class TableFieldSerializer(FieldSerializer):
    """基础模型单据字段展示"""

    def to_representation(self, instance):
        data = super(TableFieldSerializer, self).to_representation(instance)

        # 全局只读字段
        if instance.is_readonly:
            data["can_edit"] = False
        else:
            if self.context["is_ticket_admin"]:
                data["can_edit"] = True
            else:
                data["can_edit"] = instance.key in self.context["can_edit_field_keys"]
        return data


class TaskFieldSerializer(serializers.ModelSerializer):
    meta = serializers.JSONField(required=False, initial={})
    choice = serializers.JSONField(required=False, initial=[])
    kv_relation = serializers.JSONField(required=False, initial={})
    related_fields = serializers.JSONField(required=False, initial={})
    show_conditions = serializers.JSONField(required=False, initial={})
    regex_config = serializers.JSONField(required=False, initial={})

    class Meta:
        model = TaskField
        fields = (
            'id',
            'key',
            'type',
            'choice',
            'name',
            'value',
            'display',
            'display_value',
            'show_result',
            'related_fields',
            'meta',
            'source_type',
            'source_uri',
            'kv_relation',
            'validate_type',
            'api_instance_id',
            'regex',
            'regex_config',
            'custom_regex',
            'default',
            'desc',
            'tips',
            'is_tips',
            'layout',
            'is_valid',
            'is_builtin',
            'state_id',
            'task_id',
            'show_conditions',
            'show_type',
            'is_readonly',
            'source',
        ) + model.FIELDS

    def to_representation(self, instance):
        data = super(TaskFieldSerializer, self).to_representation(instance)
        return data

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


class WorkflowSerializer(serializers.Serializer):
    """
    服务流程序列化
    """

    name = serializers.CharField(read_only=True)
    flow_type = serializers.CharField(read_only=True)
    desc = serializers.CharField(read_only=True)
    version_number = serializers.CharField(read_only=True)
    states = serializers.JSONField(read_only=True, initial=dict)
    transitions = serializers.JSONField(read_only=True, initial=dict)
    fields = serializers.JSONField(read_only=True, initial=dict)

    def to_representation(self, instance):
        data = super(WorkflowSerializer, self).to_representation(instance)

        data.update(
            states=self.clean_states(data['states']),
            transitions=self.clean_transitions(data['transitions']),
            fields=self.clean_fields(data['fields']),
        )

        return data

    def clean_states(self, states):
        """清理states"""

        for state_id, state in states.items():
            for key in [
                'creator',
                'create_at',
                'end_at',
                'update_at',
                'notify',
                'extras',
                'updated_by',
                'service',
                'axis',
                'is_draft',
                'variables',
                'is_builtin',
                'desc',
            ]:
                state.pop(key, None)

        return states.values()

    def clean_transitions(self, transitions):
        """清理transitions"""

        for transition_id, transition in transitions.items():
            for key in ['creator', 'create_at', 'end_at', 'update_at', 'updated_by', 'axis', 'desc']:
                transition.pop(key, None)

        return transitions.values()

    def clean_fields(self, fields):
        """清理fields"""

        for field_id, field in fields.items():
            for key in [
                'creator',
                'create_at',
                'end_at',
                'update_at',
                'updated_by',
                'default',
                'show_conditions',
                'show_type',
                'is_builtin',
                'layout',
                'is_deleted',
                'is_valid',
                'is_tips',
                'display',
                'kv_relation',
                'tips',
                'related_fields',
            ]:
                field.pop(key, None)

        return fields.values()

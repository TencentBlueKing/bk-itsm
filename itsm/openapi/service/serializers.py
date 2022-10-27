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


class ServiceSerializer(serializers.Serializer):
    """
    服务项列表序列化
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    service_type = serializers.CharField(read_only=True)
    desc = serializers.CharField(read_only=True)


class ServiceRetrieveSerializer(serializers.Serializer):
    """
    服务项详情序列化
    """

    service_id = serializers.IntegerField(read_only=True, source="id")
    workflow_id = serializers.IntegerField(read_only=True, source="workflow.id")
    name = serializers.CharField(read_only=True)
    service_type = serializers.CharField(read_only=True)
    desc = serializers.CharField(read_only=True)
    fields = serializers.JSONField(read_only=True, source="first_state_fields")


class WorkflowVersionFirstStateFieldSerializer(serializers.Serializer):
    """
    流程版本提单节点字段序列化
    """

    id = serializers.IntegerField(read_only=True)
    key = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    default = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    desc = serializers.CharField(read_only=True)
    choice = serializers.JSONField(read_only=True, initial=list)
    layout = serializers.CharField(read_only=True)
    source_type = serializers.CharField(read_only=True)
    source_uri = serializers.CharField(read_only=True)
    api_instance_id = serializers.IntegerField(read_only=True)
    api_info = serializers.JSONField(read_only=True, initial=dict)
    kv_relation = serializers.JSONField(read_only=True, initial=dict)
    validate_type = serializers.CharField(read_only=True)
    regex = serializers.CharField(read_only=True)
    regex_config = serializers.JSONField(read_only=True, initial=dict)
    custom_regex = serializers.CharField(read_only=True)
    meta = serializers.JSONField(read_only=True, initial=dict)
    show_type = serializers.IntegerField(read_only=True)
    show_conditions = serializers.JSONField(read_only=True, initial=dict)

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

from rest_framework import serializers

from requests_tracker.models import Record


class RecordSerializer(serializers.ModelSerializer):
    """请求记录序列化"""

    class Meta:
        model = Record
        fields = (
        'id', 'url', 'method', 'api_instance_id', 'status_code', 'date_created', 'duration')


class RecordFilterSerializer(serializers.Serializer):
    """请求记录过滤参数序列化"""

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    name__contains = serializers.CharField(required=False)
    status = serializers.ChoiceField(
        required=False, choices=[('20X', '20X'), ('30X', '40X'), ('40X', '40X'), ('50X', '40X'), ]
    )
    date_created__gte = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    date_created__lte = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")


class RecordRetriveSerializer(RecordSerializer):
    """请求记录详情序列化"""

    class Meta(RecordSerializer.Meta):
        fields = RecordSerializer.Meta.fields + (
        'ticket_id', 'state_id', 'request_message', 'response_message')

    def to_representation(self, instance):
        data = super(RecordRetriveSerializer, self).to_representation(instance)

        response_message = data.get('response_message')
        try:
            response_message = json.loads(response_message)
        except Exception:
            pass

        data.update(response_message=response_message)

        return data

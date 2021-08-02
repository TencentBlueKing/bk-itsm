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

from itsm.component.utils.human import get_time
from itsm.component.utils.misc import transform_single_username
from itsm.ticket.models import Ticket, TicketField
from itsm.ticket.serializers import FieldSerializer


class WXTicketDealLogListSerializer(serializers.ModelSerializer):
    """处理记录序列化"""

    class Meta:
        model = Ticket
        fields = ('id', 'sn', 'title', 'service_type_name', 'creator', 'catalog_fullname')

    def to_representation(self, instance):
        data = super(WXTicketDealLogListSerializer, self).to_representation(instance)

        username = self.context['request'].user.username

        log = (
            instance.logs.filter(operator=username)
            .exclude(message__in=['流程开始', '单据流程结束'])
            .order_by('-operate_at')
            .first()
        )
        data.update(
            creator=transform_single_username(instance.creator),
            action=log.type if log else '',
            operate_at=get_time(log.operate_at, format='%Y-%m-%d %H:%M:%S') if log else '',
            state_name=instance.flow.states[str(log.from_state_id)]['name'] if log else '',
        )
        return data


class WXTicketRetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    sn = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    service_type_name = serializers.CharField(read_only=True)
    creator = serializers.CharField(read_only=True)
    catalog_fullname = serializers.CharField(read_only=True)
    create_at = serializers.CharField(read_only=True)
    current_steps = serializers.JSONField(read_only=True)
    current_status = serializers.CharField(read_only=True)
    current_status_display = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        data = super(WXTicketRetrieveSerializer, self).to_representation(instance)
        data.update(
            creator=transform_single_username(instance.creator),
            states=instance.get_wx_states(self.context["request"].user.username),
        )
        return data


class WXFieldSerializer(FieldSerializer):
    """微信单据字段序列化"""

    class Meta:
        model = TicketField
        fields = (
            'id',
            'key',
            'type',
            'choice',
            'meta',
            'state_id',
            'name',
            'display_value',
            'value',
            'display',
            'source_type',
            'related_fields',
            'source_uri',
            'layout',
            'validate_type',
        )

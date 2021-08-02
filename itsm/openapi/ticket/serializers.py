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

from django.utils.translation import ugettext as _
from rest_framework import serializers

from itsm.component.constants import ALL_ACTION_CHOICES, API, LEN_LONG
from itsm.component.exceptions import ParamError
from itsm.ticket.serializers import TicketSerializer, TicketStateOperateSerializer
from itsm.ticket.validators import ticket_fields_validate


class TicketStatusSerializer(serializers.Serializer):
    """
    单据状态序列化
    """

    ticket_url = serializers.CharField(read_only=True)
    iframe_ticket_url = serializers.CharField(read_only=True)
    operations = serializers.JSONField(read_only=True)
    current_status = serializers.CharField(read_only=True)
    current_steps = serializers.JSONField(read_only=True)
    is_commented = serializers.BooleanField(read_only=True)

    def clean_fields(self, fields):
        """清理fields"""

        for field in fields:
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

        return fields

    def to_representation(self, instance):
        data = super(TicketStatusSerializer, self).to_representation(instance)
        current_steps = data['current_steps']
        flow = instance.flow
        data["ticket_url"] = instance.pc_ticket_url

        for step in current_steps:
            state_id = step['state_id']
            status = instance.status(state_id)
            fields = flow.get_state_fields(state_id)
            fields = self.clean_fields(fields)
            step.update(fields=fields, operations=status.operations)

        return data


class TicketResultSerializer(serializers.Serializer):
    """
    审批结果序列化
    """

    sn = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    ticket_url = serializers.CharField(read_only=True)
    current_status = serializers.CharField(read_only=True)
    updated_by = serializers.CharField(read_only=True)
    update_at = serializers.DateTimeField(read_only=True)

    def clean_fields(self, fields):
        """清理fields"""

        for field in fields:
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

        return fields

    def to_representation(self, instance):
        data = super(TicketResultSerializer, self).to_representation(instance)
        data["ticket_url"] = instance.pc_ticket_url
        data["approve_result"] = instance.get_ticket_result()
        data['updated_by'] = data["updated_by"].strip(",")
        return data


class TicketRetrieveSerializer(serializers.Serializer):
    """
    单据详情序列化
    """

    id = serializers.IntegerField(read_only=True)
    catalog_id = serializers.IntegerField(read_only=True)
    service_id = serializers.IntegerField(read_only=True)
    flow_id = serializers.IntegerField(read_only=True)
    sn = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    current_status = serializers.CharField(read_only=True)
    current_steps = serializers.JSONField(read_only=True)
    comment_id = serializers.CharField(read_only=True)
    is_commented = serializers.BooleanField(read_only=True)
    updated_by = serializers.CharField(read_only=True)
    update_at = serializers.DateTimeField(read_only=True)
    end_at = serializers.DateTimeField(read_only=True)
    creator = serializers.CharField(read_only=True)
    create_at = serializers.DateTimeField(read_only=True)
    is_biz_need = serializers.BooleanField(read_only=True)
    bk_biz_id = serializers.IntegerField(read_only=True)
    fields = serializers.JSONField(read_only=True, source='ticket_fields')
    iframe_ticket_url = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        data = super(TicketRetrieveSerializer, self).to_representation(instance)
        data["ticket_url"] = instance.pc_ticket_url
        data['updated_by'] = data["updated_by"].strip(",")
        return data


class TicketFieldSerializer(serializers.Serializer):
    """
    单据字段序列化
    """

    id = serializers.IntegerField(read_only=True)
    key = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    desc = serializers.CharField(read_only=True)
    value = serializers.JSONField(read_only=True)
    display_value = serializers.JSONField(read_only=True)


class TicketLogsSerializer(serializers.Serializer):
    """
    单据日志序列化
    """

    sn = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    create_at = serializers.DateTimeField(read_only=True)
    creator = serializers.CharField(read_only=True)
    logs = serializers.JSONField(read_only=True, source='ticket_logs')


class SimpleLogsSerializer(serializers.Serializer):
    """
    单据日志主要信息序列化
    """

    operator = serializers.CharField(read_only=True)
    operate_at = serializers.DateTimeField(read_only=True)
    message = serializers.CharField(read_only=True)
    source = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        data = super(SimpleLogsSerializer, self).to_representation(instance)
        data['message'] = data['message'].format(
            operator=instance.operator,
            name=instance.from_state_name,
            detail_message=instance.detail_message,
            action=instance.action,
        )
        return data


class TicketListSerializer(serializers.Serializer):
    """
    单据列表序列化
    """

    id = serializers.IntegerField(read_only=True)
    sn = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    catalog_id = serializers.IntegerField(read_only=True)
    service_id = serializers.IntegerField(read_only=True)
    service_type = serializers.CharField(read_only=True)
    flow_id = serializers.IntegerField(read_only=True)
    current_status = serializers.CharField(read_only=True)
    comment_id = serializers.CharField(read_only=True)
    is_commented = serializers.BooleanField(read_only=True)
    updated_by = serializers.CharField(read_only=True)
    update_at = serializers.DateTimeField(read_only=True)
    end_at = serializers.DateTimeField(read_only=True)
    creator = serializers.CharField(read_only=True)
    create_at = serializers.DateTimeField(read_only=True)
    is_biz_need = serializers.BooleanField(read_only=True)
    bk_biz_id = serializers.IntegerField(read_only=True)
    ticket_url = serializers.CharField(read_only=True)
    iframe_ticket_url = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        data = super(TicketListSerializer, self).to_representation(instance)
        data["ticket_url"] = instance.pc_ticket_url
        data['updated_by'] = data["updated_by"].strip(",")
        return data


class ProceedFieldSerializer(serializers.Serializer):
    """
    单据字段列表
    """

    key = serializers.CharField(required=True, min_length=1)
    value = serializers.CharField(required=True, allow_blank=True)


class TicketProceedSerializer(serializers.Serializer):
    """
    单据处理序列化
    """

    operator = serializers.CharField(required=True, min_length=1)
    fields = ProceedFieldSerializer(many=True, required=True)

    def validate_fields(self, fields):
        """
        检验字段合法性：必填校验（未考虑隐藏字段）
        """
        ticket = self.context['ticket']
        state_id = self.context['state_id']

        # 检查字段是否缺失
        state_fields = ticket.flow.get_state_fields(state_id)
        required_fields = filter(lambda f: f['validate_type'] == 'REQUIRE', state_fields)
        required_keys = {f['key'] for f in required_fields}

        field_keys = set()
        field_hash = {}
        for f in fields:
            field_keys.add(f['key'])
            field_hash[f['key']] = f['value']

        lost_keys = required_keys - field_keys
        if lost_keys:
            raise ParamError(_('单据处理失败，缺少参数：{}'.format(list(lost_keys))))

        for f in state_fields:
            f.update(value=field_hash.get(f['key'], ''))

        # TODO: 校验字段的value的合法性，需要进一步重构validators
        ticket_fields_validate(state_fields, state_id, ticket, request=self.context["request"])

        return state_fields


class TicketCreateSerializer(TicketSerializer):
    """
    单据处理序列化
    """

    creator = serializers.CharField(required=True)


class TicketNodeOperateSerializer(TicketStateOperateSerializer):
    """单据节点操作序列化"""

    operator = serializers.CharField(required=True)

    def to_internal_value(self, data):
        data = super(TicketNodeOperateSerializer, self).to_internal_value(data)
        data.update(source=API)
        return data


class TicketOperateSerializer(serializers.Serializer):
    """单据操作序列化"""

    operator = serializers.CharField(required=True)
    action_type = serializers.ChoiceField(choices=ALL_ACTION_CHOICES)
    action_message = serializers.CharField(required=False, max_length=LEN_LONG)


class TicketFilterSerializer(serializers.Serializer):
    """单据查询过滤的序列化器"""
    view_type = serializers.ChoiceField(
        required=True,
        choices=[
            ("my_todo", "my_todo"),
            ("my_created", "my_created"),
            ("my_history", "my_history"),
            ("my_dealt", "my_dealt"),
            ("my_attention", "my_attention"),
            ("my_approval", "my_approval"),
        ],
    )
    create_at__gte = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    create_at__lte = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    exclude_ticket_id__in = serializers.CharField(required=False)
    current_processor = serializers.CharField(required=False)

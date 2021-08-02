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
from rest_framework.fields import empty

from itsm.component.constants import FIRST_ORDER, LEN_LONG, LEN_NORMAL, LEN_SHORT, PROCESS_RUNNING
from itsm.service.validators import service_type_validator
from itsm.ticket_status.models import StatusTransit, TicketStatus, TicketStatusConfig
from itsm.ticket_status.validators import TicketStatusValidator


class TicketStatusConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketStatusConfig
        fields = ("id", "service_type", "service_type_name", "ticket_status", "updated_by", "update_at", "configured")


class TicketStatusOptionSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    key = serializers.CharField(read_only=True)
    is_over = serializers.CharField(read_only=True)


class TicketStatusSerializer(serializers.ModelSerializer):
    """单据状态序列化"""

    name = serializers.CharField(
        required=True, max_length=LEN_LONG, error_messages={"blank": _("请输入状态名称"), "max_length": _("状态名称长度不能大于255个字符")}
    )
    color_hex = serializers.CharField(required=True, max_length=LEN_SHORT, error_messages={"blank": _("二进制颜色不能为空")})
    service_type = serializers.CharField(
        required=True,
        max_length=LEN_NORMAL,
        error_messages={"blank": _("服务类型不能为空")},
        validators=[service_type_validator],
    )

    class Meta:
        model = TicketStatus
        fields = (
            "id",
            "service_type",
            "order",
            "key",
            "name",
            "color_hex",
            "flow_status",
            "desc",
            "is_builtin",
            "is_start",
            "is_over",
            "is_suspend",
        ) + model.DISPLAY_FIELDS

        # 只读字段在创建和更新时均被忽略
        # key为后台自动生成
        read_only_fields = ("key", "is_builtin", "order") + model.DISPLAY_FIELDS

    def create(self, validated_data):
        """创建自定义单据状态"""

        # 获取同一服务类型下的最大order数值
        ticket_status = (
            TicketStatus.objects.filter(service_type=validated_data["service_type"]).order_by("order").last()
        )
        created_order = ticket_status.order + FIRST_ORDER if ticket_status else FIRST_ORDER
        validated_data.update(
            order=created_order,
            key=TicketStatus.get_unique_key(validated_data["name"]),
            is_builtin=False,
            is_start=False,
            is_over=False,
            flow_status=PROCESS_RUNNING,
        )

        instance = super(TicketStatusSerializer, self).create(validated_data)
        return instance

    def update(self, instance, validated_data):
        """更新单据状态"""
        # 内置的单据状态 只有以下属性可以被编辑
        can_edited = ("is_start", "is_over", "name", "desc", "color_hex") + TicketStatus.DISPLAY_FIELDS
        if instance.is_builtin and set(validated_data.keys()).difference(can_edited):
            raise serializers.ValidationError(_("抱歉，内置单据状态无法被编辑"))

        return super(TicketStatusSerializer, self).update(instance, validated_data)

    def run_validation(self, data=empty):
        self.validators = [TicketStatusValidator(self.instance)]
        return super(TicketStatusSerializer, self).run_validation(data)


class StatusTransitSerializer(serializers.ModelSerializer):
    """状态转换序列化"""

    class Meta:
        model = StatusTransit
        fields = (
            "id",
            "from_status",
            "from_status_name",
            "to_status",
            "to_status_name",
            "is_auto",
            "threshold",
            "threshold_unit",
        ) + model.DISPLAY_FIELDS

        # 只读字段在创建和更新时均被忽略
        read_only_fields = model.DISPLAY_FIELDS

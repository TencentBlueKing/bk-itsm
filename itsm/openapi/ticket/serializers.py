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
import random
import string

from django.utils.translation import ugettext as _
from rest_framework import serializers

from itsm.component.constants import (
    ALL_ACTION_CHOICES,
    API,
    LEN_LONG,
    APPROVAL_CHOICES,
    LEN_NORMAL,
    TASK_STATE,
    NORMAL_STATE,
    APPROVAL_STATE,
    SIGN_STATE,
)
from itsm.component.exceptions import ParamError
from itsm.ticket.models import Ticket
from itsm.ticket.serializers import (
    TicketComment,
)
from itsm.component.utils.basic import get_random_key
from itsm.ticket.models import Status
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
                "creator",
                "create_at",
                "end_at",
                "update_at",
                "updated_by",
                "default",
                "show_conditions",
                "show_type",
                "is_builtin",
                "layout",
                "is_deleted",
                "is_valid",
                "is_tips",
                "display",
                "kv_relation",
                "tips",
                "related_fields",
            ]:
                field.pop(key, None)

        return fields

    def to_representation(self, instance):
        data = super(TicketStatusSerializer, self).to_representation(instance)
        current_steps = data["current_steps"]
        flow = instance.flow
        data["ticket_url"] = instance.pc_ticket_url

        for step in current_steps:
            state_id = step["state_id"]
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
                "creator",
                "create_at",
                "end_at",
                "update_at",
                "updated_by",
                "default",
                "show_conditions",
                "show_type",
                "is_builtin",
                "layout",
                "is_deleted",
                "is_valid",
                "is_tips",
                "display",
                "kv_relation",
                "tips",
                "related_fields",
            ]:
                field.pop(key, None)

        return fields

    def to_representation(self, instance):
        data = super(TicketResultSerializer, self).to_representation(instance)
        data["ticket_url"] = instance.pc_ticket_url
        data["approve_result"] = instance.get_ticket_result()
        data["updated_by"] = data["updated_by"].strip(",")
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
    fields = serializers.JSONField(read_only=True, source="ticket_fields")
    iframe_ticket_url = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        data = super(TicketRetrieveSerializer, self).to_representation(instance)
        data["ticket_url"] = instance.pc_ticket_url
        data["updated_by"] = data["updated_by"].strip(",")
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
    logs = serializers.JSONField(read_only=True, source="ticket_logs")

    def to_representation(self, instance):
        data = super(TicketLogsSerializer, self).to_representation(instance)

        return data


class TicketComplexLogsSerializer(TicketLogsSerializer):
    logs = serializers.JSONField(read_only=True, source="ticket_complex_logs")


class TicketApproveSerializer(TicketLogsSerializer):
    sn = serializers.CharField(read_only=True)
    state_id = serializers.IntegerField(read_only=True)
    approver = serializers.CharField(read_only=True)
    action = serializers.CharField(read_only=True)
    remarked = serializers.CharField(read_only=True)


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
        data["message"] = data["message"].format(
            operator=instance.operator,
            name=instance.from_state_name,
            detail_message=instance.detail_message,
            action=instance.action,
        )
        return data


class ComplexLogsSerializer(serializers.Serializer):
    operator = serializers.CharField(read_only=True)
    operate_at = serializers.DateTimeField(read_only=True)
    message = serializers.CharField(read_only=True)
    source = serializers.CharField(read_only=True)
    form_data = serializers.JSONField(read_only=True)

    def to_representation(self, instance):
        data = super(ComplexLogsSerializer, self).to_representation(instance)
        # 返回form data 数据，由于API节点的 form data 太过于庞大，故只返回输出变量
        node_status = Status.objects.filter(
            ticket_id=instance.ticket_id, state_id=instance.from_state_id
        ).first()

        from_state_type = getattr(node_status, "type", "")
        data["from_state_type"] = from_state_type

        if from_state_type in [NORMAL_STATE, APPROVAL_STATE, SIGN_STATE]:
            data["form_data"] = TicketFieldSerializer(
                instance.form_data, many=True
            ).data

        if from_state_type == TASK_STATE:
            form_data = []
            if isinstance(instance.form_data, list) and instance.form_data:
                for item in instance.form_data:
                    form_data.append(
                        {
                            "output_variables": item.get("value", {}).get(
                                "output_variables", []
                            )
                        }
                    )
            data["form_data"] = form_data

        data["message"] = data["message"].format(
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
        data["updated_by"] = data["updated_by"].strip(",")
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
        ticket = self.context["ticket"]
        state_id = self.context["state_id"]

        # 检查字段是否缺失
        state_fields = ticket.flow.get_state_fields(state_id)
        required_fields = filter(
            lambda f: f["validate_type"] == "REQUIRE", state_fields
        )
        required_keys = {f["key"] for f in required_fields}

        field_keys = set()
        field_hash = {}
        for f in fields:
            field_keys.add(f["key"])
            field_hash[f["key"]] = f["value"]

        lost_keys = required_keys - field_keys
        if lost_keys:
            raise ParamError(_("单据处理失败，缺少参数：{}".format(list(lost_keys))))

        for field in state_fields:
            if "workflow_id" in field:
                field.pop("workflow_id")
            field.update(value=field_hash.get(field["key"], ""))

        # TODO: 校验字段的value的合法性，需要进一步重构validators
        ticket_fields_validate(
            state_fields, state_id, ticket, request=self.context["request"]
        )

        return state_fields


class TicketCreateSerializer(TicketSerializer):
    """
    单据处理序列化
    """

    creator = serializers.CharField(required=True)
    tag = serializers.CharField(required=False)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "catalog_id",
            "catalog_name",
            "catalog_fullname",
            "service_id",
            "service_name",
            "flow_id",
            "sn",
            "title",
            "service_type",
            "service_type_name",
            "is_draft",
            "current_status",
            "current_status_display",
            "comment_id",
            "is_commented",
            "is_over",
            "related_type",
            "has_relationships",
            "priority_name",
            "meta",
            "bk_biz_id",
            "project_key",
            "task_schemas",
            "tag",
        ) + model.FIELDS
        read_only_fields = ("sn",) + model.FIELDS


class DynamicFieldSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=32)
    type = serializers.ChoiceField(
        choices=[("STRING", "字符串"), ("INT", "数字"), ("LINK", "链接")], required=True
    )
    value = serializers.CharField(required=True, max_length=255)
    key = serializers.CharField(required=False, read_only=True)

    def validate(self, attrs):
        key = get_random_key(attrs["name"])
        if key[0].isdigit():
            # 开头为数字，重新生成
            first_letter = random.choice(string.ascii_letters)
            key = first_letter + key[1:]

        attrs["key"] = key
        return attrs


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


class ProceedApprovalSerializer(serializers.Serializer):
    """审批操作序列化"""

    process_inst_id = serializers.CharField(required=False, max_length=LEN_NORMAL)
    activity = serializers.IntegerField(required=True)
    submit_action = serializers.ChoiceField(choices=APPROVAL_CHOICES)
    submit_opinion = serializers.CharField(required=False, max_length=LEN_LONG)
    handler = serializers.CharField(required=True)


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
    service_id = serializers.IntegerField(required=False)
    catalog_id = serializers.IntegerField(required=False)
    create_at__gte = serializers.DateTimeField(
        required=False, format="%Y-%m-%d %H:%M:%S"
    )
    create_at__lte = serializers.DateTimeField(
        required=False, format="%Y-%m-%d %H:%M:%S"
    )
    exclude_ticket_id__in = serializers.CharField(required=False)
    current_processor = serializers.CharField(required=False)


class CommentSerializer(serializers.Serializer):
    """工单评价序列化"""

    ticket_id = serializers.IntegerField(required=False)
    operator = serializers.CharField(max_length=16, required=True)
    sn = serializers.CharField(required=True)
    stars = serializers.IntegerField(required=True, max_value=6, min_value=1)
    comments = serializers.CharField(
        required=False, max_length=LEN_LONG, allow_null=True, allow_blank=True
    )

    def validate(self, attrs):
        sn = attrs.get("sn", "")
        try:
            ticket = Ticket.objects.get(sn=sn)
        except Ticket.DoesNotExist:
            raise ParamError(_("sn={}对应的单据不存在!".format(sn)))

        if ticket.current_status != "FINISHED":
            raise ParamError(_("单据未结束，不允许评价!"))

        try:
            ticket_comment = TicketComment.objects.get(ticket_id=ticket.id)
        except TicketComment.DoesNotExist:
            raise ParamError(_("单据评价记录未存在，无法评价!"))

        if ticket_comment.stars != 0:
            raise ParamError(_("该单据已经被评论，请勿重复评论"))

        attrs["ticket_id"] = ticket.id

        return attrs

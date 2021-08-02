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

from itsm.component.constants import LEN_LONG, LEN_NORMAL
from itsm.component.utils.client_backend_query import get_bk_users
from itsm.component.utils.human import get_time
from itsm.component.utils.misc import transform_username
from itsm.role.models import UserRole
from itsm.ticket.models import (
    TicketComment,
    TicketCommentInvite,
    TicketFollowerNotifyLog,
    TicketGlobalVariable,
    TicketStateDraft,
    TicketTemplate,
)


class TemplateSerializer(serializers.ModelSerializer):
    """单据模板序列化"""

    name = serializers.CharField(required=True, max_length=LEN_NORMAL)
    service = serializers.CharField(required=True, max_length=LEN_NORMAL)
    template = serializers.JSONField(required=True)

    class Meta:
        model = TicketTemplate
        fields = ("id", "name", "service", "template")

    def validate(self, attrs):
        creator = self.context["request"].user.username
        pk = self.context["view"].kwargs.get("pk")
        if self.context["view"].action == "create":
            if TicketTemplate.objects.filter(
                name=attrs.get("name"), creator=creator, service=attrs.get("service")
            ).exists():
                raise serializers.ValidationError(_("该模板名字已存在"))
        if self.context["view"].action == "update":
            if (
                TicketTemplate.objects.filter(name=attrs.get("name"), creator=creator, service=attrs.get("service"))
                .exclude(id=pk)
                .exists()
            ):
                raise serializers.ValidationError(_("该模板名字已存在"))
        attrs["creator"] = creator
        return attrs


class StateDraftSerializer(serializers.ModelSerializer):
    """单据节点草稿序列化"""

    ticket_id = serializers.IntegerField(required=True)
    state_id = serializers.IntegerField(required=True)
    draft = serializers.JSONField(required=True)

    class Meta:
        model = TicketStateDraft
        fields = ("id", "ticket_id", "state_id", "draft")

    def validate(self, attrs):
        creator = self.context["request"].user.username
        if self.context["view"].action == "create":
            if TicketStateDraft.objects.filter(
                ticket_id=attrs.get("ticket_id"), creator=creator, state_id=attrs.get("state_id")
            ).exists():
                raise serializers.ValidationError(_("该模板名字已存在"))
        if self.context["view"].action == "update":
            if (
                TicketStateDraft.objects.filter(
                    ticket_id=attrs.get("ticket_id"), creator=creator, state_id=attrs.get("state_id")
                )
                .exclude(id=self.context["view"].kwargs.get("pk"))
                .exists()
            ):
                raise serializers.ValidationError(_("已在该单据节点创建了草稿"))
        attrs["creator"] = creator
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """工单评价序列化"""

    stars = serializers.IntegerField(required=True, max_value=6, min_value=1)
    comments = serializers.CharField(required=False, max_length=LEN_LONG, allow_null=True, allow_blank=True)

    class Meta:
        model = TicketComment
        fields = (
            "id",
            "ticket",
            "stars",
            "comments",
            "source",
            "creator",
            "create_at",
            "update_at",
        )

    # 已经评论的直接返回
    def update(self, instance, validated_data):
        if instance.stars != 0:
            raise serializers.ValidationError(_("该单据已经被评论，请勿重复评论"))

        return super(CommentSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        data = super(CommentSerializer, self).to_representation(instance)
        data["has_invited"] = ",".join(instance.invite.all().values_list("receiver", flat=True))
        data["creator"] = get_bk_users(format="dict", users=[data["creator"]]).get(data["creator"], data["creator"])
        return data


class CommentInviteSerializer(serializers.ModelSerializer):
    """邀请途径记录表序列化"""

    class Meta:
        model = TicketCommentInvite
        fields = ("id", "comment", "number", "code")


class FollowerNotifyLogSerializer(serializers.ModelSerializer):
    """工单关注人日志序列化"""

    class Meta:
        model = TicketFollowerNotifyLog
        fields = (
            "id",
            "ticket",
            "state_id",
            "state_name",
            "followers",
            "followers_type",
            "message",
            "creator",
            "create_at",
        )

    def to_representation(self, instance):
        data = super(FollowerNotifyLogSerializer, self).to_representation(instance)
        data["creator_zh"] = get_bk_users(format="dict", users=[instance.creator]).get(instance.creator, "")
        data["create_at"] = "{}".format(get_time(instance.create_at))
        data["group"] = transform_username(
            UserRole.get_users_by_type(
                bk_biz_id=instance.ticket.bk_biz_id,
                users=instance.followers,
                user_type=instance.followers_type,
                ticket=instance.ticket,
            )
        )

        return data


class TicketGlobalVariableSerializer(serializers.ModelSerializer):
    """单据全局变量序列化"""

    value = serializers.JSONField(required=True)

    class Meta:
        model = TicketGlobalVariable
        fields = ("key", "name", "value", "update_at")

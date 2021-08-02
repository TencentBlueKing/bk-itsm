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

from itsm.component.constants import LEN_MIDDLE, LEN_SHORT
from itsm.component.drf.serializers import AuthModelSerializer
from itsm.sla.models import Action, ActionPolicy, PriorityPolicy, Sla, SlaTimerRule, SlaTicketHighlight
from itsm.sla.serializers import ModelSerializer
from itsm.sla.validators import SlaTimerRuleValidator, SlaValidator


class PriorityPolicySerializer(serializers.ModelSerializer):
    """
    优先级处理策略
    """

    id = serializers.IntegerField(required=False)
    priority = serializers.CharField(required=True, max_length=LEN_MIDDLE)
    handle_time = serializers.IntegerField(required=True)
    handle_unit = serializers.CharField(required=True, max_length=LEN_SHORT)
    reply_time = serializers.IntegerField(required=True, allow_null=True)
    reply_unit = serializers.CharField(required=True, max_length=LEN_SHORT)

    class Meta:
        model = PriorityPolicy
        fields = (
            "id",
            "priority",
            "schedule",
            "handle_time",
            "handle_unit",
            "reply_time",
            "reply_unit",
        ) + model.DISPLAY_FIELDS

        read_only_fields = model.DISPLAY_FIELDS
        
    def to_internal_value(self, data):
        if not data["reply_time"]:
            data["reply_time"] = None
            
        return super(PriorityPolicySerializer, self).to_internal_value(data)


class SlaTimerRuleSerializer(serializers.ModelSerializer):
    """
    sla到达规则规则
    """

    condition = serializers.JSONField(required=True)

    class Meta:
        model = SlaTimerRule
        fields = ('id', 'name', 'service_type', 'condition_type', 'condition') + model.DISPLAY_FIELDS

        read_only_fields = model.DISPLAY_FIELDS

    def run_validation(self, data=empty):
        self.validators = [SlaTimerRuleValidator(self.instance)]
        return super(SlaTimerRuleSerializer, self).run_validation(data)


class ActionSerializer(serializers.ModelSerializer):
    """
    升级事件动作
    """

    id = serializers.IntegerField(required=False)
    config = serializers.JSONField()

    class Meta:
        model = Action
        fields = ('id', 'action_type', 'config',) + model.DISPLAY_FIELDS

        read_only_fields = model.DISPLAY_FIELDS


class ActionPolicySerializer(ModelSerializer):
    """
    sla到达规则规则
    """

    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    actions = ActionSerializer(many=True)
    condition = serializers.JSONField(required=True)

    class Meta:
        model = ActionPolicy
        fields = ('id', 'name', 'condition', 'actions', 'type') + model.DISPLAY_FIELDS

        read_only_fields = model.DISPLAY_FIELDS

    def create(self, validated_data):
        actions = validated_data.pop("actions", [])
        instance = super(ActionPolicySerializer, self).create(validated_data)
        if not actions:
            return instance

        actions = [self.fields.fields['actions'].child.create(action) for action in actions]
        instance.actions.set(actions)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        全量更新
        """
        actions = validated_data.pop("actions", [])
        instance = super(ActionPolicySerializer, self).update(instance, validated_data)

        instance = self.update_many_to_many_relation(instance, {"actions": actions})
        return instance


class SlaSerializer(AuthModelSerializer, ModelSerializer):
    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("SLA协议名称为必填")},
        # validators=[name_validator],
        max_length=LEN_MIDDLE,
    )
    is_enabled = serializers.BooleanField(required=False, default=False)
    policies = PriorityPolicySerializer(many=True)
    action_policies = ActionPolicySerializer(many=True)
    is_reply_need = serializers.BooleanField()
    project_key = serializers.CharField(required=True, max_length=LEN_SHORT)

    class Meta:
        model = Sla
        fields = (
            'id',
            'name',
            'is_enabled',
            'is_builtin',
            'policies',
            'action_policies',
            'service_count',
            'service_names',
            'is_reply_need',
            'project_key'
        ) + model.DISPLAY_FIELDS

        related_fields = ('policies', 'action_policies')

        read_only_fields = model.DISPLAY_FIELDS

    def create(self, validated_data):
        SlaValidator(self.instance).name_validate(validated_data)
        action_policies = validated_data.pop("action_policies", [])
        policies = validated_data.pop("policies", [])
        instance = super(SlaSerializer, self).create(validated_data)
        instance.action_policies.set([
            self.fields.fields['action_policies'].child.create(a_data) for a_data in action_policies
        ])
        instance.policies.set([self.fields.fields['policies'].child.create(p_data) for p_data in policies])
        instance.save()
        return instance

    def update(self, instance, validated_data):
        rel_fields = {key: validated_data.pop(key, []) for key in self.Meta.related_fields}

        instance = super(SlaSerializer, self).update(instance, validated_data)
        instance = self.update_many_to_many_relation(instance, rel_fields)

        return instance

    def run_validation(self, data=empty):
        return super(SlaSerializer, self).run_validation(data)
    
    def to_representation(self, instance):
        data = super(SlaSerializer, self).to_representation(instance)
        return self.update_auth_actions(instance, data)


class TicketHighlightSerializer(ModelSerializer):
    """工单高亮偏好序列化"""

    class Meta:
        model = SlaTicketHighlight
        fields = (
            'id',
            'reply_timeout_color',
            'handle_timeout_color'
        )

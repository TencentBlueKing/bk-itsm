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

from django.db.models import Model
from rest_framework import serializers

from itsm.component.constants import (
    LEN_LONG,
    TRIGGER_SIGNAL_CHOICE,
    TRIGGER_SOURCE_TYPE,
    EMPTY_LIST,
    EMPTY_DICT,
    OPT_TYPE_CHOICE, LEN_SHORT,
)
from itsm.component.drf.serializers import AuthModelSerializer
from itsm.trigger.models import Trigger, TriggerRule, ActionSchema, Action
from .validators import TriggerValidator


class TriggerSerializer(AuthModelSerializer):
    """
    触发器规则序列化
    """

    name = serializers.CharField(max_length=LEN_LONG)
    desc = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)
    signal = serializers.ChoiceField(choices=TRIGGER_SIGNAL_CHOICE)
    source_type = serializers.ChoiceField(required=True, choices=TRIGGER_SOURCE_TYPE)
    source_id = serializers.IntegerField(required=True)
    source_table_id = serializers.IntegerField(required=False, allow_null=True)
    project_key = serializers.CharField(required=True, max_length=LEN_SHORT)

    class Meta:
        model = Trigger
        fields = model.FIELDS + model.DISPLAY_FIELDS
        read_only_fields = model.DISPLAY_FIELDS

    def to_internal_value(self, data):
        """
        外部参数序列化
        """
        source_table_id = data.pop("source_table_id", None)
        if source_table_id:
            # 仅配置了source_table_id的时候，才真正的对应的table id记录
            data['source_table_id'] = source_table_id

        internal_data = super(TriggerSerializer, self).to_internal_value(data)
        if internal_data.get('is_draft') is True:
            internal_data['is_enabled'] = False

        return internal_data
    
    def to_representation(self, instance):
        data = super(TriggerSerializer, self).to_representation(instance)
        return self.update_auth_actions(instance, data)

    def run_validators(self, value):
        self.validators.extend([TriggerValidator(self.instance)])
        return super(TriggerSerializer, self).run_validators(value)
    
    def update_auth_actions(self, instance, data):
        """
        更新权限信息
        """
        if instance is not None:
            if instance.source_type != "basic":
                data.update(auth_actions=["triggers_view", "triggers_manage"])
            else:
                resource_id = str(instance.id if isinstance(instance, Model) else instance['id'])
                instance_permissions = self.resource_permissions.get(resource_id, {})
                data.update(auth_actions=[action for action, result in instance_permissions.items() if result])
        return data


class TriggerRuleSerializer(AuthModelSerializer):
    """
    触发器条件配置和触发时间配置序列化
    """

    condition = serializers.JSONField(default={})
    action_schemas = serializers.JSONField(default=EMPTY_LIST)
    trigger_id = serializers.IntegerField(required=True,)
    name = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True, allow_null=True)

    class Meta:
        model = TriggerRule
        fields = model.FIELDS + model.DISPLAY_FIELDS
        read_only_fields = model.DISPLAY_FIELDS
        
    def update_auth_actions(self, instance, data):
        """
        更新权限信息
        """
        if instance is not None:
            trigger = Trigger.objects.get(id=instance.trigger_id)
            if trigger.source_type != "basic":
                data.update(auth_actions=["triggers_view", "triggers_manage"])
            else:
                resource_id = str(instance.id if isinstance(instance, Model) else instance['id'])
                instance_permissions = self.resource_permissions.get(resource_id, {})
                data.update(auth_actions=[action for action, result in instance_permissions.items() if result])
        return data


class ActionSchemaSerializer(AuthModelSerializer):
    """
    触发器条件配置和触发时间配置序列化
    """

    # 参数
    name = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True, allow_null=True)
    component_type = serializers.CharField(required=True, max_length=LEN_LONG)

    operate_type = serializers.ChoiceField(choices=OPT_TYPE_CHOICE, default="BACKEND")
    can_repeat = serializers.BooleanField(default=False)
    display_name = serializers.CharField(max_length=LEN_LONG, allow_blank=True, allow_null=True)
    delay_params = serializers.JSONField(required=False)

    # 参数
    params = serializers.JSONField(default=EMPTY_DICT)
    inputs = serializers.JSONField(default=EMPTY_DICT)

    class Meta:
        model = ActionSchema
        fields = model.FIELDS + model.DISPLAY_FIELDS
        read_only_fields = model.DISPLAY_FIELDS


class ActionSerializer(serializers.ModelSerializer):
    """
    触发器条件配置和触发时间配置序列化
    """

    inputs = serializers.JSONField(required=False, default=EMPTY_DICT)

    class Meta:
        model = Action
        fields = model.FIELDS
        read_only_fields = model.DISPLAY_FIELDS


class ActionDetailSerializer(serializers.ModelSerializer):
    """
    触发器条件配置和触发时间配置序列化
    """

    inputs = serializers.JSONField(required=False, default=EMPTY_DICT)
    fields = serializers.JSONField(required=False, default=EMPTY_LIST)

    class Meta:
        model = Action
        read_only_fields = model.DISPLAY_FIELDS
        fields = model.FIELDS + ("fields", "trigger_name", "rule_name", "operate_type", "signal_name", "create_at",)

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
from rest_framework.fields import JSONField

from itsm.component.constants import DEFAULT_FLOW_CONDITION, LEN_NORMAL, LEN_SHORT
from itsm.workflow.models import Condition, State, Transition
from itsm.workflow.validators import TransitionValidator


class TransitionTemplateSerializer(serializers.ModelSerializer):
    """线条模板序列化"""

    name = serializers.CharField(
        required=True,
        max_length=LEN_NORMAL,
        allow_null=False,
        error_messages={'blank': _('请输入模板名称!'), 'max_length': _('模板名称长度不能大于64个字符')},
    )
    data = JSONField(required=False, initial=DEFAULT_FLOW_CONDITION)

    class Meta:
        model = Condition
        fields = ('id', 'name', 'data', 'workflow')

        read_only_fields = ('creator', 'create_at', 'update_at', 'end_at')

    def validate(self, attrs):
        """校验参数，name不能相同等"""
        if self.context["view"].action == "create":
            if Condition.objects.filter(is_deleted=False, name=attrs["name"]).exists():
                raise serializers.ValidationError(_("同流程下线条模板名称已存在"))
        if self.context["view"].action == "update":
            if Condition.objects.filter(is_deleted=False, name=attrs["name"]).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(_("同流程下线条模板名称已存在"))

        return attrs


class TransitionSerializer(serializers.ModelSerializer):
    """流转序列化"""

    axis = JSONField(required=False, initial={})
    name = serializers.CharField(required=True, max_length=LEN_SHORT, allow_blank=False, allow_null=False)
    condition = JSONField(required=False, initial=DEFAULT_FLOW_CONDITION)

    class Meta:
        model = Transition
        fields = (
            'workflow',
            'id',
            'from_state',
            'to_state',
            'name',
            'axis',
            'condition',
            'condition_type',
        ) + model.FIELDS
        read_only_fields = ('key',) + model.FIELDS

    def __init__(self, *args, **kwargs):
        super(TransitionSerializer, self).__init__(*args, **kwargs)
        self.view = self.context.get('view')
        if self.view and self.view.action == 'create':
            self.validators = [TransitionValidator()]

    def update(self, instance, validated_data):
        instance = super(TransitionSerializer, self).update(instance, validated_data)

        # 不是全局更新的情况下，需要更新条件
        if self.context['view'].action != 'partial_update' and instance.condition_type != 'default':
            State.objects.update_outputs_variables(instance.condition, instance.workflow.id)

        return instance

    def create(self, validated_data):
        instance = super(TransitionSerializer, self).create(validated_data)
        State.objects.update_state_label(instance.from_state, instance.to_state)
        return instance

    def to_internal_value(self, data):
        if data.get('condition_type') == 'default':
            data['condition'] = DEFAULT_FLOW_CONDITION
        return super(TransitionSerializer, self).to_internal_value(data)

    def validate(self, attrs):
        """线条配置校验"""
        if attrs.get('condition_type', '') == 'by_field':
            for expression in attrs['condition']['expressions']:
                for condition in expression['expressions']:
                    if condition['type'] == 'INT' and condition['value'] == 0:
                        if not (condition['condition'] and condition['key']):
                            raise serializers.ValidationError(_("条件配置错误"))
                    if condition['type'] == 'BOOLEAN' and condition['value'] not in [True, False]:
                        raise serializers.ValidationError(_("布尔类型的取值范围不正确"))
                        # elif not (condition['condition'] and condition['key'] and condition['value']):
                    #     raise serializers.ValidationError(u"条件配置错误")
        return attrs

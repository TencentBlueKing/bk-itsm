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

from itsm.component.constants import (
    EMPTY_INT,
    FIELD_BIZ,
    LEN_LONG,
    LEN_MIDDLE,
    LEN_NORMAL,
    NOTIFY_FREQ_CHOICES,
    NOTIFY_RULE_CHOICES,
    PROCESSOR_CHOICES,
    LEN_XX_LONG,
)
from itsm.component.drf.serializers import DynamicFieldsModelSerializer
from itsm.component.utils.basic import dotted_name, dotted_property, normal_name
from itsm.component.utils.misc import transform_single_username
from itsm.workflow.models import Notify, Table, Workflow, WorkflowVersion
from itsm.workflow.serializers import FieldSerializer, NotifySerializer
from itsm.workflow.serializers.state import StateSerializer
from itsm.workflow.validators import WorkflowPipelineValidator, related_validate


class WorkflowSerializer(DynamicFieldsModelSerializer):
    """工作流序列化"""

    # 基础字段
    name = serializers.CharField(
        required=True,
        max_length=LEN_MIDDLE,
        error_messages={'blank': _('请输入流程名称!'), 'max_length': _('流程名称长度不能大于120个字符')},
    )
    flow_type = serializers.CharField(required=True, max_length=LEN_NORMAL)
    desc = serializers.CharField(required=False, max_length=LEN_LONG, min_length=1,
                                 allow_blank=True)
    owners = serializers.CharField(required=False, max_length=LEN_XX_LONG, allow_blank=True)
    deploy = serializers.BooleanField(required=False)
    deploy_name = serializers.CharField(required=False, max_length=LEN_LONG, min_length=1,
                                        allow_blank=True)
    # 基础模型
    table = serializers.PrimaryKeyRelatedField(required=True, queryset=Table.objects.all())
    # 业务属性字段
    is_biz_needed = serializers.BooleanField(required=False)
    # 是否自动过单
    is_auto_approve = serializers.BooleanField(required=False)
    is_iam_used = serializers.BooleanField(required=False)
    is_supervise_needed = serializers.BooleanField(required=False)
    supervise_type = serializers.ChoiceField(required=False, choices=PROCESSOR_CHOICES)
    supervisor = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)
    is_enabled = serializers.BooleanField(required=False)
    is_draft = serializers.BooleanField(required=False)
    is_revocable = serializers.BooleanField(required=False)
    revoke_config = serializers.JSONField(required=False)
    notify = NotifySerializer(required=False, allow_null=True, many=True)
    notify_rule = serializers.ChoiceField(required=False, allow_blank=True,
                                          choices=NOTIFY_RULE_CHOICES)
    notify_freq = serializers.IntegerField(default=EMPTY_INT)
    extras = serializers.JSONField(required=False)

    class Meta:
        model = Workflow
        fields = (
                     'id',
                     'name',
                     'desc',
                     'flow_type',
                     'version_number',
                     'deploy',
                     'deploy_name',
                     'notify',
                     'notify_rule',
                     'notify_freq',
                     'is_biz_needed',
                     'is_iam_used',
                     'is_enabled',
                     'is_draft',
                     'is_revocable',
                     'is_builtin',
                     'is_supervise_needed',
                     'supervisor',
                     'supervise_type',
                     'table',
                     'owners',
                     'extras',
                     'revoke_config',
                     'is_auto_approve',
                 ) + model.FIELDS

        # 只读字段在创建和更新时均被忽略
        read_only_fields = ('creator', 'create_at', 'update_at', 'end_at')

    def save(self, **kwargs):
        instance = super(WorkflowSerializer, self).save(**kwargs)
        instance.update_biz_field()
        return instance

    def update(self, instance, validated_data):
        deploy = validated_data.pop('deploy', None)
        deploy_name = validated_data.pop('deploy_name', None)

        is_biz_needed = validated_data.get('is_biz_needed', None)
        if is_biz_needed is False and instance.is_biz_needed is True:
            related_validate(instance.fields.get(key=FIELD_BIZ))
        flow = super(WorkflowSerializer, self).update(instance, validated_data)
        if 'task_settings' in validated_data.get('extras', {}):
            flow.create_task(validated_data['extras']['task_settings'])

        # 是否立即部署
        if deploy:
            flow.create_version(validated_data["updated_by"], name=deploy_name)

        return instance

    def to_internal_value(self, data):

        validated_data = super(WorkflowSerializer, self).to_internal_value(data)
        if validated_data.get('supervise_type') == 'PERSON':
            validated_data['supervisor'] = dotted_name(validated_data.get('supervisor', ''))

        notify_list = validated_data.pop("notify", None)
        if notify_list:
            validated_data['notify'] = Notify.objects.filter(
                type__in=(notify["type"] for notify in notify_list)
            ).values_list('pk', flat=True)

        if "owners" in validated_data:
            validated_data["owners"] = dotted_name(validated_data["owners"])

        if "is_enabled" in validated_data and "extras" not in validated_data and self.instance:
            # 如果extras不存在，直接置空
            extras = self.instance.extras
            extras["task_settings"] = []
            validated_data['extras'] = extras

        return validated_data

    def to_representation(self, instance):
        data = super(WorkflowSerializer, self).to_representation(instance)
        data["owners"] = normal_name(data.get("owners"))
        data['updated_by'] = transform_single_username(data['updated_by'])

        if "supervise_type" in data and data['supervise_type'] == 'PERSON':
            data['supervisor'] = dotted_property(data, 'supervisor')
        task_settings = data["extras"].get("task_settings")
        if task_settings and isinstance(task_settings, dict):
            data["extras"]["task_settings"] = []
            if task_settings.get("task_schema_ids"):
                data["extras"]["task_settings"] = [
                    {
                        "task_schema_id": task_settings["task_schema_ids"][0],
                        "create_task_state": task_settings["create_task_state"],
                        "execute_can_create": task_settings.get("execute_can_create", False),
                        "execute_task_state": task_settings["execute_task_state"],
                        "need_task_finished": task_settings["need_task_finished"],
                    }
                ]
        return self.update_auth_actions(instance, data)

    # ====================================== validate ========================

    def validate_notify_freq(self, value):
        """通知频率校验"""
        if value not in NOTIFY_FREQ_CHOICES:
            raise serializers.ValidationError({str(_('参数校验失败')): _('通知频率参数不正确')})
        return value

    def validate(self, attrs):
        name = attrs.get('name')
        if self.instance:
            if Workflow.objects.filter(name=name).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({str(_('参数校验失败')): _('系统中已存在同名流程，请尝试换个流程名称')})
        else:
            if Workflow.objects.filter(name=name).exists():
                raise serializers.ValidationError({str(_('参数校验失败')): _('系统中已存在同名流程，请尝试换个流程名称')})

        notify_rule = attrs.get('notify_rule', 'NONE')
        notify = attrs.get('notify', '')
        if notify_rule != 'NONE' and not notify:
            raise serializers.ValidationError({str(_('参数校验失败')): _('至少选择一种通知类型')})

        deploy = attrs.get('deploy')
        deploy_name = attrs.get('deploy_name')
        if deploy:
            WorkflowPipelineValidator(self.instance)(if_deploy=True)
        if deploy and not deploy_name:
            raise serializers.ValidationError({str(_('参数校验失败')): _('请指定部署流程名')})

        return attrs


class WorkflowVersionSerializer(DynamicFieldsModelSerializer):
    """工作流快照序列化"""

    class Meta:
        model = WorkflowVersion
        main_fields = (
            'id',
            'name',
            'desc',
            'workflow_id',
            'flow_type',
            'version_number',
            'is_builtin',
            'is_enabled',
            'is_draft',
            'is_revocable',
            'updated_by',
            'update_at',
            'creator',
        )
        property_fields = ('service_cnt',)
        fields = property_fields + main_fields

        read_only_fields = (
            'service_cnt',
            'version_number',
            'is_builtin',
            'is_draft',
            'workflow_id',
            'updated_by',
            'update_at',
        )

    def to_representation(self, instance):

        from collections import OrderedDict  # NOQA # isort:skip
        from rest_framework.fields import SkipField  # NOQA # isort:skip
        from rest_framework.relations import PKOnlyObject  # NOQA # isort:skip

        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                if field.field_name in self.Meta.property_fields:
                    attribute = getattr(self.Meta.model.objects, field.field_name)(instance)
                else:
                    continue
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)
        return self.update_auth_actions(instance, ret)


class OperationalDataWorkflowSerializer(WorkflowSerializer):
    """运营数据流程序列化"""

    def to_representation(self, instance):
        data = super(OperationalDataWorkflowSerializer, self).to_representation(instance)
        query_type = self.context.get("query_type", "list")
        if query_type == "detail":
            states_serializer = StateSerializer(instance.states, many=True)
            fields_serializer = FieldSerializer(instance.fields, many=True)
            data.update(
                {"states": states_serializer.data, "fields": fields_serializer.data, }
            )
        return data

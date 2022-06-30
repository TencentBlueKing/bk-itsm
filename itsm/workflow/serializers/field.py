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

from django.db import transaction
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.fields import JSONField, empty
from rest_framework.validators import UniqueValidator

from itsm.auth_iam.utils import IamRequest
from itsm.component.drf.serializers import AuthModelSerializer
from itsm.component.constants import (
    FIELD_BIZ,
    LAYOUT_CHOICES,
    LEN_LONG,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_XX_LONG,
    REGEX_CHOICES_LIST,
    SHOW_DIRECTLY,
    SOURCE_CHOICES,
    TABLE,
    VALIDATE_CHOICES,
    LEN_SHORT,
    PUBLIC_PROJECT_PROJECT_KEY,
)
from itsm.component.utils.basic import get_pinyin_key
from itsm.postman.models import RemoteApi, RemoteApiInstance
from itsm.postman.serializers import ApiInstanceSerializer
from itsm.workflow.models import Field, Table, TemplateField
from itsm.workflow.validators import FieldValidator, TemplateFieldValidator


class FieldVariablesSerializer(serializers.ModelSerializer):
    """字段变量序列化， 配置线条用"""

    choice = serializers.JSONField(initial=[])
    kv_relation = JSONField(required=False, initial={})
    meta = JSONField(required=False, initial={})

    class Meta:
        model = Field
        fields = (
            "id",
            "key",
            "name",
            "choice",
            "type",
            "validate_type",
            "source_type",
            "source_uri",
            "source",
            "api_instance_id",
            "kv_relation",
            "meta",
        )

    def to_representation(self, instance):
        data = super(FieldVariablesSerializer, self).to_representation(instance)
        if data.get("source", TABLE) == TABLE:
            name = "{}({})".format(data["name"], _("基础模型"))
        else:
            state_name = instance.state.name if instance.state.name else _("当前节点")
            name = "{}({})".format(data["name"], state_name)
        data["source"] = "field"
        data.update({"name": name})

        return data


class FieldVariablesGroupSerializer(FieldVariablesSerializer):
    def to_representation(self, instance):
        data = super(FieldVariablesSerializer, self).to_representation(instance)
        if data.get("source", TABLE) == TABLE:
            state_name = _("基础模型")
            name = "{}".format(data["name"])
        else:
            state_name = instance.state.name if instance.state.name else _("当前节点")
            name = "{}".format(data["name"])
        data.setdefault("id", instance.id)
        data.setdefault("state", state_name)
        data["source"] = "field"
        data.update({"name": name})
        if data["source_type"] == "API" and data["api_instance_id"]:
            api_instance = RemoteApiInstance.objects.get(id=data["api_instance_id"])
            data["api_info"] = ApiInstanceSerializer(api_instance).data

        return data


class TemplateFieldSerializer(AuthModelSerializer):
    """字段库序列化"""

    name = serializers.CharField(
        required=True,
        max_length=LEN_NORMAL,
        error_messages={"max_length": _("字段显示名称不能超过64个字符")},
    )
    key = serializers.CharField(required=True, max_length=LEN_MIDDLE)
    default = serializers.CharField(
        required=False, max_length=LEN_XX_LONG, allow_blank=True
    )
    desc = serializers.CharField(
        required=False, allow_blank=True, max_length=LEN_MIDDLE
    )
    validate_type = serializers.ChoiceField(choices=VALIDATE_CHOICES)
    regex = serializers.ChoiceField(choices=REGEX_CHOICES_LIST)
    regex_config = JSONField(required=False, initial={})
    source_type = serializers.ChoiceField(choices=SOURCE_CHOICES)
    layout = serializers.ChoiceField(choices=LAYOUT_CHOICES)
    choice = JSONField(required=False, initial=[])
    kv_relation = JSONField(required=False, initial={})
    related_fields = JSONField(required=False, initial={})
    api_instance_id = serializers.IntegerField(required=False, default=0)
    api_info = JSONField(required=False, initial={})
    meta = JSONField(required=False, initial={})
    show_type = serializers.IntegerField(required=False, default=SHOW_DIRECTLY)
    show_conditions = JSONField(required=False, initial={})
    project_key = serializers.CharField(required=True, max_length=LEN_SHORT)

    class Meta:
        model = TemplateField
        fields = (
            "id",
            "key",
            "name",
            "source_type",
            "source_uri",
            "type",
            "desc",
            "is_builtin",
            "is_readonly",
            "meta",
            "api_instance_id",
            "related_fields",
            "layout",
            "validate_type",
            "regex",
            "regex_config",
            "custom_regex",
            "choice",
            "kv_relation",
            "default",
            "api_info",
            "is_tips",
            "tips",
            "show_type",
            "show_conditions",
            "project_key",
        ) + model.FIELDS
        read_only_fields = ("is_builtin", "key") + model.FIELDS

    def __init__(self, *args, **kwargs):
        validator_class = kwargs.pop("validator_class", TemplateFieldValidator)
        super(TemplateFieldSerializer, self).__init__(*args, **kwargs)
        self.validators = [validator_class(self.instance)]

    @staticmethod
    def get_new_meta(data):
        """
        格式描述：
                meta: {
                    columns: [
                        {
                            key: 'name',
                            name: '姓名',
                            display: 'input',
                            'choice': []
                        },
                        {
                            key: 'sex',
                            name: '性别',
                            display: 'select',
                            'choice': [u'\\u59d3\\u540d', u'\\u6027\\u522b']
                        },
                    ]
                }
        """
        new_meta = data.get("meta", {})
        for column in new_meta.get("columns", []):
            column.update(
                key=get_pinyin_key(column.get("name")),
            )
            # 忽略展现形式不是下拉框的类型
            if column.get("display") in ["select", "multiselect"]:
                column.update(
                    choice=[
                        {"name": value, "key": get_pinyin_key(value)}
                        for value in column.get("choice", [])
                    ]
                )
        return new_meta

    def get_new_choice(self, data):
        """
        格式描述：
                choice: <type 'list'>: [u'\\u59d3\\u540d', u'\\u6027\\u522b']
                meta: {
                    columns: [
                        {key: 'name', name: '姓名', display: 'input', 'choice': []},
                        {key: 'sex', name: '性别', display: 'select', 'choice': [u'\\u59d3\\u540d', u'\\u6027\\u522b']},
                    ]
                }
        """
        new_choices = data.get("choice", [])

        if not self.instance:
            new_choices = [
                {"name": choice, "key": get_pinyin_key(choice)}
                for choice in new_choices
            ]
        else:
            # update exist options
            name2key = {item["name"]: item["key"] for item in self.instance.choice}
            new_choices = [
                {
                    "name": choice,
                    # use exist key first
                    "key": name2key.get(choice, get_pinyin_key(choice)),
                }
                for choice in new_choices
            ]
        return new_choices

    def to_internal_value(self, data):
        """BEP: 另一种添加key的写法
        处理后的数据会经过drf的校验逻辑
        所有incoming数据都会被处理
        处理的数据是原始前端数据
        """

        if data.get("type") == "CUSTOMTABLE":
            # 复杂表格支持：更新meta中每一列的values的key
            data.update(
                meta=self.get_new_meta(data),
            )
        if data.get("source_type") == "API":
            data["api_info"].pop("remote_system_id", None)

        if data.get("show_type") == SHOW_DIRECTLY:
            data["show_conditions"] = {}

        return super(TemplateFieldSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        data = super(TemplateFieldSerializer, self).to_representation(instance)
        if instance.source_type == "API" and instance.api_instance:
            data["api_info"] = ApiInstanceSerializer(instance.api_instance).data

        # 默认初始化的时候没有request
        if "request" not in self.context:
            return data
        if isinstance(instance, TemplateField):
            if instance.project_key == PUBLIC_PROJECT_PROJECT_KEY:
                return self.update_public_field_auth_actions(instance, data)
        return self.update_auth_actions(instance, data)

    def run_validation(self, data=empty):
        validated_data = super(TemplateFieldSerializer, self).run_validation(data)
        if validated_data["source_type"] == "API":
            self.to_api_internal_value(validated_data)
        return validated_data

    def update_public_field_auth_actions(self, instance, data):
        # 默认项目信息
        request = self.context["request"]

        iam_client = IamRequest(request)

        filed_info = {
            "resource_id": instance.id,
            "resource_name": instance.name,
            "resource_type": "public_field",
            "resource_type_name": "公共字段",
        }
        apply_actions = self.Meta.model.public_field_resource_operations
        auth_actions = iam_client.batch_resource_multi_actions_allowed(
            apply_actions, [filed_info]
        ).get(str(instance.id), {})
        auth_actions = [
            action_id for action_id, result in auth_actions.items() if result
        ]
        data["auth_actions"] = auth_actions
        return data

    def get_related_fields(self, api_instance, validated_data):
        """获取当前字段依赖的字段"""
        return {"rely_on": []}

    def to_api_internal_value(self, validated_data):
        """
        api字段接口信息格式化
        """
        from itsm.postman.serializers import RemoteApiSerializer

        api_info = validated_data.pop("api_info", {})
        api_info.pop("id", "")

        remote_api = RemoteApi.objects.get(id=api_info["remote_api_id"])
        api_info.update(
            remote_api_info=RemoteApiSerializer(remote_api).data,
            map_code=remote_api.map_code,
            before_req=remote_api.before_req,
        )
        api_instance = RemoteApiInstance.objects.create(**api_info)
        validated_data["api_instance_id"] = api_instance.id

        validated_data["related_fields"] = self.get_related_fields(
            api_instance, validated_data
        )

        return validated_data


class FieldSerializer(TemplateFieldSerializer):
    """流程字段序列化"""

    class Meta:
        model = Field
        # 此处'workflow', 'workflow_id'，'state', 'state_id',兼容数据，方便前端处理
        fields = (
            "workflow",
            "workflow_id",
            "state",
            "state_id",
            "id",
            "key",
            "name",
            "source_type",
            "source_uri",
            "type",
            "desc",
            "is_builtin",
            "is_readonly",
            "meta",
            "api_instance_id",
            "related_fields",
            "layout",
            "validate_type",
            "regex",
            "regex_config",
            "custom_regex",
            "choice",
            "kv_relation",
            "default",
            "api_info",
            "is_tips",
            "tips",
            "show_type",
            "show_conditions",
            "source",
            "display",
        ) + model.FIELDS
        read_only_fields = ("is_builtin", "key") + model.FIELDS

    def __init__(self, *args, **kwargs):
        super(AuthModelSerializer, self).__init__(*args, **kwargs)
        self.resource_permissions = {}
        self.validators = [FieldValidator(self.instance)]

    def create(self, validated_data):
        """BEP: 创建state后的自定义行为"""
        state = validated_data["state"]
        workflow = validated_data["workflow"]
        instance = super(FieldSerializer, self).create(validated_data)
        with transaction.atomic():
            if (
                workflow.first_state.id == state.id
                and validated_data["key"] == "bk_biz_id"
            ):
                workflow.is_biz_needed = True
                workflow.save()
            instance.state.fields.append(instance.pk)
            instance.state.save()
        return instance

    def get_related_fields(self, api_instance, validated_data):
        related_fields = []
        api_config = api_instance.get_config()
        for key in Field.objects.filter(
            workflow_id=validated_data["workflow"]
        ).values_list("key", flat=True):
            if "${params_%s}" % key in json.dumps(api_config["query_params"]):
                related_fields.append(key)
        return {"rely_on": related_fields}


class RelatedFieldSerializer(serializers.Serializer):
    """关联参数字段序列化，删除字段时使用"""

    name = serializers.CharField(read_only=True)
    related_fields = serializers.JSONField(read_only=True)


class ConditionsFieldSerializer(serializers.Serializer):
    """展示条件参数字段序列化，删除字段时使用"""

    name = serializers.CharField(read_only=True)
    show_conditions = serializers.JSONField(read_only=True)


class TemplateFieldFilterSerializer(serializers.Serializer):
    """模板库过滤字段序列化"""

    update_at__gte = serializers.DateTimeField(
        required=False, format="%Y-%m-%d %H:%M:%S"
    )
    update_at__lte = serializers.DateTimeField(
        required=False, format="%Y-%m-%d %H:%M:%S"
    )
    order_by = serializers.CharField(required=False)


class TableSerializer(AuthModelSerializer):
    """基础模型序列化"""

    name = serializers.CharField(
        required=True,
        max_length=LEN_MIDDLE,
        validators=[
            UniqueValidator(queryset=Table.objects.all(), message=_("基础模型名称已经存在，请重新输入"))
        ],
    )
    desc = serializers.CharField(
        required=False, max_length=LEN_LONG, allow_blank=True, allow_null=True
    )
    fields = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=TemplateField.objects.all(),
        error_messages={"does_not_exist": _("该字段模板不存在，请检查")},
        many=True,
    )
    fields_order = serializers.JSONField(required=True, initial=list)

    class Meta:
        model = Table
        fields = (
            "id",
            "name",
            "desc",
            "fields",
            "fields_order",
            "is_builtin",
            "creator",
            "create_at",
            "update_at",
            "updated_by",
        )

    def to_representation(self, instance):
        data = super(TableSerializer, self).to_representation(instance)
        ordering = "FIELD(`id`, %s)" % ",".join(
            [str(field_id) for field_id in data["fields_order"]]
        )
        data["fields"] = TemplateFieldSerializer(
            TemplateField.objects.filter(id__in=data["fields"]).extra(
                select={"ordering": ordering}, order_by=("ordering",)
            ),
            many=True,
        ).data
        return data


class TableRetrieveSerializer(AuthModelSerializer):
    name = serializers.CharField(read_only=True)
    desc = serializers.CharField(read_only=True)
    fields = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    fields_order = serializers.JSONField(required=True)

    class Meta:
        model = Table
        fields = (
            "id",
            "name",
            "desc",
            "fields",
            "fields_order",
            "is_builtin",
            "creator",
            "create_at",
            "update_at",
            "updated_by",
        )

    def to_representation(self, instance):
        data = super(TableRetrieveSerializer, self).to_representation(instance)

        query_set = TemplateField.objects.filter(id__in=data["fields"])
        if self.context.get("is_biz_needed", True) is False:
            query_set = query_set.exclude(key=FIELD_BIZ)

        ordering = "FIELD(`id`, %s)" % ",".join(
            [str(field_id) for field_id in instance.fields_order]
        )
        data["fields"] = TemplateFieldSerializer(
            query_set.extra(select={"ordering": ordering}, order_by=("ordering",)),
            many=True,
        ).data
        return data

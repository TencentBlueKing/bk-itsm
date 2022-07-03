# coding=utf-8
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

from django.db import transaction
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.fields import JSONField, empty

from itsm.component.constants import (
    DISTRIBUTE_TYPE_CHOICES,
    EMPTY_STRING,
    LEN_NORMAL,
    PERSON,
    PROCESSOR_CHOICES,
    STATE_TYPE_CHOICES,
    TASK_SOPS_STATE,
    TASK_STATE,
    LEN_LONG,
    TASK_DEVOPS_STATE,
)
from itsm.component.exceptions import ParamError
from itsm.component.utils.basic import dotted_name, dotted_property
from itsm.postman.models import RemoteApi, RemoteApiInstance
from itsm.postman.serializers import RemoteApiSerializer, ApiInstanceSerializer
from itsm.workflow.models import GlobalVariable, State
from itsm.workflow.validators import (
    SopsStateValidator,
    StateGlobalVariablesValidator,
    StatePollValidator,
    StateProcessorsValidator,
    DevSopsStateValidator,
)


class StateSerializer(serializers.ModelSerializer):
    """状态序列化"""

    name = serializers.CharField(
        required=False,
        initial=EMPTY_STRING,
        max_length=LEN_NORMAL,
        allow_blank=True,
        allow_null=True,
    )
    desc = serializers.CharField(
        required=False, initial=EMPTY_STRING, max_length=LEN_NORMAL
    )
    type = serializers.ChoiceField(choices=STATE_TYPE_CHOICES, required=False)
    tag = serializers.CharField(required=False, max_length=LEN_LONG)
    processors = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    processors_type = serializers.ChoiceField(choices=PROCESSOR_CHOICES, required=False)
    assignors = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    assignors_type = serializers.ChoiceField(choices=PROCESSOR_CHOICES, required=False)
    delivers = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    delivers_type = serializers.ChoiceField(choices=PROCESSOR_CHOICES, required=False)
    can_deliver = serializers.BooleanField(required=False)
    fields = JSONField(required=False, initial=[])
    is_draft = serializers.BooleanField(required=False)
    is_terminable = serializers.BooleanField(required=False)
    axis = JSONField(required=False, initial={})
    variables = JSONField(required=False, initial={})
    distribute_type = serializers.ChoiceField(
        choices=DISTRIBUTE_TYPE_CHOICES, required=False
    )
    api_info = JSONField(required=False, initial={})
    finish_condition = JSONField(required=False, initial={})
    extras = JSONField(required=False, initial={})
    is_multi = serializers.BooleanField(required=False)

    class Meta:
        model = State
        fields = (
            "workflow",
            "id",
            "key",
            "name",
            "desc",
            "distribute_type",
            "axis",
            "is_builtin",
            "variables",
            "tag",
            "processors_type",
            "processors",
            "assignors",
            "assignors_type",
            "delivers",
            "delivers_type",
            "can_deliver",
            "extras",
            "is_draft",
            "is_terminable",
            "fields",
            "type",
            "api_info",
            "api_instance_id",
            "is_sequential",
            "finish_condition",
            "is_multi",
            "is_allow_skip",
        ) + model.FIELDS

        read_only_fields = model.FIELDS

    def update(self, instance, validated_data):
        with transaction.atomic():
            if validated_data.get("type", "") == "TASK":
                api_info = validated_data.pop("api_info", {})
                api_info.pop("remote_system_id", "")
                api_info.pop("id", "")

                remote_api = RemoteApi.objects.get(id=api_info["remote_api_id"])
                api_info["remote_api_info"] = RemoteApiSerializer(remote_api).data
                api_info.update(
                    map_code=remote_api.map_code,
                    before_req=remote_api.before_req,
                )

                api_instance = RemoteApiInstance.objects.create(**api_info)
                validated_data["api_instance_id"] = api_instance.id

                outputs = GlobalVariable.objects.create_global_variable(
                    instance.id,
                    instance.workflow_id,
                    instance.variables["outputs"],
                    validated_data["variables"]["outputs"],
                )
                validated_data["variables"].update(outputs=outputs)

            if validated_data.get("type", "") == "WEBHOOK":
                outputs = GlobalVariable.objects.create_global_variable(
                    instance.id,
                    instance.workflow_id,
                    instance.variables["outputs"],
                    validated_data["variables"]["outputs"],
                )
                validated_data["variables"].update(outputs=outputs)

            if validated_data.get("type", "") == "BK-PLUGIN":
                outputs = GlobalVariable.objects.create_global_variable(
                    instance.id,
                    instance.workflow_id,
                    instance.variables["outputs"],
                    validated_data["variables"]["outputs"],
                )
                validated_data["variables"].update(outputs=outputs)
            if validated_data.get("type", "") == "TASK-SOPS":
                GlobalVariable.objects.get_or_create(
                    key="sops_result_%s" % instance.id,
                    name="任务执行结果",
                    type="BOOLEAN",
                    is_valid=True,
                    state_id=instance.id,
                    flow_id=instance.workflow_id,
                )
                validated_data["variables"] = {
                    "inputs": [],
                    "outputs": [
                        {
                            "source": "global",
                            "name": "任务执行结果",
                            "key": "sops_result_%s" % instance.id,
                            "ref_path": "",
                            "type": "BOOLEAN",
                        }
                    ],
                }
            if validated_data.get("type", "") == "TASK-DEVOPS":
                outputs = GlobalVariable.objects.create_global_variable(
                    instance.id,
                    instance.workflow_id,
                    instance.variables["outputs"],
                    validated_data["variables"]["outputs"],
                )
                validated_data["variables"].update(outputs=outputs)

            state = super(StateSerializer, self).update(instance, validated_data)

            return state

    def to_internal_value(self, data):
        validated_data = super(StateSerializer, self).to_internal_value(data)

        if validated_data.get("processors_type") == PERSON:
            validated_data["processors"] = dotted_name(
                validated_data.get("processors", "")
            )

        if validated_data.get("assignors_type") == PERSON:
            validated_data["assignors"] = dotted_name(
                validated_data.get("assignors", "")
            )

        # 网关节点无需额外配置，直接为非草稿状态
        if validated_data.get("type") in ["ROUTER-P", "COVERAGE"]:
            validated_data.update(is_draft=False)

        return validated_data

    def to_representation(self, instance):
        data = super(StateSerializer, self).to_representation(instance)
        if data["processors_type"] == PERSON:
            data["processors"] = dotted_property(instance, "processors")
        if data["assignors_type"] == PERSON:
            data["assignors"] = dotted_property(instance, "assignors")
        if data["type"] == "TASK" and instance.api_instance:
            data["api_info"] = ApiInstanceSerializer(instance.api_instance).data
        if data["type"] == "NORMAL" and data["is_builtin"] is True:
            data["is_first_state"] = True
        else:
            data["is_first_state"] = False

        return data

    def get_variables(self, data):
        if self.instance is None:
            return {"inputs": [], "outputs": []}
        return data

    # =============================================== validate ===============

    def validate_name(self, value):
        if self.context["view"].action == "update":
            if not value:
                raise ParamError(_("节点名称不能为空"))
        return value

    def run_validation(self, data=empty):

        if self.context["view"].action != "update":
            return super(StateSerializer, self).run_validation(data)
        if self.instance.type == TASK_STATE:
            self.validators = [
                StatePollValidator(),
                StateGlobalVariablesValidator(self.instance),
            ]
            return super(StateSerializer, self).run_validation(data)
        elif self.instance.type == TASK_SOPS_STATE:
            self.validators = [
                SopsStateValidator(self.instance),
            ]
            return super(StateSerializer, self).run_validation(data)
        elif self.instance.type == TASK_DEVOPS_STATE:
            self.validators = [
                DevSopsStateValidator(self.instance),
            ]
            return super(StateSerializer, self).run_validation(data)
        else:
            self.validators = [
                StateProcessorsValidator(self.instance),
            ]
            return super(StateSerializer, self).run_validation(data)


class StateExtrasSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    extras = serializers.JSONField(read_only=True)

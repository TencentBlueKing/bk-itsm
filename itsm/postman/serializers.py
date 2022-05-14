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

from django.utils.translation import ugettext as _
from mako.template import Template
from rest_framework import serializers
from rest_framework.fields import JSONField

from itsm.component.constants import (
    LEN_LONG,
    LEN_NORMAL,
    LEN_SHORT,
    LEN_X_LONG,
    TASK_STATE,
    LEN_XX_LONG,
    PUBLIC_PROJECT_PROJECT_KEY,
)
from itsm.component.drf.serializers import DynamicFieldsModelSerializer
from itsm.component.exceptions import ParamError
from itsm.component.utils.basic import normal_name, dotted_name
from itsm.postman.models import RemoteApi, RemoteApiInstance, RemoteSystem
from itsm.workflow.models import Field, State


class RemoteSystemSerializer(serializers.ModelSerializer):
    """API系统序列化"""

    name = serializers.CharField(
        max_length=LEN_NORMAL, required=True, error_messages={"blank": _("名称不能为空")}
    )
    code = serializers.CharField(
        max_length=LEN_NORMAL, required=True, error_messages={"blank": _("编码不能为空")}
    )
    system_id = serializers.IntegerField(required=False)
    desc = serializers.CharField(max_length=LEN_LONG, required=False, allow_blank=True)
    owners = serializers.CharField(
        max_length=LEN_NORMAL, required=False, allow_blank=True
    )

    is_activated = serializers.BooleanField(required=True)
    headers = serializers.JSONField(required=True)
    cookies = serializers.JSONField(required=True)
    variables = serializers.JSONField(required=True)
    project_key = serializers.CharField(required=True, max_length=LEN_SHORT)

    class Meta:
        model = RemoteSystem
        fields = (
            "id",
            "name",
            "system_id",
            "domain",
            "code",
            "desc",
            "owners",
            "is_builtin",
            "is_activated",
            "headers",
            "cookies",
            "variables",
            "create_at",
            "update_at",
            "creator",
            "updated_by",
            "contact_information",
            "project_key",
        )
        read_only_fields = ("creator", "updated_by")

    def to_internal_value(self, data):
        # 新增系统时,system_id为空
        if not data.get("system_id"):
            data.pop("system_id")

        data = super(RemoteSystemSerializer, self).to_internal_value(data)
        return data

    def to_representation(self, instance):
        data = super(RemoteSystemSerializer, self).to_representation(instance)
        data["can_edit"] = True
        return data

    # ====================================== validate ========================
    def validate_code(self, value):
        if self.instance:
            if (
                RemoteSystem.objects.filter(code=value)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise ParamError(_("该系统已经存在，请重新选择"))
        else:
            if RemoteSystem.objects.filter(code=value).exists():
                raise ParamError(_("该系统已经存在，请重新选择"))
        return value


class RemoteApiSerializer(DynamicFieldsModelSerializer):
    """API序列化"""

    name = serializers.CharField(
        required=True, error_messages={"blank": _("名称不能为空")}, max_length=LEN_NORMAL
    )
    path = serializers.CharField(
        required=True, error_messages={"blank": _("路径不能为空")}, max_length=LEN_X_LONG
    )
    version = serializers.CharField(required=False, max_length=LEN_SHORT)
    func_name = serializers.CharField(
        required=True, error_messages={"blank": _("调用函数不能为空")}, max_length=LEN_NORMAL
    )
    method = serializers.ChoiceField(
        choices=[("GET", "GET"), ("POST", "POST")], default="GET"
    )
    desc = serializers.CharField(max_length=LEN_LONG, required=False, allow_blank=True)
    owners = serializers.CharField(
        required=False, max_length=LEN_XX_LONG, allow_blank=True
    )

    is_activated = serializers.BooleanField(required=True)
    req_headers = serializers.JSONField(required=True)
    req_params = serializers.JSONField(required=True)
    req_body = serializers.JSONField(required=True)
    rsp_data = serializers.JSONField(required=True)
    map_code = serializers.CharField(required=False, allow_blank=True)
    before_req = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = RemoteApi
        fields = (
            "id",
            "remote_system",
            "remote_system_name",
            "name",
            "owners",
            "path",
            "version",
            "method",
            "func_name",
            "desc",
            "is_activated",
            "req_headers",
            "req_params",
            "req_body",
            "rsp_data",
            "map_code",
            "before_req",
            "create_at",
            "update_at",
            "creator",
            "updated_by",
            "is_builtin",
        )
        read_only_fields = ("creator", "updated_by")

    def to_internal_value(self, data):
        data = super(RemoteApiSerializer, self).to_internal_value(data)
        if "owners" in data:
            data["owners"] = dotted_name(data["owners"])
        return data

    def to_representation(self, instance):
        data = super(RemoteApiSerializer, self).to_representation(instance)
        api_instance_ids = instance.api_instances.values_list("id", flat=True)
        field_count = Field.objects.filter(api_instance_id__in=api_instance_ids).count()
        state_count = State.objects.filter(
            type=TASK_STATE, api_instance_id__in=api_instance_ids
        ).count()

        data["count"] = field_count + state_count
        data["owners"] = normal_name(data.get("owners"))
        if instance.remote_system.project_key == PUBLIC_PROJECT_PROJECT_KEY:
            return self.update_auth_actions(instance, data)

        data["auth_actions"] = []
        return data

    # ====================================== validate ========================
    def validate_name(self, value):
        if self.instance:
            if (
                RemoteApi.objects.filter(name=value)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise ParamError(_("该接口名称已存在，请重新输入"))
        else:
            if RemoteApi.objects.filter(name=value).exists():
                raise ParamError(_("该接口名称已存在，请重新输入"))
        return value


class ApiInstanceSerializer(serializers.ModelSerializer):
    req_params = JSONField(required=False, initial=[])
    req_body = JSONField(required=False, initial={})
    rsp_data = JSONField(required=False, initial={})
    map_code = serializers.CharField(required=False, allow_blank=True)
    before_req = serializers.CharField(required=False, allow_blank=True)
    succeed_conditions = JSONField(required=False, initial={})
    end_conditions = JSONField(required=False, initial={})
    need_poll = serializers.BooleanField(required=False, initial=False)

    remote_api_info = JSONField(required=False, read_only=True, initial={})

    class Meta:
        model = RemoteApiInstance
        fields = (
            "id",
            "remote_system_id",
            "remote_api_id",
            "req_params",
            "req_body",
            "rsp_data",
            "map_code",
            "before_req",
            "succeed_conditions",
            "end_conditions",
            "need_poll",
            "remote_api_info",
            "map_code",
            "before_req",
        )

    def to_representation(self, instance):
        data = super(ApiInstanceSerializer, self).to_representation(instance)
        data["remote_api_info"].update(
            system_info=instance.remote_api.remote_system.data_to_dict()
        )
        return data


class TaskStateApiInfoSerializer(ApiInstanceSerializer):
    """API配置及返回数据"""

    remote_api_info = JSONField(required=False, read_only=True, initial={})

    class Meta:
        model = RemoteApiInstance
        fields = (
            "id",
            "remote_system_id",
            "remote_api_id",
            "req_params",
            "req_body",
            "rsp_data",
            "succeed_conditions",
            "end_conditions",
            "need_poll",
            "remote_api_info",
        )

    def to_representation(self, instance):
        from itsm.ticket.serializers import TicketGlobalVariableSerializer

        status = self.context["status"]
        data = super(TaskStateApiInfoSerializer, self).to_representation(instance)
        data.update(
            output_variables=TicketGlobalVariableSerializer(
                status.global_variables, many=True
            ).data,
            response={},
        )

        params = {
            "params_%s" % field["key"]: field["value"]
            for field in status.ticket.get_output_fields(need_display=True)
        }
        try:
            req_body_data = json.loads(
                Template(json.dumps(data["req_body"])).render(**params)
            )
            req_params = json.loads(
                Template(json.dumps(data["req_params"])).render(**params)
            )
        except Exception:
            req_body_data = {}
            req_params = {}
        data["req_body"] = req_body_data
        data["req_params"] = req_params
        data["method"] = instance.remote_api.method
        return data

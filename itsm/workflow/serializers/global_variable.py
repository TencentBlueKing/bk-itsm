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

from itsm.workflow.models import GlobalVariable, State


class GlobalVariableSerializer(serializers.ModelSerializer):
    """全局变量序列化"""

    meta = JSONField(required=False, initial={})

    class Meta:
        model = GlobalVariable
        fields = ("id", "key", "name", "type", "meta")

    def to_representation(self, instance):

        data = super(GlobalVariableSerializer, self).to_representation(instance)
        try:
            state_name = State.objects.get(id=instance.state_id).name
            state_name = state_name if state_name else _("当前节点")
            data.update(name="%s(%s)" % (data["name"], state_name))
        except State.DoesNotExist:
            data.update(name="%s(%s)" % (data["name"], _("当前节点")))

        # 统一格式
        if data.get("meta", {}).get("type"):
            data["type"] = data["meta"]["type"]
        data["choice"] = (
            data["meta"]["choice"] if data.get("meta", {}).get("choice") else []
        )
        data["source"] = "global"
        data["source_uri"] = ""
        data["source_type"] = ""
        return data


class GlobalVariableGroupSerializer(GlobalVariableSerializer):
    def to_representation(self, instance):

        data = super(GlobalVariableSerializer, self).to_representation(instance)
        try:
            state_name = State.objects.get(id=instance.state_id).name
            state_name = state_name if state_name else _("当前节点")
            data.update(name="%s(%s)" % (data["name"], state_name))
        except State.DoesNotExist:
            state_name = _("当前节点")
            data.update(name="%s(%s)" % (data["name"], state_name))

        # 统一格式
        if data.get("meta", {}).get("type"):
            data["type"] = data["meta"]["type"]
        data["choice"] = (
            data["meta"]["choice"] if data.get("meta", {}).get("choice") else []
        )
        data["state"] = state_name
        data["source"] = "global"
        data["source_uri"] = ""
        data["source_type"] = ""
        return data

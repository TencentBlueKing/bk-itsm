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

from rest_framework import serializers
from rest_framework.fields import JSONField, empty

from itsm.component.constants import TRIGGER_TYPE
from itsm.workflow.models import Trigger
from itsm.workflow.validators import TriggerValidator


class TriggerSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=TRIGGER_TYPE)
    inputs = JSONField(required=False, initial={})
    condition = JSONField(required=False, initial={})

    class Meta:
        model = Trigger
        fields = (
            'id',
            'name',
            'component_key',
            'type',
            'inputs',
            'condition',
            'state_id',
            'workflow_id',
        ) + model.FIELDS
        read_only_fields = model.FIELDS

    def run_validation(self, data=empty):
        self.validators = [TriggerValidator(self.instance)]
        return super(TriggerSerializer, self).run_validation(data)

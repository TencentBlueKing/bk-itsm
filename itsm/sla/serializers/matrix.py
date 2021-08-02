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

from bulk_update.helper import bulk_update
from itsm.component.constants import EMPTY_STRING, PRIORITY
from itsm.service.models import SysDict
from itsm.sla.models import PriorityMatrix


class PriorityMatrixSerializer(serializers.ModelSerializer):
    """服务优先级矩阵序列化"""

    class Meta:
        model = PriorityMatrix
        fields = ('id', 'service_type', 'urgency', 'impact', 'priority',) + model.DISPLAY_FIELDS

        read_only_fields = model.DISPLAY_FIELDS


class MatrixListSerializer(serializers.ListSerializer):
    """重写列表序列化类，提供批量更新方法"""

    def update(self, instance, validated_data, other_types=None):
        """批量更新，返回更新的数量"""

        item_hash = {item['id']: item for item in validated_data}

        priorities = []
        for p in PriorityMatrix.objects.filter(pk__in=list(item_hash.keys())):
            p.priority = item_hash[p.id]['priority']
            priorities.append(p)

        # 其他类型更新
        other_types = [] if other_types is None else other_types
        for other_type in other_types:
            for i in validated_data:
                p = PriorityMatrix.objects.get(service_type=other_type, urgency=i["urgency"], impact=i["impact"])
                p.priority = i['priority']
                priorities.append(p)

        return bulk_update(priorities, update_fields=['priority'])


class MatrixUpdateSerializer(serializers.ModelSerializer):
    """服务优先级矩阵元素序列化"""

    id = serializers.IntegerField()
    impact = serializers.CharField(required=False)
    urgency = serializers.CharField(required=False)

    class Meta:
        model = PriorityMatrix
        list_serializer_class = MatrixListSerializer
        fields = (
            'id',
            'priority',
            'impact',
            'urgency'
        )

    def validate_priority(self, value):
        priority_set = SysDict.get_data_by_key(PRIORITY, 'sets')
        priority_set.add(EMPTY_STRING)

        if value not in priority_set:
            raise serializers.ValidationError(_("请指定合法的优先级选项"))

        return value

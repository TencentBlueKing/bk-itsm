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

import itertools
from bulk_update.helper import bulk_update

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.constants import PRIORITY, PX_URGENCY, PY_IMPACT, ResponseCodeStatus
from itsm.component.drf.viewsets import ModelViewSet
from itsm.service.models import DictData, SysDict
from itsm.sla.models import PriorityMatrix
from itsm.sla.permissions import SlaMatrixPermit
from itsm.sla.serializers import PriorityMatrixSerializer
from itsm.sla.validators import (
    matrix_of_service_type_validate,
    priority_matrix_batch_update_validate,
)


class PriorityMatrixViewSet(ModelViewSet):
    """优先级矩阵视图"""

    serializer_class = PriorityMatrixSerializer
    queryset = PriorityMatrix.objects.all()
    pagination_class = None
    permission_classes = (SlaMatrixPermit,)

    filter_fields = {
        'service_type': ['exact', 'in'],
    }

    @action(detail=False, methods=['put'])
    def batch_update(self, request):
        """
        批量更新优先级矩阵
        """
        service_type = request.data.get('service_type', [])
        impact = request.data.get('impact', [])
        urgency = request.data.get('urgency', [])
        priority_matrix = request.data.get('priority_matrix', [])

        priority_matrix_batch_update_validate(service_type, impact, urgency, priority_matrix)

        # 获取紧急程度/影响范围的启用/禁用的key值
        def split_keys(key_info_list):
            """拆分成2个列表，一个是启用key列表，另一个是禁用key列表"""
            enabled_keys = []
            disabled_keys = []
            for key_info in key_info_list:
                if key_info['is_enabled']:
                    enabled_keys.append(key_info['key'])
                else:
                    disabled_keys.append(key_info['key'])

            return enabled_keys, disabled_keys

        enabled_impact_keys, disabled_impact_keys = split_keys(impact)
        enabled_urgency_keys, disabled_urgency_keys = split_keys(urgency)

        # 紧急程度/影响范围的启用项系统数据字典
        tables = []
        for s in service_type:
            impact_dict_table = SysDict.objects.get(key='%s_%s' % (s.upper(), PY_IMPACT))
            urgency_dict_table = SysDict.objects.get(key='%s_%s' % (s.upper(), PX_URGENCY))
            tables.append(
                {"impact_dict_table": impact_dict_table, "urgency_dict_table": urgency_dict_table})

        with transaction.atomic():
            # 更新紧急程度/影响范围的启用维度
            # 删除 禁用key列表
            for table in tables:
                DictData.objects.filter(
                    (Q(key__in=disabled_impact_keys) & Q(dict_table=table["impact_dict_table"]))
                    | (Q(key__in=disabled_urgency_keys) & Q(dict_table=table["urgency_dict_table"]))
                ).delete()

                # 新建或者激活，激活表示把已软删除的对象恢复
                DictData.active_dict_data(enabled_impact_keys, table["impact_dict_table"])
                DictData.active_dict_data(enabled_urgency_keys, table["urgency_dict_table"])

            # 更新优先级矩阵
            priorities = []
            for s in service_type:
                for m in priority_matrix:
                    p, created = PriorityMatrix.objects.get_or_create(
                        defaults={"priority": m["priority"]},
                        **{"impact": m["impact"], "urgency": m["urgency"], "service_type": s}
                    )
                    p.priority = m["priority"]
                    priorities.append(p)

            bulk_update(priorities, update_fields=['priority'])

        return Response()

    @action(detail=False, methods=['post'])
    def matrix_of_service_type(self, request, *args, **kwargs):
        """
        获取指定服务类型下的矩阵视图全量数据，紧急程度/影响范围/优先级
        """
        service_type = request.data.get('service_type')

        matrix_of_service_type_validate(service_type)

        # 影响范围
        impacts = PriorityMatrix.objects.get_dict_datas(service_type, PY_IMPACT)
        # 紧急程度
        urgencies = PriorityMatrix.objects.get_dict_datas(service_type, PX_URGENCY)
        # 优先级
        priorities = SysDict.get_data_by_key(PRIORITY)

        # 优先级 交叉值，不存在则新增
        priority_matrices = []
        for impact, urgency in itertools.product(impacts, urgencies):
            instance, created = PriorityMatrix.objects.get_or_create(
                service_type=service_type, impact=impact["key"], urgency=urgency["key"]
            )
            priority_matrices.append(PriorityMatrixSerializer(instance=instance).data)

        return Response(
            {'impact': impacts, 'urgency': urgencies, 'priority': priorities,
             'priority_matrix': priority_matrices}
        )

    @action(detail=False, methods=['post'], permission_classes=())
    def priority_value(self, request, *args, **kwargs):
        """根据影响范围、紧急度获取优先级"""
        service_type = request.data.get('service_type')
        urgency = request.data.get('urgency')
        impact = request.data.get('impact')

        priority = get_object_or_404(PriorityMatrix, service_type=service_type, urgency=urgency,
                                     impact=impact).priority

        return Response({'result': True, 'code': ResponseCodeStatus.OK, 'message': 'success',
                         'data': priority, })

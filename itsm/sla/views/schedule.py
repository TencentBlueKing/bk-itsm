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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.sla.models import Day, Schedule
from itsm.sla.serializers import DaySerializer, ScheduleDayRelationSerializer, ScheduleSerializer
from itsm.sla.validators import schedule_can_destroy

from .basic import ModelViewSet
from ..permissions import SchedulePermit
from ...component.constants import DEFAULT_PROJECT_PROJECT_KEY
from ...component.drf.viewsets import AuthModelViewSet


class ScheduleViewSet(AuthModelViewSet):
    """Schedule视图集合"""

    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all()
    pagination_class = None
    permission_free_actions = ["list"]
    permission_classes = (SchedulePermit, )
    ordering_fields = '__all__'
    filter_fields = {
        "id": ["exact", "in"],
        "name": ["exact", "in"],
    }
    
    def list(self, request, *args, **kwargs):
        project_key = self.request.query_params.get("project_key", DEFAULT_PROJECT_PROJECT_KEY)
        queryset = self.filter_queryset(self.get_queryset().filter(project_key=project_key))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """重写删除"""
        instance = self.get_object()

        # 可删除校验
        schedule_can_destroy(instance)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['put'])
    def add_day(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ScheduleDayRelationSerializer(
            instance, data=request.data, **{"context": self.get_serializer_context()}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def days(self, request, *args, **kwargs):
        type_of_day = request.GET.get("type_of_day", 'days')
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data.get(type_of_day, []))


class DayViewSet(ModelViewSet):
    """Schedule视图集合"""

    serializer_class = DaySerializer
    queryset = Day.objects.all()
    pagination_class = None
    filter_fields = {
        "id": ["exact", "in"],
        "type_of_day": ["exact", "in"],
    }
    ordering_fields = '__all__'

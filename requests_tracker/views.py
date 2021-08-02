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

import datetime
import json

from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.drf import viewsets as component_viewsets
from itsm.component.utils.misc import JsonEncoder
from requests_tracker.models import Record
from requests_tracker.serializers import (
    RecordFilterSerializer,
    RecordRetriveSerializer,
    RecordSerializer,
)


__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."


class RecordModelViewSet(component_viewsets.ReadOnlyModelViewSet):
    """用户收藏视图"""

    serializer_class = RecordSerializer
    queryset = Record.objects.all()

    filter_fields = {
        "url": ["exact", "contains", "startswith"],
        "method": ["exact", "in"],
        "status_code": ["exact", "in"],
        "api_instance_id": ["exact", "in"],
        "ticket_id": ["exact", "in"],
    }

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecordRetriveSerializer

        return RecordSerializer

    def list(self, request, *args, **kwargs):
        """列表查询视图
        """

        queryset = self.filter_queryset(self.get_queryset())

        if queryset:
            filter_serializer = RecordFilterSerializer(
                data=request.query_params)
            filter_serializer.is_valid(raise_exception=True)
            kwargs = filter_serializer.validated_data

            status = kwargs.get('status')
            name__contains = kwargs.get('name__contains')
            start_time = kwargs.get('date_created__gte')
            end_time = kwargs.get('date_created__lte')

            if name__contains:
                queryset = queryset.filter(url__icontains=name__contains)

            if status:
                status = int(status[:-1]) * 10
                queryset = queryset.filter(
                    status_code__range=(
                        status, status + 99))

            if start_time and end_time:
                queryset = queryset.filter(
                    date_created__range=(
                        start_time, end_time))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def exports(self, request, pk=None):
        """
        导出请求记录
        """
        record = self.get_object()
        data = RecordRetriveSerializer(record).data
        response = HttpResponse(content_type='application/json; charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=bk_itsm_{}_{}.json".format(
            record.url.strip('/').rsplit('/')[-1],
            datetime.datetime.now().strftime('%Y%m%d%H%M')
        )

        # 统一导入导出格式为列表数据
        response.write(json.dumps([data], cls=JsonEncoder, indent=2))

        return response

    @action(detail=False, methods=['get'])
    def batch_exports(self, request, pk=None):
        """
        批量导出请求记录
        """
        logs = request.query_params.get('logs', '').split(',')
        records = Record.objects.filter(id__in=logs)
        data = RecordRetriveSerializer(records, many=True).data
        response = HttpResponse(content_type='application/json; charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=bk_itsm_api_log_{}.json".format(
            datetime.datetime.now().strftime('%Y%m%d%H%M')
        )

        # 统一导入导出格式为列表数据
        response.write(json.dumps(data, cls=JsonEncoder, indent=2))

        return response

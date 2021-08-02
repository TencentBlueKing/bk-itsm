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

from collections import defaultdict

from django.db import transaction
from django.db.models import Q
from django.utils.translation import ugettext as _
from django_bulk_update.helper import bulk_update
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from itsm.component.constants import FIRST_ORDER
from itsm.component.drf import viewsets as component_viewsets
from itsm.service.validators import service_type_validator
from itsm.ticket_status.models import StatusTransit, TicketStatus, TicketStatusConfig
from itsm.ticket_status.permissions import TicketStatusPermit
from itsm.ticket_status.serializers import (
    StatusTransitSerializer,
    TicketStatusConfigSerializer,
    TicketStatusOptionSerializer,
    TicketStatusSerializer,
)
from itsm.ticket_status.validators import (
    from_status_id_validator,
    save_ticket_status_validate,
    save_transit_validate,
    set_transit_rule_validate,
)


class ModelViewSet(component_viewsets.AuthWithoutResourceModelViewSet):
    """按需改造DRF默认的ModelViewSet类"""

    def perform_create(self, serializer):
        """创建时补充基础Model中的字段"""
        user = serializer.context.get('request').user
        username = getattr(user, 'username', 'guest')
        serializer.save(creator=username, updated_by=username)
        # 更新和创建都要更新TicketStatusConfig表的信息
        service_type = serializer.data.get('service_type')
        TicketStatusConfig.update_config(service_type, user)

    def perform_update(self, serializer):
        """更新时补充基础Model中的字段"""
        user = serializer.context.get('request').user
        username = getattr(user, 'username', 'guest')
        serializer.save(updated_by=username)
        # 更新和创建都要更新TicketStatusConfig表的信息
        service_type = serializer.data.get('service_type')
        TicketStatusConfig.update_config(service_type, user)


class TicketStatusViewSet(ModelViewSet):
    serializer_class = TicketStatusSerializer
    queryset = TicketStatus.objects.all()
    pagination_class = None
    ordering_fields = ("order",)
    permission_classes = (TicketStatusPermit, )

    filter_fields = {
        "service_type": ["exact"],
        "flow_status": ["exact", "contains"],
    }

    def perform_destroy(self, instance):
        """自定义删除前行为"""

        if instance.is_builtin:
            raise ValidationError(_("抱歉，内置工单状态无法被删除"))
        else:
            instance.delete()

    @action(detail=False, methods=['get'])
    def get_configs(self, request, *args, **kwargs):
        ticket_status_config = TicketStatusConfig.objects.all()
        ticket_status_config_data = TicketStatusConfigSerializer(instance=ticket_status_config, many=True)
        return Response(ticket_status_config_data.data)

    @action(detail=True, methods=['post'])
    def set_transit_rule(self, request, *args, **kwargs):
        """设置状态转换规则"""
        instance = self.get_object()
        to_status_id = request.data.get("to_status")
        threshold = request.data.get("threshold")
        threshold_unit = request.data.get("threshold_unit")

        set_transit_rule_validate(instance, to_status_id, threshold, threshold_unit)

        with transaction.atomic():
            # 一个状态转换来源只能设置唯一一个自动转换规则
            StatusTransit.objects.filter(from_status_id=instance.id).update(is_auto=False)
            StatusTransit.objects.update_or_create(
                defaults={"is_auto": True, "threshold": threshold, "threshold_unit": threshold_unit},
                **{"from_status_id": instance.id, "to_status_id": to_status_id, "service_type": instance.service_type}
            )
        return Response()

    @action(detail=True, methods=['post'])
    def close_transit_rule(self, request, *args, **kwargs):
        """关闭状态流转规则"""
        instance = self.get_object()
        StatusTransit.objects.filter(from_status_id=instance.id).update(is_auto=False)
        return Response()

    @action(detail=False, methods=['post'])
    def save_status_of_service_type(self, request, *args, **kwargs):
        """保存工单状态"""
        service_type = request.data.get("service_type")
        ticket_status_ids = request.data.get("ticket_status_ids", [])
        start_status_id = request.data.get("start_status_id")
        over_status_ids = request.data.get("over_status_ids", [])

        save_ticket_status_validate(service_type, ticket_status_ids, start_status_id, over_status_ids)

        # 按照自定义顺序获取工单状态
        ordering = 'FIELD(`id`, {})'.format(','.join(["'{}'".format(v) for v in ticket_status_ids]))
        ticket_status = TicketStatus.objects.status_of_service_type(service_type).extra(
            select={"ordering": ordering}, order_by=["ordering"]
        )

        for index, s in enumerate(ticket_status):
            is_start = False
            is_over = False
            # 设置排序序号
            s.order = FIRST_ORDER + index

            if s.id == start_status_id:
                is_start = True

            if s.id in over_status_ids:
                is_over = True

            s.is_start = is_start
            s.is_over = is_over

        # 批量更新指定字段
        bulk_update(ticket_status, update_fields=["order", "is_start", "is_over"])
        return Response()

    @action(detail=False, methods=['get'])
    def next_over_status(self, request, *args, **kwargs):
        query_params = dict(service_type=request.query_params.get("service_type"), key=request.query_params.get("key"))
        instance = get_object_or_404(self.queryset, **query_params)
        return Response(TicketStatusOptionSerializer(instance.to_over_status, many=True).data)

    @action(detail=False, methods=['get'])
    def overall_ticket_statuses(self, request, *args, **kwargs):
        """全局视图的工单状态"""
        status_names = TicketStatus.objects.get_overall_status_names()
        return Response([{"name": name, "key": key} for key, name in status_names.items()])


class StatusTransitViewSet(ModelViewSet):
    serializer_class = StatusTransitSerializer
    queryset = StatusTransit.objects.all()
    pagination_class = None

    filter_fields = {
        "service_type": ["exact"],
    }

    def get_queryset(self):
        """支持额外过滤参数[service_type]"""
        service_type = self.request.query_params.get("service_type")

        if service_type:
            service_type_validator(service_type)
            queryset = self.queryset.filter(service_type=service_type)
        else:
            queryset = super(StatusTransitViewSet, self).get_queryset()

        return queryset

    @action(detail=False, methods=['get'])
    def is_auto(self, request, *args, **kwargs):
        """工单状态是否自动转换"""
        queryset = self.get_queryset()

        auto_transits = defaultdict(bool)
        for item in queryset:
            if auto_transits[item.from_status_id]:
                continue

            auto_transits[item.from_status_id] = item.is_auto

        return Response(auto_transits)

    @action(detail=False, methods=['get'])
    def get_auto_detail(self, request, *args, **kwargs):
        """获取工单状态自动流转的详细信息"""
        from_status_id = request.query_params.get("from_status_id")

        from_status_id_validator(from_status_id)

        status_transit_data = StatusTransit.objects.filter(Q(from_status_id=from_status_id) & Q(is_auto=True)).first()
        if not status_transit_data:
            return Response()
        data = StatusTransitSerializer(instance=status_transit_data).data
        return Response(data)

    @action(detail=False, methods=['post'])
    def save_transit_of_service_type(self, request, *args, **kwargs):
        """保存状态转换规则"""
        service_type = request.data.get("service_type")
        transits = request.data.get("transits")

        save_transit_validate(service_type, transits)

        queryset = self.get_queryset().filter(service_type=service_type)

        # TODO: 不确定是否还有更加优雅的写法
        with transaction.atomic():
            # 更新前数据(A)和更新后数据(B)进行比较，在A不在B则删除，在B不在A则新增
            # 待删除
            deleted_transit_ids = []
            for item in queryset:
                for transit in transits:
                    if item.from_status_id == transit["from_status"] and item.to_status_id == transit["to_status"]:
                        break
                else:
                    deleted_transit_ids.append(item.id)

            # 批量删除
            StatusTransit.objects.filter(id__in=deleted_transit_ids).delete()

            # 待新增
            created_transits = []
            for transit in transits:
                for item in queryset:
                    if transit["from_status"] == item.from_status_id and transit["to_status"] == item.to_status_id:
                        break
                else:
                    created_transits.append(transit)

            # 批量新增
            transit_bulks = []
            for created_transit in created_transits:
                transit_bulks.append(
                    StatusTransit(
                        service_type=service_type,
                        from_status_id=created_transit["from_status"],
                        to_status_id=created_transit["to_status"],
                        is_auto=False,
                    )
                )
            StatusTransit.objects.bulk_create(transit_bulks)

        return Response()

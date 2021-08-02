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

from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.drf.exception import ValidationError
from itsm.component.drf.viewsets import NormalModelViewSet, AuthModelViewSet
from itsm.sla.models import ActionPolicy, PriorityPolicy, Sla, SlaTimerRule, SlaTicketHighlight
from itsm.sla.serializers import (
    ActionPolicySerializer,
    PriorityPolicySerializer,
    SlaSerializer,
    SlaTimerRuleSerializer,
    TicketHighlightSerializer
)
from itsm.sla.validators import sla_can_destroy
from itsm.ticket_status.models import TicketStatus, TicketStatusConfig
from .basic import ModelViewSet
from ..permissions import SlaPermit
from ...component.constants import DEFAULT_PROJECT_PROJECT_KEY


class SlaTimerRuleViewSet(ModelViewSet):
    """SLA起止规则视图"""

    serializer_class = SlaTimerRuleSerializer
    queryset = SlaTimerRule.objects.all()
    pagination_class = None
    permission_classes = ()

    filter_fields = {
        "service_type": ["exact", "in"],
        "condition_type": ["exact", "in"],
    }

    def create(self, request, *args, **kwargs):
        if not request.data.get("batch_create", False):
            return super(SlaTimerRuleViewSet, self).create(request, *args, **kwargs)
        return self.batch_create(request, *args, **kwargs)

    def batch_create(self, request, *args, **kwargs):
        """
        批量创建
        """
        data = request.data
        basic_info = {"name": data['name'], "service_type": data['service_type']}
        rules = []
        for rule in data['rules']:
            rule.update(basic_info)
            serializer = self.get_serializer(data=rule)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            rules.append(serializer.data)

        # 创建完后，修改工单状态配置为已配置状态
        TicketStatusConfig.update_config(data['service_type'], request.user, True)

        return Response(rules, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'])
    def batch_update(self, request, *args, **kwargs):
        """
        批量修改
        """

        data = request.data
        basic_info = {"name": data['name'], "service_type": data['service_type']}
        rules = []
        for rule in data['rules']:
            rule.update(basic_info)
            try:
                instance = self.queryset.get(id=rule.pop("id", 0))
            except SlaTimerRule.DoesNotExist:
                instance = None

            serializer = self.get_serializer(instance, data=rule)
            serializer.is_valid(raise_exception=True)
            if instance is None:
                self.perform_create(serializer)
            else:
                self.perform_update(serializer)
            rules.append(serializer.data)
        # 修改完后，修改工单状态配置为已配置状态
        TicketStatusConfig.update_config(data['service_type'], request.user, True)
        return Response(rules)


class PriorityPolicyViewSet(ModelViewSet):
    """
    优先级处理时长策略视图
    """

    serializer_class = PriorityPolicySerializer
    queryset = PriorityPolicy.objects.all()
    pagination_class = None

    filter_fields = {
        "priority": ["exact", "in"],
    }


class ActionPolicyViewSet(ModelViewSet):
    """
    优先级处理时长策略视图
    """

    serializer_class = ActionPolicySerializer
    queryset = ActionPolicy.objects.all()
    pagination_class = None

    filter_fields = {
        "name": ["exact", "in"],
    }


class SlaViewSet(AuthModelViewSet):
    """服务协议视图"""

    serializer_class = SlaSerializer
    queryset = Sla.objects.all()
    permission_classes = (SlaPermit, )
    permission_free_actions = ["list"]
    filter_fields = {
        "name": ["exact", "contains", "icontains"],
        "is_enabled": ["exact", "in"],
        "updated_by": ["exact", "contains"],
    }

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None
        return super(SlaViewSet, self).get_queryset().filter()
    
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
        sla_can_destroy(instance)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        """重写执行更新行为"""
        is_enabled = serializer.validated_data.get("is_enabled", False)
        # 禁用协议
        if not is_enabled:
            is_over_statuses = TicketStatus.objects.get_is_over_statuses()

            # 拼接获取结束单据状态的筛选条件
            is_over_q = Q()
            for service_type, statuses in is_over_statuses.items():
                sub_q = Q()
                sub_q.connector = "AND"
                sub_q.children.extend([("service_type", service_type), ("current_status__in", statuses)])
                is_over_q.add(sub_q, "OR")

            if serializer.instance.get_tickets().exclude(is_over_q).exists():
                raise ValidationError(_("抱歉, 该协议下存在运行中的单据, 无法禁用!"))
        super(SlaViewSet, self).perform_create(serializer)

    @action(detail=False, methods=["put"])
    def ticket_highlight(self, request, *args, **kwargs):
        alert_color = request.data.get("alert_color")
        timeout_color = request.data.get("timeout_color")
        # SlaTicketHighlight只维护一行，记录sla单据背景颜色
        color_setting = SlaTicketHighlight.objects.first()
        color_setting.reply_timeout_color = alert_color
        color_setting.handle_timeout_color = timeout_color
        color_setting.save()
        return Response()


class TicketHighlightViewSet(NormalModelViewSet):
    """单据高亮偏好设定视图"""

    serializer_class = TicketHighlightSerializer
    queryset = SlaTicketHighlight.objects.all()

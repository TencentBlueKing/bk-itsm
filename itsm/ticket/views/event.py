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

from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.constants import SYS
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.utils.human import get_time
from itsm.ticket.models import TicketEventLog
from itsm.ticket.models import Ticket
from itsm.ticket.permissions import EventLogPermissionValidate
from itsm.ticket.serializers import EventSerializer
from itsm.ticket.utils import translate


class EventLogViewSet(component_viewsets.ReadOnlyModelViewSet):
    """日志视图"""

    pagination_class = None
    queryset = TicketEventLog.objects.all().select_related("ticket")
    serializer_class = EventSerializer
    filter_fields = {
        "status": ["exact"],
        "type": ["exact", "in"],
        "from_state_id": ["exact"],
    }
    permission_classes = (EventLogPermissionValidate,)

    def get_queryset(self):
        """
        重写get_queryset
        :return:
        """
        queryset = super(EventLogViewSet, self).get_queryset()
        if not self.request.query_params.get("ticket"):
            # 不存在的请求参数，直接返回全部
            return queryset

        master_ticket = Ticket.objects.get_master_ticket(self.request.query_params['ticket'])
        if not master_ticket:
            return queryset

        return queryset.filter(ticket=master_ticket)

    @action(detail=False, methods=["get"])
    def get_index_ticket_event_log(self, request):
        """我的动态：最近一周的操作日志"""

        pre_week_day = datetime.datetime.now() - datetime.timedelta(days=7)
        logs = (
            self.queryset.filter(operator=request.user.username, ticket__is_draft=False, operate_at__gte=pre_week_day)
            .exclude(source=SYS)
            .values(
                "operate_at",
                "ticket__sn",
                "message",
                "ticket__service",
                "ticket_id",
                "operator",
                "from_state_name",
                "action",
                "detail_message",
            )
            .order_by("-operate_at")[:6]
        )

        language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME, 'zh_CN')
        return Response(
            [
                dict(
                    id=log["ticket_id"],
                    time="{}".format(get_time(log["operate_at"], language)),
                    sn=log["ticket__sn"],
                    type=log["ticket__service"],
                    message=translate(log['message'], log),
                )
                for log in logs
            ]
        )

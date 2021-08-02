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

from rest_framework.routers import DefaultRouter

from itsm.sla.views import DayViewSet, PriorityMatrixViewSet, ScheduleViewSet
from itsm.sla.views.policy import (
    ActionPolicyViewSet,
    PriorityPolicyViewSet,
    SlaTimerRuleViewSet,
    SlaViewSet,
    TicketHighlightViewSet
)


routers = DefaultRouter(trailing_slash=True)

routers.register(r'schedules', ScheduleViewSet, basename="schedule")
routers.register(r'days', DayViewSet, basename="day")
routers.register(r'matrixs', PriorityMatrixViewSet, basename="matrix")
routers.register(r'policy/timers', SlaTimerRuleViewSet, basename="policy.timer")
routers.register(r'policy/actions', ActionPolicyViewSet, basename="policy.action")
routers.register(r'policy/priorities', PriorityPolicyViewSet, basename="policy.priority")
routers.register(r'protocols', SlaViewSet, basename="protocol")
routers.register(r'ticket_highlight', TicketHighlightViewSet, basename="ticket_highlight")

urlpatterns = routers.urls

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

from .views import (
    CommentInviteViewSet,
    CommentViewSet,
    EventLogViewSet,
    FieldViewSet,
    FollowersNotifyLogViewSet,
    OperationalDataViewSet,
    StateDraftViewSet,
    TemplateViewSet,
    TicketModelViewSet,
    TicketStatusModelViewSet,
    TicketTestModelViewSet,
)
from .views.ticket_remark import TicketRemarkModelViewSet
from .views_test import TestViewSet


routers = DefaultRouter(trailing_slash=True)

routers.register(r"receipts", TicketModelViewSet, basename="receipts")
routers.register(r"remark", TicketRemarkModelViewSet, basename="remark")
routers.register(r"current_steps", TicketStatusModelViewSet, basename="current_steps")
routers.register(r"fields", FieldViewSet, basename="fields")
routers.register(r"logs", EventLogViewSet, basename="event_logs")
routers.register(r"templates", TemplateViewSet, basename="templates")
routers.register(r"comments", CommentViewSet, basename="comments")
routers.register(r"invite", CommentInviteViewSet, basename="invite")
routers.register(r"draft", StateDraftViewSet, basename="draft")
routers.register(
    r"followers_logs", FollowersNotifyLogViewSet, basename="followers_logs"
)
routers.register(r"operational", OperationalDataViewSet, basename="operational")
routers.register(r"test", TestViewSet, basename="test")
routers.register(r"ticket_tests", TicketTestModelViewSet, basename="ticket_test")

urlpatterns = routers.urls

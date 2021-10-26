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

from blueapps.account.models import User
from django.core.cache import cache
from django.db.models import Count

from itsm.component.constants import TIME_DELTA
from itsm.component.utils.dimensions import fill_time_dimension
from itsm.ticket.models import Ticket, TicketEventLog


def user_count(last_week=None, this_week=None, project_key=None):
    if project_key:
        tickets = Ticket.objects.filter(project_key=project_key)
        event_log = TicketEventLog.objects.filter(
            ticket__id__in=set(tickets.values_list("id", flat=True))
        )
        if last_week:
            event_log = event_log.filter(operate_at__range=last_week)
    
        if this_week:
            event_log = event_log.filter(operate_at__range=this_week)
    
        users_count = len(set(event_log.values_list("operator", flat=True)))
        return users_count

    if not (last_week or this_week):
        return User.objects.count()
    if last_week:
        return (
            cache.get("last_week_user_count")
            or User.objects.filter(last_login__range=last_week).count()
        )
    return User.objects.filter(last_login__range=this_week).count()


def get_user_statistics(time_delta, data):
    data_str = TIME_DELTA[time_delta].format(field_name="date_joined")
    info = (
        User.objects.filter(date_joined__range=(data["create_at__gte"], data["create_at__lte"]))
        .extra(select={"date_str": data_str})
        .values("date_str")
        .annotate(count=Count("id"))
        .order_by("date_str")
    )
    dates_range = fill_time_dimension(data["create_at__gte"], data["create_at__lte"], info, time_delta)
    return dates_range

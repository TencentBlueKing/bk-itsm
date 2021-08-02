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

import traceback

from django.apps import AppConfig
from django.db.models.signals import post_migrate


__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."


def app_ready_handler(sender, **kwargs):
    from itsm.sla.models import PriorityMatrix

    print('PriorityMatrix.init_matrix')
    try:
        PriorityMatrix.objects.init_matrix()
    except BaseException:
        print(traceback.format_exc())

    print('Sla.init_sla')

    from itsm.sla.models import Sla, Schedule, SlaTimerRule, SlaTicketHighlight

    try:
        Sla.init_sla(Schedule.init_schedule())
    except BaseException:
        print(traceback.format_exc())

    print('Sla.init_sla_timer_rule')

    try:
        SlaTimerRule.init_sla_timer_rule()
    except BaseException:
        print(traceback.format_exc())

    print('Sla.init_ticket_hightlight')
    try:
        SlaTicketHighlight.init_sla_ticket_hightlight()
    except BaseException:
        print(traceback.format_exc())        


class SlaConfig(AppConfig):
    name = 'itsm.sla'

    def ready(self):
        post_migrate.connect(app_ready_handler, sender=self)

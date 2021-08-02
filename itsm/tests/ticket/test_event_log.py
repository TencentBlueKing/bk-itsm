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

import json

from django.test import TestCase, override_settings

from itsm.service.models import CatalogService
from itsm.tests.ticket.params import CREATE_TICKET_PARAMS
from itsm.ticket.models import TicketEventLog


class TicketEventLogTestCase(TestCase):

    def setUp(self) -> None:
        CatalogService.objects.create(service_id=1, is_deleted=False, catalog_id=2, creator="admin")
        TicketEventLog.objects.all().delete()

    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_get_index_ticket_event_log(self):
        url = "/api/ticket/receipts/"
        resp = self.client.post(path=url, data=json.dumps(CREATE_TICKET_PARAMS),
                                content_type="application/json")

        sn = resp.data["data"]["sn"]

        url = "/api/ticket/logs/get_index_ticket_event_log/"
        resp = self.client.get(url)

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")
        self.assertEqual(resp.data["message"], "success")
        self.assertEqual(resp.data["data"][0]["sn"], sn)

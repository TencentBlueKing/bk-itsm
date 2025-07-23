# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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
import mock
from django.test import TestCase, override_settings

from itsm.project.models import CostomTab


class CostomTabViewTest(TestCase):
    def setUp(self) -> None:
        CostomTab.objects.all().delete()

    def tearDown(self) -> None:
        CostomTab.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.utils.client_backend_query.update_user_departments")
    def test_get_filter_tickets(self, update_user_departments):
        update_user_departments.return_value = [
            {"id": "1", "name": "总公司", "family": []}
        ]
        url = "/api/ticket/receipts/get_filter_tickets/?page_size=10&page=1&ordering=-create_at"
        data = {"project_key": "0", "tab_conditions": {}, "extra_conditions": {}}
        resp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], True)
        self.assertIsInstance(resp.data["data"]["items"], list)

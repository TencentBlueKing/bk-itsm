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

import mock
from django.test import TestCase, override_settings

from itsm.project.models import CostomTab


class CostomTabViewTest(TestCase):
    def setUp(self) -> None:
        CostomTab.objects.all().delete()

    def tearDown(self) -> None:
        CostomTab.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_create_project(self):
        # 1.创建默认项目下的tab
        create_url = "/api/project/tabs/"
        data_1 = {
            "name": "test_1",
            "desc": "description_1",
            "project_key": "0",
            "conditions": {},
        }
        resp_1 = self.client.post(
            path=create_url, data=data_1, content_type="application/json"
        )
        self.assertEqual(resp_1.status_code, 201)
        self.assertEqual(resp_1.data["result"], True)
        self.assertEqual(resp_1.data["data"]["order"], 1)

        data_2 = {
            "name": "test_2",
            "desc": "description_2",
            "project_key": "0",
            "conditions": {},
        }
        resp_2 = self.client.post(
            path=create_url, data=data_2, content_type="application/json"
        )
        self.assertEqual(resp_2.status_code, 201)
        self.assertEqual(resp_2.data["result"], True)
        self.assertEqual(resp_2.data["data"]["order"], 2)

        data_3 = {
            "name": "test_3",
            "desc": "description_3",
            "project_key": "0",
            "conditions": {},
        }
        resp_3 = self.client.post(
            path=create_url, data=data_3, content_type="application/json"
        )
        self.assertEqual(resp_3.status_code, 201)
        self.assertEqual(resp_3.data["result"], True)
        self.assertEqual(resp_3.data["data"]["order"], 3)

        # 2.创建非默认项目下的tab
        data_other = {
            "name": "test_other",
            "desc": "description_other",
            "project_key": "123",
            "conditions": {},
        }
        resp_other = self.client.post(
            path=create_url, data=data_other, content_type="application/json"
        )
        self.assertEqual(resp_other.status_code, 201)
        self.assertEqual(resp_other.data["result"], True)
        self.assertEqual(resp_other.data["data"]["order"], 1)

        # 3.查询tab
        data_list = {"project_key": "0"}
        resp_list = self.client.get(
            path=create_url, data=data_list, content_type="application/json"
        )
        self.assertEqual(resp_list.status_code, 200)
        self.assertEqual(resp_list.data["result"], True)
        self.assertIsInstance(resp_list.data["data"], list)

        # 4.把第3个tab移到第2的位置
        tab_id_3 = resp_list.data["data"][2].get("id")
        move_url = "/api/project/tabs/{}/move/".format(tab_id_3)
        move_data = {"new_order": 2}
        resp_move = self.client.post(
            path=move_url, data=move_data, content_type="application/json"
        )
        print(json.loads(resp_move.content.decode("utf-8")))
        self.assertEqual(resp_move.status_code, 200)
        self.assertEqual(resp_move.data["result"], True)

        resp_list = self.client.get(
            path=create_url, data=data_list, content_type="application/json"
        )
        self.assertEqual(resp_list.data["data"][1].get("id"), tab_id_3)

        # 5.把第2个tab移到第3的位置
        tab_id_2 = resp_list.data["data"][1].get("id")
        move_url = "/api/project/tabs/{}/move/".format(tab_id_2)
        move_data = {"new_order": 3}
        resp_move = self.client.post(
            path=move_url, data=move_data, content_type="application/json"
        )
        print(json.loads(resp_move.content.decode("utf-8")))
        self.assertEqual(resp_move.status_code, 200)
        self.assertEqual(resp_move.data["result"], True)

        resp_list = self.client.get(
            path=create_url, data=data_list, content_type="application/json"
        )
        self.assertEqual(resp_list.data["data"][2].get("id"), tab_id_2)

        # 6.删除第2个，第3个tab自动变为第2
        tab_id_2 = resp_list.data["data"][1].get("id")
        delete_url = "/api/project/tabs/{}/".format(tab_id_2)
        resp_move = self.client.delete(
            path=delete_url, data=None, content_type="application/json"
        )
        self.assertEqual(resp_move.status_code, 200)
        self.assertEqual(resp_move.data["result"], True)

        resp_list = self.client.get(
            path=create_url, data=data_list, content_type="application/json"
        )
        self.assertEqual(resp_list.data["data"][-1].get("order"), 2)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.utils.client_backend_query.update_user_departments")
    def test_get_filter_tickets(self, update_user_departments):
        update_user_departments.return_value = [{'id': '1', 'name': '总公司', 'family': []}]
        url = "/api/ticket/receipts/get_filter_tickets/?page_size=10&page=1&ordering=-create_at"
        data = {"project_key": "0", "tab_conditions": {}, "extra_conditions": {}}
        resp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], True)
        self.assertIsInstance(resp.data["data"]["items"], list)

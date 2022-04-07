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

from itsm.service.models import CatalogService
from itsm.ticket.models import Ticket


class TicketViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def setUp(self):
        CatalogService.objects.create(
            service_id=1, is_deleted=False, catalog_id=2, creator="admin"
        )
        data = {
            "catalog_id": 3,
            "service_id": 1,
            "service_type": "request",
            "fields": [
                {
                    "type": "STRING",
                    "id": 1,
                    "key": "title",
                    "value": "test_ticket",
                    "choice": [],
                },
                {
                    "type": "STRING",
                    "id": 5,
                    "key": "apply_content",
                    "value": "测试内容",
                },
                {
                    "type": "STRING",
                    "key": "ZHIDINGSHENPIREN",
                    "value": "test",
                },
                {
                    "type": "STRING",
                    "key": "apply_reason",
                    "value": "test",
                },
            ],
            "creator": "admin",
            "attention": True,
        }
        url = "/api/ticket/receipts/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(rsp.data["message"], "success")

    def tearDown(self):
        Ticket.objects.all().delete()
        CatalogService.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_total_count(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/total_count/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_get_ticket_output(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/get_ticket_output/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_first_state_fields(self):
        url = "/api/ticket/receipts/get_first_state_fields/?service_id=1"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_api_field_choices_without_data(self):
        url = "/api/ticket/receipts/api_field_choices/"
        rsp = self.client.post(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "对应的api配置不存在，请查询")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.esb.backend_component.BaseClient.request")
    def test_api_field_choices(self, request):
        request.return_value = {
            "result": True,
            "code": 0,
            "data": {
                "count": 1,
                "info": [
                    {
                        "bk_biz_developer": "",
                        "bk_biz_id": 2,
                        "bk_biz_maintainer": "admin",
                        "bk_biz_name": "\xe8\x93\x9d\xe9\xb2\xb8",
                        "bk_biz_productor": "",
                        "bk_biz_tester": "",
                        "bk_supplier_account": "0",
                        "create_time": "2020-09-24T23:08:55.458+08:00",
                        "default": 0,
                        "language": "1",
                        "last_time": "2021-07-18T11:45:13.27+08:00",
                        "life_cycle": "2",
                        "operator": "",
                        "time_zone": "Asia/Shanghai",
                    }
                ],
            },
            "message": "success",
            "permission": None,
            "request_id": "c760e0b8284b4b788e2664d35c2edece",
        }

        data = {
            "api_instance_id": 1,
            "kv_relation": {"name": "bk_biz_name", "key": "bk_biz_id"},
            "fields": {"name": "test", "key": "001"},
        }
        url = "/api/ticket/receipts/api_field_choices/"
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.utils.client_backend_query.update_user_departments")
    def test_send_sms(self, update_user_departments):
        update_user_departments.return_value = [
            {"id": "1", "name": "总公司", "family": []}
        ]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        data = {"receiver": "admin"}
        url = "/api/ticket/receipts/{}/send_sms/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        print(json.loads(rsp.content.decode("utf-8")))
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.utils.client_backend_query.update_user_departments")
    def test_send_email(self, update_user_departments):
        update_user_departments.return_value = [
            {"id": "1", "name": "总公司", "family": []}
        ]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        data = {"receiver": "admin"}
        url = "/api/ticket/receipts/{}/send_email/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_export_excel(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/export_excel/?export_fields=sn"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_export_group_by_service(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/export_group_by_service/?export_fields=sn&service_id__in=1&service_fields=eyI2IjpbInRpdGxlIl19"  # noqa
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    @mock.patch("itsm.ticket.serializers.ticket.transform_single_username")
    @mock.patch("itsm.component.utils.client_backend_query.get_bk_users")
    def test_print_ticket(
        self, get_user_departments, transform_single_username, get_bk_users
    ):
        get_user_departments.return_value = ["1"]
        get_bk_users.return_value = ["1"]
        transform_single_username.return_value = "admin(管理员)"
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/print_ticket/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_global_choices(self):
        url = "/api/ticket/receipts/get_global_choices/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)
        self.assertIsInstance(rsp.data["data"]["export_fields"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_trigger_actions(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/trigger_actions/?operate_type=all".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_withdraw(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/withdraw/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.post(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_fields(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/fields/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_all_fields(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/all_fields/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_derive_tickets(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/derive_tickets/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_master_or_slave(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/master_or_slave/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_table_fields(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp_base = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/table_fields/".format(
            rsp_base.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_sla_task(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/sla_task/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_ticket_base_info(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/{}/ticket_base_info/".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_my_approval_ticket(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/my_approval_ticket/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    @mock.patch("itsm.component.utils.client_backend_query.get_bk_users")
    def test_tickets_processors(self, get_user_departments, get_bk_users):
        get_user_departments.return_value = ["1"]
        get_bk_users.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/tickets_processors/?ids={}".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_tickets_can_operate(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/ticket/receipts/tickets_can_operate/?ids={}".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_tree_view(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/ticket/remark/tree_view/?ticket_id={}&show_type=1".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_remark(self, get_user_departments):
        get_user_departments.return_value = ["1"]
        url = "/api/ticket/receipts/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/ticket/remark/?ticket_id={}".format(
            rsp.data["data"]["items"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)


class OperationalDataViewTest(TestCase):
    data_filter = "create_at__gte=2021-01-01&create_at__lte=2031-01-01"
    month_filter = "create_at__gte=2021-01&create_at__lte=2031-01"

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def setUp(self):
        CatalogService.objects.create(
            service_id=1, is_deleted=False, catalog_id=2, creator="admin"
        )
        data = {
            "catalog_id": 3,
            "service_id": 1,
            "service_type": "request",
            "fields": [
                {
                    "type": "STRING",
                    "id": 1,
                    "key": "title",
                    "value": "test_ticket",
                    "choice": [],
                },
                {
                    "type": "STRING",
                    "id": 5,
                    "key": "apply_content",
                    "value": "测试内容",
                },
                {
                    "type": "STRING",
                    "key": "ZHIDINGSHENPIREN",
                    "value": "test",
                },
                {
                    "type": "STRING",
                    "key": "apply_reason",
                    "value": "test",
                },
            ],
            "creator": "admin",
            "attention": True,
        }
        url = "/api/ticket/receipts/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(rsp.data["message"], "success")

    def tearDown(self):
        Ticket.objects.all().delete()
        CatalogService.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_overview_count(self):
        url = "/api/ticket/operational/overview_count/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_compared_same_week(self):
        url = "/api/ticket/operational/compared_same_week/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_service_statistics(self):
        url = "/api/ticket/operational/service_statistics/?{}&page=1".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)
        self.assertIsInstance(rsp.data["data"]["items"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.utils.client_backend_query.get_all_apps")
    def test_biz_statistics(self, all_apps):
        all_apps.return_value = [
            {
                "bk_biz_developer": "",
                "bk_biz_id": 2,
                "bk_biz_maintainer": "admin",
                "bk_biz_name": "test",
                "bk_biz_productor": "",
                "bk_biz_tester": "",
                "bk_supplier_account": "0",
                "create_time": "2020-09-24T23:08:55.458+08:00",
                "default": 0,
                "language": "1",
                "last_time": "2021-07-18T11:45:13.27+08:00",
                "life_cycle": "2",
                "operator": "",
                "time_zone": "Asia/Shanghai",
            }
        ]
        url = "/api/ticket/operational/biz_statistics/?{}&page=1".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)
        self.assertIsInstance(rsp.data["data"]["items"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_category_statistics(self):
        url = "/api/ticket/operational/category_statistics/?{}".format(self.data_filter)
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_status_statistics(self):
        url = "/api/ticket/operational/status_statistics/?{}".format(self.data_filter)
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_service_count_statistics(self):
        url = "/api/ticket/operational/service_count_statistics/?{}&timedelta=days&resource_type=ticket".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

        url = "/api/ticket/operational/service_count_statistics/?{}&timedelta=days&resource_type=biz".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_top_creator_statistics(self):
        url = "/api/ticket/operational/top_creator_statistics/?{}".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_distribute_statistics(self):
        url = "/api/ticket/operational/distribute_statistics/?{}".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_resource_count_statistics(self):
        url = "/api/ticket/operational/resource_count_statistics/?{}&timedelta=days&resource_type=creator".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

        url = "/api/ticket/operational/resource_count_statistics/?{}&timedelta=days&resource_type=user".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

        url = "/api/ticket/operational/resource_count_statistics/?{}&timedelta=days&resource_type=service".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.utils.client_backend_query.update_user_departments")
    def test_sync_organization(self, update_user_departments):
        update_user_departments.return_value = [
            {"id": "1", "name": "总公司", "family": []}
        ]
        url = "/api/ticket/operational/sync_organization/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_tickets(self):
        tickets_filter = "{}&title=test&creator=admin&sn=123456&is_draft=1&service_type=request".format(
            self.data_filter
        )
        url = "/api/ticket/operational/get_tickets/?{}".format(tickets_filter)
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_comments(self):
        url = "/api/ticket/operational/comments/?{}".format(self.data_filter)
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ticket_category(self):
        url = "/api/ticket/operational/ticket_category/?{}".format(self.data_filter)
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_month_ticket_category(self):
        url = "/api/ticket/operational/month_ticket_category/?{}&service_type=request".format(
            self.month_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ticket_status(self):
        url = "/api/ticket/operational/ticket_status/?{}&service_type=request".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_whole_close_ratio(self):
        url = "/api/ticket/operational/whole_close_ratio/?{}".format(self.data_filter)
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_month_close_ratio(self):
        url = "/api/ticket/operational/month_close_ratio/?{}".format(self.month_filter)
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.tasks.adapter_api")
    def test_ticket_processor_rank(self, adapter_api):
        adapter_api.get_all_users.return_value = [
            {
                "id": "admin",
                "name": "admin(admin)",
                "bk_username": "admin",
                "chname": "admin",
            }
        ]
        url = "/api/ticket/operational/ticket_processor_rank/?{}".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ticket_score(self):
        url = "/api/ticket/operational/ticket_score/?{}&service_type=request".format(
            self.month_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ticket_time(self):
        url = "/api/ticket/operational/ticket_time/?{}&service_type=request".format(
            self.month_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_new_tickets(self):
        url = "/api/ticket/operational/new_tickets/?{}&service_type=request".format(
            self.data_filter
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

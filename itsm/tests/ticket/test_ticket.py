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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

import json
import mock
from blueapps.core.celery.celery import app

from django.test import TestCase, override_settings
from django.core.cache import cache

from itsm.service.models import CatalogService, Service
from itsm.ticket.models import Ticket, Status, AttentionUsers
from itsm.component.constants import APPROVAL_STATE


class TicketTest(TestCase):
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        Ticket.objects.all().delete()
        AttentionUsers.objects.all().delete()

        CatalogService.objects.create(
            service_id=1, is_deleted=False, catalog_id=2, creator="admin"
        )

    def tearDown(self):
        Ticket.objects.all().delete()
        AttentionUsers.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_create_ticket(self):
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

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_list(self, patch_get_user_departments):
        patch_get_user_departments.return_value = {}
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
        ticket_id = rsp.data["data"]["id"]
        url = "/api/ticket/receipts/"
        list_rsp = self.client.get(url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual(ticket_id, list_rsp.data["data"]["items"][0]["id"])
        self.assertEqual(["admin"], list_rsp.data["data"]["items"][0]["followers"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideTestMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_list_follower(self, patch_get_user_departments):
        patch_get_user_departments.return_value = {}
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
        self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )

        data_test = {
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
            "creator": "test",
            "attention": True,
        }
        rsp = self.client.post(
            path=url, data=json.dumps(data_test), content_type="application/json"
        )
        ticket_id = rsp.data["data"]["id"]
        list_rsp = self.client.get(url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual(2, len(list_rsp.data["data"]["items"]))
        self.assertEqual(["test"], list_rsp.data["data"]["items"][0]["followers"])
        self.assertEqual(ticket_id, list_rsp.data["data"]["items"][0]["id"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    def test_retrieve(self, patch_misc_get_bk_users, path_get_bk_users):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
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

        ticket_id = rsp.data["data"]["id"]
        get_url = "/api/ticket/receipts/{}/".format(ticket_id)
        list_rsp = self.client.get(get_url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual(["admin"], list_rsp.data["data"]["followers"])
        self.assertEqual(ticket_id, list_rsp.data["data"]["id"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    def test_add_follower(self, patch_misc_get_bk_users, path_get_bk_users):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
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
            "creator": "test",
            "attention": True,
        }
        url = "/api/ticket/receipts/"

        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        ticket_id = rsp.data["data"]["id"]

        add_url = "/api/ticket/receipts/{}/add_follower/".format(ticket_id)
        add_rsp = self.client.post(
            path=add_url,
            data=json.dumps({"attention": True}),
            content_type="application/json",
        )
        self.assertEqual(add_rsp.data["code"], "OK")
        self.assertEqual(add_rsp.data["message"], "success")
        get_url = "/api/ticket/receipts/{}/".format(ticket_id)
        list_rsp = self.client.get(get_url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual(["test", "admin"], list_rsp.data["data"]["followers"])
        self.assertEqual(ticket_id, list_rsp.data["data"]["id"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    def test_delete_follower(self, patch_misc_get_bk_users, path_get_bk_users):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
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

        ticket_id = rsp.data["data"]["id"]

        add_url = "/api/ticket/receipts/{}/add_follower/".format(ticket_id)
        add_rsp = self.client.post(
            path=add_url,
            data=json.dumps({"attention": False}),
            content_type="application/json",
        )
        self.assertEqual(add_rsp.data["code"], "OK")
        self.assertEqual(add_rsp.data["message"], "success")
        get_url = "/api/ticket/receipts/{}/".format(ticket_id)
        list_rsp = self.client.get(get_url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual([], list_rsp.data["data"]["followers"])
        self.assertEqual(ticket_id, list_rsp.data["data"]["id"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideTestMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    def test_operate(self, patch_misc_get_bk_users, path_get_bk_users):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
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

        ticket_id = rsp.data["data"]["id"]
        AttentionUsers.objects.create(ticket_id=ticket_id, follower="test")

        get_url = "/api/ticket/receipts/{}/".format(ticket_id)
        list_rsp = self.client.get(get_url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual(["admin", "test"], list_rsp.data["data"]["followers"])
        self.assertEqual(ticket_id, list_rsp.data["data"]["id"])
        self.assertEqual(True, list_rsp.data["data"]["can_view"])
        self.assertEqual(True, list_rsp.data["data"]["can_operate"])

    @mock.patch.object(Status, "approval_result")
    @mock.patch.object(Status, "get_processor_in_sign_state")
    @mock.patch.object(Ticket, "activity_callback")
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_approval_add_queue_success(
        self, mock_callback, mock_user, mock_result
    ):
        mock_callback.return_value = type("MyResult", (object,), {"result": True})
        mock_user.return_value = "admin"
        mock_result.return_value = [
            {"id": 1, "key": "123", "value": "true"},
            {"id": 2, "key": "234", "value": "通过"},
        ]
        ticket = Ticket.objects.create(
            sn="123", title="test", service_id="456", service_type="change"
        )
        status = Status.objects.create(
            ticket_id=ticket.id, state_id="111", status="RUNNING", type=APPROVAL_STATE
        )
        ticket.node_status.add(status)
        data = {
            "result": "true",
            "opinion": "xxxxx",
            "approval_list": [{"ticket_id": ticket.id}],
        }
        url = "/api/ticket/receipts/batch_approval/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(
            cache.get("approval_status_{}_{}_{}".format("admin", ticket.id, "111")),
            "RUNNING",
        )

    @mock.patch.object(Status, "approval_result")
    @mock.patch.object(Status, "get_processor_in_sign_state")
    @mock.patch.object(Ticket, "activity_callback")
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_approval_add_queue_error(
        self, mock_callback, mock_user, mock_result
    ):
        mock_callback.return_value = type(
            "MyResult", (object,), {"result": False, "message": "error_test"}
        )
        mock_user.return_value = "admin"
        mock_result.return_value = [
            {"id": 1, "key": "123", "value": "true"},
            {"id": 2, "key": "234", "value": "通过"},
        ]
        ticket = Ticket.objects.create(
            sn="123", title="test", service_id="456", service_type="change"
        )
        status = Status.objects.create(
            ticket_id=ticket.id, state_id="111", status="RUNNING", type=APPROVAL_STATE
        )
        ticket.node_status.add(status)
        data = {
            "result": "true",
            "opinion": "xxxxx",
            "approval_list": [{"ticket_id": ticket.id}],
        }
        url = "/api/ticket/receipts/batch_approval/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(
            cache.get("approval_status_{}_{}_{}".format("admin", ticket.id, "111")),
            None,
        )

    @override_settings(
        MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",), ENVIRONMENT="dev"
    )
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    @mock.patch("itsm.auth_iam.utils.IamRequest")
    def test_exception_distribute(
        self, patch_misc_get_bk_users, path_get_bk_users, patch_iam_request
    ):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
        patch_iam_request.resource_multi_actions_allowed.return_value = {
            "ticket_management",
            True,
        }

        service = Service.objects.get(name="帐号开通申请")
        print("service name === {}".format(service.name))
        service.owners = ",admin,"
        service.save()

        data = {
            "catalog_id": 3,
            "service_id": service.id,
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
                    "value": "111",
                },
                {
                    "type": "STRING",
                    "key": "ZHIDINGSHENPIREN",
                    "value": "111",
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
        self.assertEqual(rsp.status_code, 201)
        self.assertEqual(rsp.data["result"], True)
        ticket_id = rsp.data["data"]["id"]
        ticket = Ticket.objects.get(id=ticket_id)
        current_steps = ticket.current_steps
        print("current_steps === {}".format(current_steps))
        if not current_steps:
            return

        state_id = current_steps[0]["state_id"]

        data = {
            "state_id": state_id,
            "action_type": "EXCEPTION_DISTRIBUTE",
            "processors": "admin1",
            "processors_type": "PERSON",
        }

        url = "/api/ticket/receipts/{}/exception_distribute/".format(ticket_id)
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], True)
        ticket.refresh_from_db()

        self.assertEqual(ticket.current_steps[0]["processors"], "admin1")

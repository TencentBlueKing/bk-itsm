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
__copyright__ = "Copyright © 2012-Now Tencent BlueKing. All Rights Reserved."

import json
import time
from collections import OrderedDict

import mock
from blueapps.core.celery.celery import app
from django.conf import settings
from django.test import TestCase, override_settings
from common.cipher import AESVerification
from common.redis import Cache
from itsm.tests.openapi.params import CREATE_TICKET_DATA
from itsm.ticket.models import Ticket, AttentionUsers, TicketComment
from itsm.service.models import Service, CatalogService
from itsm.workflow.models import WorkflowVersion
from itsm.role.models import UserRole


class TicketOpenTest(TestCase):
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
        WorkflowVersion.objects.all().delete()
        UserRole.objects.filter(role_type="IAM").delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_approval_result(self, patch_jwt_client):
        data = {
            "fast_approval": True,
            "fields": [
                {"key": "title", "value": "测试内置审批"},
                {"key": "APPROVER", "value": "admin,admin3,admin2"},
                {"key": "APPROVAL_CONTENT", "value": "这是一个审批单"},
            ],
            "creator": "admin",
        }
        patch_jwt_client.is_valid.return_value = True
        url = "/openapi/ticket/create_ticket/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        sn = rsp.data["data"]["sn"]
        query_url = "/openapi/ticket/ticket_approval_result/"
        query_data = {"sn": [sn]}
        result = self.client.post(
            path=query_url, data=json.dumps(query_data), content_type="application/json"
        )
        self.assertEqual(result.data["code"], 0)
        self.assertEqual(result.data["message"], "success")
        self.assertEqual(False, result.data["data"][0]["approve_result"])
        self.assertEqual(sn, result.data["data"][0]["sn"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_verify(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True
        message = AESVerification.gen_signature(
            settings.APP_CODE + "_" + settings.SECRET_KEY
        )
        data = {
            "token": str(message, encoding="utf-8"),
        }
        url = "/openapi/ticket/token/verify/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        result = rsp.data["data"]["is_passed"]
        self.assertEqual(True, result)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_get_callback_failed_ticket(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True
        Cache().hset("callback_error_ticket", "12345", int(time.time()))
        url = "/openapi/ticket/callback_failed_ticket/"
        rsp = self.client.get(path=url)
        sn = rsp.data["data"]
        self.assertEqual(["12345"], sn)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_get_service_roles(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True
        role = UserRole.objects.create(
            role_type="IAM",
            name="分级管理员",
            members="",
            role_key="rating_manager",
            access="",
        )

        states = {
            "92580": {
                "id": 92580,
                "processors_type": "GENERAL",
                "processors": "8,7",
                "name": "节点1",
                "type": "START",
                "is_multi": True,
            },
            "92581": {
                "id": 92581,
                "processors_type": "IAM",
                "processors": str(role.id),
                "name": "节点2",
                "type": "NORMAL",
                "is_multi": False,
            },
            "92582": {
                "id": 92582,
                "processors_type": "PERSON",
                "processors": "admin",
                "name": "节点3",
                "type": "NORMAL",
                "is_multi": False,
            },
            "92583": {
                "id": 92583,
                "processors_type": "PERSON",
                "processors": "admin",
                "name": "节点4",
                "type": "END",
                "is_multi": False,
            },
        }
        transitions = {
            "92584": {
                "id": 92583,
                "from_state": 92580,
                "to_state": 92581,
            },
            "92585": {
                "id": 92584,
                "from_state": 92581,
                "to_state": 92582,
            },
            "92586": {
                "id": 92585,
                "from_state": 92582,
                "to_state": 92583,
            },
        }
        workflow = WorkflowVersion.objects.create(
            name="test_flow", workflow_id=1, states=states, transitions=transitions
        )
        service = Service.objects.create(key="123", name="test", workflow=workflow)

        # test1: 测试url参数只有service.id时的执行情况
        url = "/openapi/service/get_service_roles/?service_id={}".format(service.id)
        rsp = self.client.get(path=url)
        roles = rsp.data["data"]
        self.assertEqual(
            roles,
            [
                {
                    "id": 92582,
                    "name": "节点3",
                    "processors_type": "PERSON",
                    "processors": "admin",
                    "sign_type": "or",
                }
            ],
        )

        # test2: 测试url参数为service.id和all，且all=1(逻辑真)时的执行情况
        url_with_all = (
            "/openapi/service/get_service_roles/?service_id={}&all={}".format(
                service.id, 1
            )
        )
        rsp_with_all = self.client.get(path=url_with_all)
        roles_with_all = rsp_with_all.data["data"]
        self.assertEqual(
            roles_with_all,
            [
                {
                    "id": 92581,
                    "name": "节点2",
                    "processors": "rating_manager",
                    "processors_type": "IAM",
                    "sign_type": "or",
                },
                {
                    "id": 92582,
                    "name": "节点3",
                    "processors_type": "PERSON",
                    "processors": "admin",
                    "sign_type": "or",
                },
            ],
        )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_create_ticket(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True
        url = "/openapi/ticket/create_ticket/"

        resp = self.client.post(
            url, json.dumps(CREATE_TICKET_DATA), content_type="application/json"
        )

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)
        self.assertEqual(resp.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_get_tickets(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True
        url = "/openapi/ticket/create_ticket/"

        resp = self.client.post(
            url, json.dumps(CREATE_TICKET_DATA), content_type="application/json"
        )

        sn = resp.data["data"]["sn"]

        url = "/openapi/ticket/get_tickets/"

        resp = self.client.post(
            url, json.dumps({"sns": [sn]}), content_type="application/json"
        )

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)

        self.assertIsInstance(resp.data["data"], OrderedDict)

    def create_ticket(self):
        url = "/openapi/ticket/create_ticket/"

        resp = self.client.post(
            url, json.dumps(CREATE_TICKET_DATA), content_type="application/json"
        )

        return resp.data["data"]["sn"]

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_get_ticket_info(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True
        sn = self.create_ticket()

        url = "/openapi/ticket/get_ticket_info/"

        resp = self.client.get(url, {"sn": sn})

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)
        self.assertEqual(resp.data["data"]["sn"], sn)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_get_ticket_logs(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True
        sn = self.create_ticket()

        url = "/openapi/ticket/get_ticket_logs/"

        resp = self.client.get(url, {"sn": sn})

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)
        self.assertEqual(resp.data["data"]["sn"], sn)
        self.assertEqual(resp.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_operate_ticket(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True
        sn = self.create_ticket()

        url = "/openapi/ticket/operate_ticket/"

        resp = self.client.post(
            url,
            json.dumps(
                {
                    "sn": sn,
                    "operator": "admin",
                    "action_type": "WITHDRAW",
                    "action_message": "撤销单据",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)

        url = "/openapi/ticket/get_ticket_status/"

        resp = self.client.get(url, {"sn": sn})

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)
        self.assertEqual(resp.data["data"]["current_status"], "REVOKED")

    @override_settings(
        MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",), ENVIRONMENT="dev"
    )
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_comment(
        self, patch_jwt_client, patch_misc_get_bk_users, path_get_bk_users
    ):
        patch_jwt_client.is_valid.return_value = True
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}

        sn = self.create_ticket()

        sn_test = "11111"

        data = {
            "sn": sn_test,
            "stars": 4,
            "comments": "123",
            "source": "API",
            "operator": "admin",
        }
        url = "/openapi/ticket/comment/"

        resp = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["message"], "参数验证失败: sn=11111对应的单据不存在!")

        data["sn"] = sn
        resp = self.client.post(url, json.dumps(data), content_type="application/json")

        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["message"], "参数验证失败: 单据未结束，不允许评价!")

        ticket = Ticket.objects.get(sn=sn)
        ticket.current_status = "FINISHED"
        ticket.save()

        url = "/openapi/ticket/comment/"

        resp = self.client.post(url, json.dumps(data), content_type="application/json")

        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["message"], "参数验证失败: 单据评价记录未存在，无法评价!")

        TicketComment.objects.get_or_create(ticket_id=ticket.id, creator=ticket.creator)

        url = "/openapi/ticket/comment/"

        resp = self.client.post(url, json.dumps(data), content_type="application/json")

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["message"], "success")

        url = "/openapi/ticket/comment/"

        resp = self.client.post(url, json.dumps(data), content_type="application/json")

        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["message"], "参数验证失败: 该单据已经被评论，请勿重复评论")

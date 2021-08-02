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

from blueapps.core.celery.celery import app
from django.conf import settings
from django.test import TestCase, override_settings
from common.cipher import AESVerification
from common.redis import Cache
from itsm.tests.openapi.params import CREATE_TICKET_DATA
from itsm.ticket.models import Ticket, AttentionUsers
from itsm.service.models import Service, CatalogService
from itsm.workflow.models import WorkflowVersion
from itsm.role.models import UserRole


class TicketOpenTest(TestCase):
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        Ticket.objects.all().delete()
        AttentionUsers.objects.all().delete()

        CatalogService.objects.create(service_id=1, is_deleted=False, catalog_id=2, creator="admin")

    def tearDown(self):
        Ticket.objects.all().delete()
        AttentionUsers.objects.all().delete()
        WorkflowVersion.objects.all().delete()
        UserRole.objects.filter(role_type="IAM").delete()

    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_approval_result(self):
        data = {
            "fast_approval": True,
            "fields": [
                {"key": "title", "value": "测试内置审批"},
                {"key": "APPROVER", "value": "admin,admin3,admin2"},
                {"key": "APPROVAL_CONTENT", "value": "这是一个审批单"},
            ],
            "creator": "admin",
        }
        url = "/openapi/ticket/create_ticket/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        sn = rsp.data["data"]["sn"]
        query_url = "/openapi/ticket/ticket_approval_result/"
        query_data = {"sn": [sn]}
        result = self.client.post(path=query_url, data=json.dumps(query_data),
                                  content_type="application/json")
        self.assertEqual(result.data["code"], 0)
        self.assertEqual(result.data["message"], "success")
        self.assertEqual(False, result.data["data"][0]["approve_result"])
        self.assertEqual(sn, result.data["data"][0]["sn"])

    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_verify(self):
        message = AESVerification.gen_signature(settings.APP_CODE + "_" + settings.SECRET_KEY)
        data = {
            "token": str(message, encoding="utf-8"),
        }
        url = "/openapi/ticket/token/verify/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        result = rsp.data["data"]["is_passed"]
        self.assertEqual(True, result)

    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_get_callback_failed_ticket(self):
        Cache().hset("callback_error_ticket", "12345", int(time.time()))
        url = "/openapi/ticket/callback_failed_ticket/"
        rsp = self.client.get(path=url)
        sn = rsp.data["data"]
        self.assertEqual(["12345"], sn)

    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_get_service_roles(self):
        role = UserRole.objects.create(role_type="IAM", name="分级管理员", members="",
                                       role_key="rating_manager", access="")

        states = {
            "92580": {"id": 92580, "processors_type": "GENERAL", "processors": "8,7", "name": "节点1",
                      "is_multi": True},
            "92581": {
                "id": 92581,
                "processors_type": "IAM",
                "processors": str(role.id),
                "name": "节点2",
                "is_multi": False,
            },
            "92582": {
                "id": 92582,
                "processors_type": "PERSON",
                "processors": "hoganren1",
                "name": "节点3",
                "is_multi": False,
            },
        }
        workflow = WorkflowVersion.objects.create(name="test_flow", workflow_id=1, states=states)
        service = Service.objects.create(key="123", name="test", workflow=workflow)
        url = "/openapi/service/get_service_roles/?service_id={}".format(service.id)
        rsp = self.client.get(path=url)
        roles = rsp.data["data"]
        self.assertEqual(
            roles,
            [
                {"id": 92580, "name": "节点1", "processors_type": "GENERAL", "processors": "admin",
                 "sign_type": "and"},
                {
                    "id": 92581,
                    "name": "节点2",
                    "processors_type": "IAM",
                    "processors": "rating_manager",
                    "sign_type": "or",
                },
                {"id": 92582, "name": "节点3", "processors_type": "PERSON", "processors": "hoganren1",
                 "sign_type": "or"},
            ],
        )

    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_create_ticket(self):
        url = "/openapi/ticket/create_ticket/"

        resp = self.client.post(url, json.dumps(CREATE_TICKET_DATA),
                                content_type="application/json")

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)
        self.assertEqual(resp.data["message"], "success")

    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_get_tickets(self):
        url = "/openapi/ticket/create_ticket/"

        resp = self.client.post(url, json.dumps(CREATE_TICKET_DATA),
                                content_type="application/json")

        sn = resp.data["data"]["sn"]

        url = "/openapi/ticket/get_tickets/"

        resp = self.client.post(url, json.dumps({
            "sns": [sn]
        }), content_type="application/json")

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)

        self.assertIsInstance(resp.data["data"], OrderedDict)

    def create_ticket(self):
        url = "/openapi/ticket/create_ticket/"

        resp = self.client.post(url, json.dumps(CREATE_TICKET_DATA),
                                content_type="application/json")

        return resp.data["data"]["sn"]

    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_get_ticket_info(self):
        sn = self.create_ticket()

        url = "/openapi/ticket/get_ticket_info/"

        resp = self.client.get(url, {
            "sn": sn
        })

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)
        self.assertEqual(resp.data["data"]["sn"], sn)

    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_get_ticket_logs(self):
        sn = self.create_ticket()
        
        url = "/openapi/ticket/get_ticket_logs/"

        resp = self.client.get(url, {
            "sn": sn
        })
        
        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)
        self.assertEqual(resp.data["data"]["sn"], sn)
        self.assertEqual(resp.data["message"], "success")
        
    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_operate_ticket(self):
    
        sn = self.create_ticket()

        url = "/openapi/ticket/operate_ticket/"
        
        resp = self.client.post(url, json.dumps({
            "sn": sn,
            "operator": "admin",
            "action_type": "WITHDRAW",
            "action_message": "撤销单据"
        }), content_type="application/json")

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)

        url = "/openapi/ticket/get_ticket_status/"
        
        resp = self.client.get(
            url, {
                "sn": sn
            }
        )

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], 0)
        self.assertEqual(resp.data["data"]["current_status"], "REVOKED")

        
        
        
        

        
        
        
        
        

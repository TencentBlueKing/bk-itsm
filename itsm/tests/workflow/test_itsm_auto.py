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
from blueapps.core.celery.celery import app

from itsm.pipeline_plugins.components.collections.itsm_auto import AutoStateService
from itsm.postman.models import RemoteApiInstance
from itsm.service.models import CatalogService
from itsm.ticket.models import Ticket
from pipeline.core.data.base import DataObject


class PipelineTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def setUp(self):
        Ticket.objects.all().delete()
        CatalogService.objects.all().delete()
        self.ticket_id = self.create_ticket()
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    def create_ticket(self):
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
        data = json.loads(rsp.content.decode("utf-8"))
        return data["data"]["id"]

    def tearDown(self):
        Ticket.objects.all().delete()
        CatalogService.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.itsm_auto.RemoteApiInstance")
    @mock.patch("itsm.pipeline_plugins.components.collections.itsm_auto.AutoStateService.build_query_params")
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_auto.Ticket.do_before_enter_state"
    )
    def test_excute(self, patch_remote, build_query_params, do_before_enter_state):
        build_query_params.return_value = True, {}
        do_before_enter_state.return_value = None
        patch_remote.return_value = RemoteApiInstance.objects.get(id=2)
        print("ticket_id:{}".format(self.ticket_id))

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        auto_service = AutoStateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_auto.AutoStateService.get_rsp_content")
    def test_schedule_with_true(self, get_rsp_content):
        get_rsp_content.return_value = (True, {"message": "", "data": ""})
        print("ticket_id:{}".format(self.ticket_id))

        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "service_status": "",
                "poll_time": 1,
                "poll_interval": 0,
                "api_config": {},
                "success_conditions": {},
                "variables": ""
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        auto_service = AutoStateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_auto.AutoStateService.get_rsp_content")
    def test_schedule_with_false(self, get_rsp_content):
        get_rsp_content.return_value = (False, {"message": "", "data": ""})
        print("ticket_id:{}".format(self.ticket_id))

        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "service_status": "",
                "poll_time": 1,
                "poll_interval": 0,
                "api_config": {},
                "success_conditions": {},
                "variables": ""
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        auto_service = AutoStateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, False)
        
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_auto.AutoStateService.get_rsp_content")
    def test_schedule_with_poll_time(self, get_rsp_content):
        get_rsp_content.return_value = (False, {"message": "", "data": ""})
        print("ticket_id:{}".format(self.ticket_id))

        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "service_status": "",
                "poll_time": 10,
                "poll_interval": 0,
                "api_config": {},
                "success_conditions": {},
                "variables": ""
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        auto_service = AutoStateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_auto.jsonschema.validate")
    def test_build_query_params(self, validate):
        validate.return_value = None
        ticket = Ticket.objects.get(id=self.ticket_id)
        query_params = {}
        schema = {
            "type": "number",
            "default": 1
        }

        auto_service = AutoStateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.build_query_params(ticket, query_params, schema)
        self.assertEqual(result, (True, {}))

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_build_query_params_failed(self):
        ticket = Ticket.objects.get(id=self.ticket_id)

        auto_service = AutoStateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.build_query_params(ticket, {}, {})
        self.assertEqual(result, (False, "请求参数转换异常，详细信息： 'type'"))

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_auto.conditions_conversion")
    def test_get_rsp_content(self, conditions_conversion):
        conditions_conversion.return_value = {}
        ticket = Ticket.objects.get(id=self.ticket_id)
        
        auto_service = AutoStateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.get_rsp_content(ticket, 2, {}, {}, {})
        self.assertEqual(result[0], False)


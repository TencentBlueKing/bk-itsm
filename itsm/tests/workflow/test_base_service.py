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

from itsm.pipeline_plugins.components.collections.itsm_base_service import ItsmBaseService
from itsm.pipeline_plugins.components.collections.itsm_create import TicketCreateService
from itsm.pipeline_plugins.components.collections.itsm_migrate import ItsmMigrateService
from itsm.pipeline_plugins.components.collections.itsm_sign import ItsmSignService
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
    def test_excute_base(self):
        print("ticket_id:{}".format(self.ticket_id))

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={
                "ticket_id": self.ticket_id,
                "parent_ticket_id": self.ticket_id
            },
            outputs={
                "is_first_execute": False,
                "is_cloning": True
            }
        )
        auto_service = ItsmBaseService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_update_status_and_fields(self):
        print("ticket_id:{}".format(self.ticket_id))
        current_ticket = Ticket.objects.get(id=self.ticket_id)
        current_status = current_ticket.status(state_id=2)

        auto_service = ItsmBaseService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.update_status_and_fields(current_status, current_ticket, self.ticket_id, 2)
        self.assertEqual(result, None)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_need_schedule_base(self):
        print("ticket_id:{}".format(self.ticket_id))
        pipeline_data = DataObject(
            inputs={"_loop": 0}, outputs={"_loop": 0, "is_cloning": True}
        )

        auto_service = ItsmBaseService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.need_schedule(pipeline_data)
        self.assertEqual(result, False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_excute_create_true(self):
        print("ticket_id:{}".format(self.ticket_id))

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={
                "ticket_id": self.ticket_id,
                "parent_ticket_id": self.ticket_id
            },
            outputs={
                "is_first_execute": True,
                "is_cloning": True
            }
        )
        auto_service = TicketCreateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_excute_create_false(self):
        print("ticket_id:{}".format(self.ticket_id))

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={
                "ticket_id": self.ticket_id,
                "parent_ticket_id": self.ticket_id
            },
            outputs={
                "is_first_execute": True,
                "is_cloning": False
            }
        )
        auto_service = TicketCreateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_schedule_create(self):
        print("ticket_id:{}".format(self.ticket_id))

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={
                "ticket_id": self.ticket_id,
                "parent_ticket_id": self.ticket_id
            },
            outputs={
                "is_first_execute": True,
                "is_cloning": True
            }
        )
        auto_service = TicketCreateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.schedule(excute_data, excute_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_need_schedule_create(self):
        print("ticket_id:{}".format(self.ticket_id))
        pipeline_data = DataObject(
            inputs={"_loop": 0}, outputs={"_loop": 0, "is_cloning": True}
        )
        auto_service = TicketCreateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.need_schedule(pipeline_data)
        self.assertEqual(result, False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_approve.Ticket.do_before_enter_state")
    def test_excute_migrate(self, do_before_enter_state):
        do_before_enter_state.return_value = None
        print("ticket_id:{}".format(self.ticket_id))

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={
                "ticket_id": self.ticket_id,
                "parent_ticket_id": self.ticket_id
            },
            outputs={
                "is_first_execute": True,
                "is_cloning": False
            }
        )
        auto_service = ItsmMigrateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_approve.Ticket.do_before_enter_state")
    def test_schedule_migrate(self, do_before_enter_state):
        do_before_enter_state.return_value = None
        print("ticket_id:{}".format(self.ticket_id))

        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        schedule_parent_data = DataObject(
            inputs={
                "ticket_id": self.ticket_id,
                "parent_ticket_id": self.ticket_id
            },
            outputs={
                "is_first_execute": True,
                "is_migrate": True
            }
        )
        auto_service = ItsmMigrateService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_sign.Ticket.do_before_enter_sign_state")
    def test_excute_sign(self, do_before_enter_sign_state):
        do_before_enter_sign_state.return_value = ({}, {}, {})
        print("ticket_id:{}".format(self.ticket_id))

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={
                "ticket_id": self.ticket_id,
                "parent_ticket_id": self.ticket_id
            },
            outputs={
                "is_first_execute": True,
                "is_cloning": False
            }
        )
        auto_service = ItsmSignService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)


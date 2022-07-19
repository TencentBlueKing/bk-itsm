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

from itsm.pipeline_plugins.components.collections.bk_devops import BkDevOpsService
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
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.bk_devops.BkDevOpsService.prepare_build_params"
    )
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_devops.apigw_client")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_devops.Ticket")
    def test_execute(self, patch_ticket, apigw_client, patch_prepare_build_params):
        patch_ticket.state.return_value = {
            "extras": {
                "devops_info": {
                    "username": "user",
                    "project_id": {"value": "test", "name": "测试", "key": "project_id"},
                    "pipeline_id": {
                        "value": "p-216fafa1b9f44f2b95ed6bxxxxxxxxxx",
                        "name": "代码检查",
                        "key": "pipeline_id",
                    },
                    "constants": [
                        {"value": "test", "name": "bkapp_code", "key": "bkapp_code"}
                    ],
                }
            }
        }
        patch_prepare_build_params.return_value = {
            "bkapp_code": " test",
            "project_id": "test",
            "pipeline_id": "p-216fafa1b9f44f2b95ed6bxxxxxxxxxx",
        }
        patch_ticket.do_before_enter_state.return_value = None
        patch_ticket.update_state_before_enter = None
        patch_ticket.id.return_value = self.ticket_id

        apigw_client.devops.pipeline_build_start.return_value = {
            "data": {"id": "123xxx"},
            "message": "success",
            "status": 0,
        }
        print("ticket_id:{}".format(self.ticket_id))

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        devops_service = BkDevOpsService(name="bk_devops")
        devops_service._runtime_attrs = {"by_flow": 1}
        result = devops_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.bk_devops.BkDevOpsService.prepare_build_params"
    )
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_devops.Ticket")
    def test_excute_failed(self, patch_ticket, patch_prepare_build_params):
        patch_ticket.do_before_enter_state.return_value = None
        patch_ticket.state.return_value = {
            "extras": {
                "devops_info": {
                    "username": "user",
                    "project_id": {"value": "test", "name": "测试", "key": "project_id"},
                    "pipeline_id": {
                        "value": "p-216fafa1b9f44f2b95ed6bxxxxxxxxxx",
                        "name": "代码检查",
                        "key": "pipeline_id",
                    },
                    "constants": [
                        {"value": "test", "name": "bkapp_code", "key": "bkapp_code"}
                    ],
                }
            }
        }
        patch_prepare_build_params.return_value = {
            "bkapp_code": " test",
            "project_id": "test",
            "pipeline_id": "p-216fafa1b9f44f2b95ed6bxxxxxxxxxx",
        }
        patch_ticket.id.return_value = self.ticket_id
        print("ticket_id:{}".format(self.ticket_id))

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        devops_service = BkDevOpsService(name="bk_devops")
        devops_service._runtime_attrs = {"by_flow": 1}
        result = devops_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_devops.apigw_client")
    def test_schedule_running(self, apigw_client):
        apigw_client.devops.pipeline_build_status.return_value = {
            "data": {},
            "message": "String",
            "status": "RUNNING",
        }
        devops_service = BkDevOpsService(name="bk_devops")
        devops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "devops_username": "test_username",
                "devops_project_id": "123xxx",
                "devops_pipeline_id": "123xxx",
                "devops_build_id": "123xxx",
                "_loop": 0,
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )

        result = devops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_devops.apigw_client")
    def test_schedule_canceled(self, apigw_client):
        apigw_client.devops.pipeline_build_status.return_value = {
            "data": {},
            "message": "String",
            "status": "CANCELED",
        }
        devops_service = BkDevOpsService(name="bk_devops")
        devops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "devops_username": "test_username",
                "devops_project_id": "123xxx",
                "devops_pipeline_id": "123xxx",
                "devops_build_id": "123xxx",
                "_loop": 0,
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )

        result = devops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_devops.apigw_client")
    def test_schedule_failed(self, apigw_client):
        apigw_client.devops.pipeline_build_status.return_value = {
            "data": {},
            "message": "String",
            "status": "FAILED",
            "errorInfoList": [],
        }
        devops_service = BkDevOpsService(name="bk_devops")
        devops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "devops_username": "test_username",
                "devops_project_id": "123xxx",
                "devops_pipeline_id": "123xxx",
                "devops_build_id": "123xxx",
                "_loop": 0,
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )

        result = devops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_devops.apigw_client")
    def test_schedule_succeed(self, apigw_client):
        apigw_client.devops.pipeline_build_status.return_value = {
            "data": {},
            "message": "String",
            "status": "SUCCEED",
            "errorInfoList": [],
            "variables": {},
        }
        devops_service = BkDevOpsService(name="bk_devops")
        devops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "devops_username": "test_username",
                "devops_project_id": "123xxx",
                "devops_pipeline_id": "123xxx",
                "devops_build_id": "123xxx",
                "_loop": 0,
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )

        result = devops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, True)

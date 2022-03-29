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

import copy
import json
import mock

from blueapps.core.celery.celery import app
from django.test import TestCase, override_settings

from itsm.task.models import SopsTask, Task
from itsm.ticket.models import Ticket
from itsm.workflow.models import TaskSchema, TaskFieldSchema, TaskConfig, VERSION
from pipeline.engine.models import FunctionSwitch
from .test_params import sops_create_res, task_params, create_ticket_data, create_sops_task_data
from ...service.models import CatalogService


class SopsTaskTest(TestCase):
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        CatalogService.objects.create(service_id=1, is_deleted=False, catalog_id=2, creator="admin")
        FunctionSwitch.objects.init_db()

    def tearDown(self):
        Ticket.objects.all().delete()
        task_schema = TaskSchema.objects.filter(name="test")
        TaskFieldSchema.objects.filter(task_schema__in=task_schema).delete()
        task_schema.delete()
        SopsTask.objects.all().delete()
        Task.objects.all().delete()
        TaskConfig.objects.all().delete()

    @mock.patch("itsm.task.models.client_backend.sops")
    @mock.patch.object(Task, "call_sops_create_task")
    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_create_normal_task(self, mock_create_res, client_backend):
        client_backend.get_task_detail.return_value = {
            "result": True,
            "message": "",
            "constants": {},
            "data": {
                "task_url": "xxxx",
            }
        }
        mock_create_res.return_value = sops_create_res, task_params
        data = copy.deepcopy(create_ticket_data)
        url = "/api/ticket/receipts/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        ticket_id = rsp.data["data"]["id"]
        task_schema = TaskSchema.objects.create(name="test", component_type="NORMAL")
        TaskFieldSchema.objects.create(key="task_name", name="任务名称", task_schema=task_schema)
        TaskFieldSchema.objects.create(key="processors", name="处理人", task_schema=task_schema,
                                       sequence=1)
        ticket = Ticket.objects.get(id=ticket_id)
        TaskConfig.objects.create(
            workflow_id=ticket.flow_id, workflow_type=VERSION,
            execute_task_state=ticket.first_state_id, task_schema_id=task_schema.id,
            create_task_state=ticket.first_state_id
        )
        data = {
            "processors": "hoganren1",
            "processors_type": "PERSON",
            "fields": {"task_name": "task1"},
            "ticket_id": ticket_id,
            "state_id": ticket.first_state_id,
            "task_schema_id": task_schema.id,
        }
        url = "/api/task/tasks/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(rsp.data["message"], "success")

    @mock.patch("itsm.task.models.client_backend.sops")
    @mock.patch.object(Task, "call_sops_create_task")
    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_create_normal_task_need_start(self, mock_create_res, client_backend):
        client_backend.get_task_detail.return_value = {
            "result": True,
            "message": "",
            "constants": {},
            "data": {
                "task_url": "xxxx",
            }
        }
        mock_create_res.return_value = sops_create_res, task_params
        data = copy.deepcopy(create_ticket_data)
        url = "/api/ticket/receipts/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        ticket_id = rsp.data["data"]["id"]
        task_schema = TaskSchema.objects.create(name="test", component_type="NORMAL")
        TaskFieldSchema.objects.create(key="task_name", name="任务名称", task_schema=task_schema)
        TaskFieldSchema.objects.create(key="processors", name="处理人", task_schema=task_schema,
                                       sequence=1)
        ticket = Ticket.objects.get(id=ticket_id)
        TaskConfig.objects.create(
            workflow_id=ticket.flow_id, workflow_type=VERSION,
            execute_task_state=ticket.first_state_id, task_schema_id=task_schema.id,
            create_task_state=ticket.first_state_id
        )
        data = {
            "processors": "hoganren1",
            "processors_type": "PERSON",
            "fields": {"task_name": "task1"},
            "ticket_id": ticket_id,
            "state_id": ticket.first_state_id,
            "task_schema_id": task_schema.id,
            "need_start": True,
        }
        url = "/api/task/tasks/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(rsp.data["message"], "success")

    @mock.patch("itsm.task.models.client_backend.sops")
    @mock.patch.object(Task, "call_sops_create_task")
    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_create_sops_task_from_template(self, mock_create_res, client_backend):
        client_backend.get_task_detail.return_value = {
            "result": True,
            "message": "",
            "constants": {},
            "data": {
                "task_url": "xxxx",
            }
        }
        mock_create_res.return_value = sops_create_res, task_params
        data = copy.deepcopy(create_ticket_data)
        url = "/api/ticket/receipts/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        ticket_id = rsp.data["data"]["id"]
        task_schema = TaskSchema.objects.filter(component_type="SOPS").first()
        data = copy.deepcopy(create_sops_task_data)
        ticket = Ticket.objects.get(id=ticket_id)
        TaskConfig.objects.create(
            workflow_id=ticket.flow_id, workflow_type=VERSION,
            execute_task_state=ticket.first_state_id, task_schema_id=task_schema.id,
            create_task_state=ticket.first_state_id
        )
        data["ticket_id"] = ticket_id
        data["state_id"] = ticket.first_state_id
        data["task_schema_id"] = task_schema.id
        url = "/api/task/tasks/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(rsp.data["message"], "success")

    @mock.patch("itsm.task.models.client_backend.sops")
    @mock.patch.object(Task, "call_sops_update_task")
    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_create_sops_task_from_exist(self, mock_update_res, client_backend):
        mock_update_res.return_value = sops_create_res, task_params
        client_backend.get_task_detail.return_value = {
            "result": True,
            "message": "",
            "constants": {},
            "data": {
                "task_url": "xxxx",
            }
        }
        data = copy.deepcopy(create_ticket_data)
        url = "/api/ticket/receipts/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        ticket_id = rsp.data["data"]["id"]
        task_schema = TaskSchema.objects.filter(component_type="SOPS").first()
        data = copy.deepcopy(create_sops_task_data)
        ticket = Ticket.objects.get(id=ticket_id)
        TaskConfig.objects.create(
            workflow_id=ticket.flow_id, workflow_type=VERSION,
            execute_task_state=ticket.first_state_id, task_schema_id=task_schema.id,
            create_task_state=ticket.first_state_id
        )
        data["ticket_id"] = ticket_id
        data["task_schema_id"] = task_schema.id
        data["source"] = "task"
        data["state_id"] = ticket.first_state_id
        data["fields"]["sops_templates"]["task_id"] = 28239
        url = "/api/task/tasks/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(rsp.data["message"], "success")

    @mock.patch("itsm.task.models.client_backend.sops")
    @mock.patch.object(Task, "call_sops_create_task")
    @mock.patch.object(Task, "update_sops_task")
    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_update_sops_task(self, mock_create_res, mock_update_res, client_backend):
        # pipeline.return_value = None
        mock_create_res.return_value = sops_create_res, task_params
        mock_update_res.return_value = sops_create_res, task_params
        client_backend.get_task_detail.return_value = {
            "result": True,
            "message": "",
            "constants": {},
            "data": {
                "task_url": "xxxx",
            }
        }
        data = copy.deepcopy(create_ticket_data)
        url = "/api/ticket/receipts/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        ticket_id = rsp.data["data"]["id"]
        task_schema = TaskSchema.objects.filter(component_type="SOPS").first()
        data = copy.deepcopy(create_sops_task_data)
        ticket = Ticket.objects.get(id=ticket_id)
        TaskConfig.objects.create(
            workflow_id=ticket.flow_id, workflow_type=VERSION,
            execute_task_state=ticket.first_state_id, task_schema_id=task_schema.id,
            create_task_state=ticket.first_state_id
        )
        data["ticket_id"] = ticket_id
        data["state_id"] = ticket.first_state_id
        data["task_schema_id"] = task_schema.id
        url = "/api/task/tasks/"
        rsp = self.client.post(path=url, data=json.dumps(data), content_type="application/json")
        task_id = rsp.data["data"]["task_id"]
        url = "/api/task/tasks/{}/".format(task_id)
        rsp = self.client.patch(path=url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(rsp.data["message"], "success")

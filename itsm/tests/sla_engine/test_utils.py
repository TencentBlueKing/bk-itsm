# -*- coding: utf-8 -*-
import copy
import json
from datetime import datetime

import mock
from django.test import TestCase, override_settings
from blueapps.core.celery.celery import app

from itsm.service.models import Service, CatalogService
from itsm.sla_engine.utils import seconds_format
from itsm.tests.data.datas import DATA
from itsm.workflow.models import Workflow


class TestUtils(TestCase):
    def setUp(self) -> None:
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_seconds_format(self):
        seconds = 1640074389
        self.assertEqual(seconds_format(seconds), "455576:13:09")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_sla(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True
        workflow_data = copy.deepcopy(DATA)
        workflow, _, _ = Workflow.objects.restore(workflow_data)
        version = workflow.create_version()
        data = {
            "name": "service_create_test_{}".format(
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ),
            "key": "request",
            "workflow": version,
            "creator": "admin",
        }

        service = Service.objects.create(**data)

        start_id = version.first_state["id"]
        for item in version.states.values():
            if item["name"] == "审批节点":
                end_node_id = item["id"]

        sla_tasks = [
            {
                "color": "#34D385",
                "start_node_id": start_id,
                "end_node_id": end_node_id,
                "lines": [223],
                "states": [start_id, end_node_id],
                "sla_id": 2,
                "name": "7*24",
            }
        ]
        service.update_service_sla(sla_tasks)
        CatalogService.objects.create(
            service_id=service.id, is_deleted=False, catalog_id=2, creator="admin"
        )

        data = {
            "service_id": service.id,
            "service_type": "test",
            "fields": [
                {"type": "STRING", "key": "title", "value": "1", "choice": []},
                {
                    "type": "SELECT",
                    "key": "impact",
                    "value": "1",
                    "choice": [
                        {"key": "1", "name": "低"},
                        {"key": "2", "name": "中"},
                        {"key": "3", "name": "高"},
                    ],
                },
                {
                    "type": "SELECT",
                    "key": "urgency",
                    "value": "1",
                    "choice": [
                        {"key": "1", "name": "低"},
                        {"key": "2", "name": "中"},
                        {"key": "3", "name": "高"},
                    ],
                },
                {
                    "type": "SELECT",
                    "key": "priority",
                    "value": "1",
                    "choice": [
                        {"key": "1", "name": "低"},
                        {"key": "2", "name": "中"},
                        {"key": "3", "name": "高"},
                    ],
                },
            ],
            "creator": "admin",
        }

        url = "/openapi/ticket/create_ticket/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)

        ticket_id = rsp.data["data"]["id"]

        url = "/api/ticket/receipts/{}/sla_task/".format(ticket_id)
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.data["result"], True)

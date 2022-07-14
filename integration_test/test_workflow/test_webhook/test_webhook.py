# -*- coding: utf-8 -*-
import copy
import os
import time

from django.conf import settings
from django.test import override_settings

from integration_test.test_workflow.base import BaseTestCase
from integration_test.test_workflow.test_webhook.data.webhook import WEBHOOK_DATA
from itsm.ticket.models import TicketGlobalVariable
from itsm.workflow.models import State


class WebhookTestCase(BaseTestCase):
    def build_data(self):
        data = copy.deepcopy(WEBHOOK_DATA)

        data["workflow"]["states"]["274"]["extras"]["webhook_info"]["query_params"] = [
            {
                "check": "true",
                "desc": "",
                "key": "bk_app_code",
                "select": True,
                "value": settings.APP_CODE,
            },
            {
                "check": "true",
                "desc": "",
                "key": "bk_app_secret",
                "select": True,
                "value": settings.APP_TOKEN,
            },
            {
                "check": "true",
                "desc": "",
                "key": "bk_username",
                "select": True,
                "value": "admin",
            },
        ]
        return data

    def build_create_fields(self):
        COMPONENT_SYSTEM_HOST = os.environ.get(
            "BK_COMPONENT_API_URL", settings.BK_PAAS_INNER_HOST
        )

        fields = [
            {
                "type": "STRING",
                "id": 1,
                "key": "title",
                "value": "test_ticket",
                "choice": [],
            },
            {
                "type": "STRING",
                "id": 1,
                "key": "URL",
                "value": COMPONENT_SYSTEM_HOST.rstrip("/")
                + "/api/c/compapi/v2/cc/search_business/",
                "choice": [],
            },
        ]
        return fields

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_success(self):
        service = self.import_service(self.build_data())
        fields = self.build_create_fields()
        ticket_id = self.create_ticket(service, fields)

        time.sleep(3)
        ticket_info = self.get_ticket_info(ticket_id=ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "FINISHED")

        variable = TicketGlobalVariable.objects.get(ticket_id=ticket_id, name="执行结果")
        self.assertEqual(variable.value, "true")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_retry(self):
        data = self.build_data()
        query_params = data["workflow"]["states"]["274"]["extras"]["webhook_info"][
            "query_params"
        ]
        del query_params[2]

        service = self.import_service(data)
        fields = self.build_create_fields()

        COMPONENT_SYSTEM_HOST = os.environ.get(
            "BK_COMPONENT_API_URL", settings.BK_PAAS_INNER_HOST
        )

        ticket_id = self.create_ticket(service, fields)

        state_id = State.objects.get(
            workflow_id=service.workflow.workflow_id, name="Webhook"
        ).id

        inputs = {
            "inputs": {
                "method": "GET",
                "url": COMPONENT_SYSTEM_HOST.rstrip("/")
                + "/api/c/compapi/v2/cc/search_business/",
                "success_exp": "resp.result==true",
                "query_params": [
                    {"key": "bk_app_code", "value": settings.APP_CODE, "select": True},
                    {
                        "key": "bk_app_secret",
                        "value": settings.APP_TOKEN,
                        "select": True,
                    },
                    {
                        "check": True,
                        "key": "bk_username",
                        "value": "admin",
                        "desc": "",
                        "select": True,
                    },
                ],
                "auth": {"auth_type": "none", "auth_config": {}},
                "headers": [],
                "body": {"type": "", "raw_type": "", "content": ""},
                "settings": {"timeout": 10},
            },
            "state_id": int(state_id),
        }

        time.sleep(3)
        self.retry_node(ticket_id, inputs)

        time.sleep(5)

        ticket_info = self.get_ticket_info(ticket_id=ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "FINISHED")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ignore(self):
        data = self.build_data()
        query_params = data["workflow"]["states"]["274"]["extras"]["webhook_info"][
            "query_params"
        ]
        del query_params[2]

        service = self.import_service(data)
        fields = self.build_create_fields()

        ticket_id = self.create_ticket(service, fields)

        state_id = State.objects.get(
            workflow_id=service.workflow.workflow_id, name="Webhook"
        ).id

        time.sleep(3)

        params = {"inputs": {}, "is_direct": True, "state_id": state_id}
        self.ignore(ticket_id, params)

        time.sleep(5)

        ticket_info = self.get_ticket_info(ticket_id=ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "FINISHED")

        variable = TicketGlobalVariable.objects.get(ticket_id=ticket_id, name="执行结果")
        self.assertEqual(variable.value, "false")

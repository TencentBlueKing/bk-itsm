# -*- coding: utf-8 -*-
import json

import mock
from django.test import TestCase, override_settings
from requests import Response

from itsm.pipeline_plugins.components.collections.webhook import (
    WebHookService,
    ParamsBuilder,
)
from itsm.service.models import CatalogService
from itsm.ticket.models import Ticket
from blueapps.core.celery.celery import app
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

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.webhook.WebHookService.build_params"
    )
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.webhook.Ticket.do_before_enter_state"
    )
    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.requests.request")
    def test_excute(self, request, do_before_enter_state, build_params):
        extras = {
            "method": "GET",
            "url": "http://127.0.0.1/",
            "query_params": [
                {"key": "bk_app_code", "value": "itsm"},
            ],
            "headers": [],
            "body": {"type": "form_data", "params": [], "raw_type": "", "content": ""},
            "settings": {"timeout": 10},
            "success_exp": "",
        }

        build_params.return_value = extras
        do_before_enter_state.return_value = None

        response = Response()
        response.status_code = 200
        response._content = b"{}"
        response.json()
        request.return_value = response

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        auto_service = WebHookService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_params_builder(self):
        extras = {
            "method": "GET",
            "url": "{{URL}}",
            "query_params": [
                {"key": "bk_app_code", "value": "itsm"},
                {"key": "bk_app_secret", "value": "{{bk_app_secret}}"},
                {"key": "bk_username", "value": "admin"},
            ],
            "headers": [],
            "body": {"type": "form_data", "params": [], "raw_type": "", "content": ""},
            "settings": {"timeout": 10},
            "success_exp": "",
        }
        key_value = {
            "URL": "http://127.0.0.1",
            "bk_app_secret": "123456789",
        }
        result = ParamsBuilder(extras, key_value).result()
        self.assertEqual(result["url"], "http://127.0.0.1")
        self.assertEqual(result["query_params"]["bk_app_secret"], "123456789")

# -*- coding: utf-8 -*-
import time

from django.test import override_settings

from integration_test.test_workflow.base import BaseTestCase
from integration_test.test_workflow.testapi.data.api import API_DATA


class ApiTestCase(BaseTestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test(self):
        service = self.import_service(API_DATA)
        ticket_id = self.create_ticket(service)

        # 校验初次审批之后的单据详情是否符合预期
        ticket_info = self.get_ticket_info(ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "RUNNING")
        current_steps = ticket_info["data"]["current_steps"]
        self.assertEqual(len(current_steps), 0)

        time.sleep(5)
        ticket_info = self.get_ticket_info(ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "FINISHED")

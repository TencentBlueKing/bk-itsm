# -*- coding: utf-8 -*-
import time

from django.test import override_settings

from integration_test.test_workflow.base import BaseTestCase
from integration_test.test_workflow.test_approve.data.auto_approve import (
    AUTO_APPROVE_DATA,
)
from itsm.workflow.models import State


class AutoApproveTestCase(BaseTestCase):
    @override_settings(
        MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",), AUTO_APPROVE_TIME=5
    )
    def test(self):
        data = AUTO_APPROVE_DATA
        service = self.import_service(data)
        ticket_id = self.create_ticket(service)
        time.sleep(3)

        ticket_info = self.get_ticket_info(ticket_id)
        current_steps = ticket_info["data"]["current_steps"]
        self.assertEqual(len(current_steps), 1)
        self.assertEqual(current_steps[0]["name"], "异常分派+自动过单")

        state_id = State.objects.get(
            workflow_id=service.workflow.workflow_id, name="异常分派+自动过单"
        ).id
        self.exception_distribute(ticket_id, state_id, "admin")
        time.sleep(2)

        ticket_info = self.get_ticket_info(ticket_id)
        current_steps = ticket_info["data"]["current_steps"]
        self.assertEqual(current_steps[0]["name"], "异常分派+自动过单")

        time.sleep(10)
        ticket_info = self.get_ticket_info(ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "FINISHED")

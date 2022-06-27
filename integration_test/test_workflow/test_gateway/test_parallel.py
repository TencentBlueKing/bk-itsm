# -*- coding: utf-8 -*-
import time

from django.test import override_settings

from integration_test.test_workflow.base import BaseTestCase
from integration_test.test_workflow.test_gateway.data.parallel_gateway import (
    PARALLEL_GATEWAY_DATA,
)
from itsm.workflow.models import State


class ParallelTestCase(BaseTestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test(self):
        service = self.import_service(PARALLEL_GATEWAY_DATA)
        ticket_id = self.create_ticket(service)
        time.sleep(5)

        ticket_info = self.get_ticket_info(ticket_id=ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "RUNNING")
        current_steps = ticket_info["data"]["current_steps"]
        self.assertEqual(len(current_steps), 2)
        self.assertEqual(current_steps[0]["name"], "步骤二")
        self.assertEqual(current_steps[1]["name"], "步骤一")

        state_id = State.objects.get(
            workflow_id=service.workflow.workflow_id, name="步骤一"
        ).id

        self.proceed_ticket(ticket_id, state_id=state_id, fields=[])

        time.sleep(3)
        ticket_info = self.get_ticket_info(ticket_id=ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "RUNNING")
        current_steps = ticket_info["data"]["current_steps"]
        self.assertEqual(len(current_steps), 1)
        self.assertEqual(current_steps[0]["name"], "步骤二")

        state_id = State.objects.get(
            workflow_id=service.workflow.workflow_id, name="步骤二"
        ).id
        self.proceed_ticket(ticket_id, state_id=state_id, fields=[])

        time.sleep(3)
        ticket_info = self.get_ticket_info(ticket_id=ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "FINISHED")

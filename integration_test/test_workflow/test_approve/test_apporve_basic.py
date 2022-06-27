# -*- coding: utf-8 -*-
#
import time

from django.test import override_settings

from integration_test.test_workflow.base import BaseTestCase
from integration_test.test_workflow.test_approve.data.approve import APPROVE_DATA
from itsm.workflow.models import State


class ApproveBasicTest(BaseTestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_approve(self):
        data = APPROVE_DATA

        service = self.import_service(data)
        ticket_id = self.create_ticket(service)
        time.sleep(5)

        # 校验初次审批之后的单据详情是否符合预期
        ticket_info = self.get_ticket_info(ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "RUNNING")
        current_steps = ticket_info["data"]["current_steps"]
        self.assertEqual(len(current_steps), 1)
        self.assertEqual(current_steps[0]["name"], "审批节点")

        state_id = State.objects.get(
            workflow_id=service.workflow.workflow_id, name="审批节点"
        ).id

        # 处理审批节点
        fields = self.get_approve_fields(state_id=state_id, ticket_id=ticket_id)
        self.proceed_ticket(ticket_id, state_id, fields)

        time.sleep(5)

        ticket_info = self.get_ticket_info(ticket_id)
        current_steps = ticket_info["data"]["current_steps"]
        self.assertEqual(len(current_steps), 1)
        self.assertEqual(current_steps[0]["name"], "通过")

        # 处理人工节点
        state_id = State.objects.get(
            workflow_id=service.workflow.workflow_id, name="通过"
        ).id
        self.proceed_ticket(ticket_id, state_id, [])
        time.sleep(5)

        ticket_info = self.get_ticket_info(ticket_id)
        self.assertEqual(ticket_info["data"]["current_status"], "FINISHED")

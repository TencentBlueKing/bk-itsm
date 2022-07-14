# -*- coding: utf-8 -*-
import json

from django.test import TestCase

from itsm.component.constants import APPROVE_RESULT
from itsm.ticket.models import TicketField, Service


class BaseTestCase(TestCase):
    @classmethod
    def _enter_atomics(cls):
        """Open atomic blocks for multiple databases."""
        atomics = {}
        return atomics

    @classmethod
    def _rollback_atomics(cls, atomics):
        """Rollback atomic blocks opened by the previous method."""
        pass

    def import_service(self, data):
        data["name"] = "xxxxx"
        data["source"] = "service"
        service = Service.objects.clone(data, "admin")
        return service

    def exception_distribute(self, ticket_id, state_id, username):
        url = "/api/ticket/receipts/{}/exception_distribute/".format(ticket_id)
        params = {
            "state_id": state_id,
            "processors": username,
            "processors_type": "PERSON",
            "action_type": "EXCEPTION_DISTRIBUTE",
        }
        rsp = self.client.post(
            path=url, data=json.dumps(params), content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)

    def create_ticket(self, service, fields=None):
        service_id = service.id
        catalog_id = service.catalog_id

        default_fields = [
            {
                "type": "STRING",
                "id": 1,
                "key": "title",
                "value": "test_ticket",
                "choice": [],
            }
        ]

        params = {
            "catalog_id": catalog_id,
            "service_id": service_id,
            "service_type": "request",
            "fields": default_fields if fields is None else fields,
            "creator": "admin",
            "attention": True,
        }
        url = "/api/ticket/receipts/"
        rsp = self.client.post(
            path=url, data=json.dumps(params), content_type="application/json"
        )

        self.assertEqual(rsp.data["result"], True)

        ticket_id = rsp.data["data"]["id"]
        return ticket_id

    def get_ticket_info(self, ticket_id):
        url = "/api/ticket/receipts/{}/".format(ticket_id)
        rsp = self.client.get(path=url, content_type="application/json")

        self.assertEqual(rsp.data["result"], True)
        return rsp.data

    def get_approve_fields(self, state_id, ticket_id):
        node_fields = TicketField.objects.filter(state_id=state_id, ticket_id=ticket_id)

        fields = []
        remarked = False
        for field in node_fields:
            if field.meta.get("code") == APPROVE_RESULT:
                fields.append(
                    {
                        "id": field.id,
                        "key": field.key,
                        "type": field.type,
                        "choice": field.choice,
                        "value": "true",
                    }
                )
            else:
                if not remarked:
                    fields.append(
                        {
                            "id": field.id,
                            "key": field.key,
                            "type": field.type,
                            "choice": field.choice,
                            "value": "True",
                        }
                    )
                    remarked = True

        return fields

    def proceed_ticket(self, ticket_id, state_id, fields):
        url = "/api/ticket/receipts/{}/proceed/".format(ticket_id)
        # 处理单据
        data = {"state_id": state_id, "fields": fields}
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)

    def retry_node(self, ticket_id, data):
        url = "/api/ticket/receipts/{}/retry/".format(ticket_id)
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)

    def ignore(self, ticket_id, data):
        url = "/api/ticket/receipts/{}/ignore/".format(ticket_id)
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)

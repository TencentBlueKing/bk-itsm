# -*- coding: utf-8 -*-
import json

from django.test import TestCase, override_settings

from itsm.sla.models import Sla


class TestSlaProtocolsView(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_protocols_list(self):
        url = "/api/sla/protocols/?page=1&page_size=10&project_key=0"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.data["result"], True)
        self.assertEqual(rsp.data["data"]["count"], 2)
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_put_protocols(self):
        data = {
            "name": "7*24",
            "is_enabled": True,
            "is_reply_need": False,
            "action_policies": [],
            "project_key": "0",
            "policies": [],
        }

        sla = Sla.objects.filter(name="7*24").first()
        url = "/api/sla/protocols/{}/".format(sla.id)

        rsp = self.client.put(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.data["result"], True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_post_protocols(self):
        data = {
            "name": "7*24",
            "is_enabled": True,
            "is_reply_need": False,
            "action_policies": [],
            "project_key": "0",
            "policies": [],
        }

        url = "/api/sla/protocols/"

        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.data["result"], False)
        self.assertEqual(rsp.data["message"], "参数验证失败: 服务协议名称：[7*24] 已存在")

        data["name"] = "5*24"
        url = "/api/sla/protocols/"
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.data["result"], True)
        self.assertEqual(rsp.data["data"]["name"], "5*24")


class TestSchedulesView(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_schedules_list(self):
        url = "/api/sla/schedules/?project_key=0"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_post_chedules(self):
        url = "/api/sla/schedules/"
        data = {
            "name": "测试服务名称",
            "is_enabled": True,
            "days": [
                {
                    "type_of_day": "NORMAL",
                    "day_of_week": "0,1,2,3,4",
                    "duration": [
                        {
                            "start_time": "08:00:00",
                            "end_time": "12:00:00",
                            "name": "上午",
                        },
                        {
                            "start_time": "14:00:00",
                            "end_time": "18:00:00",
                            "name": "下午",
                        },
                    ],
                }
            ],
            "workdays": [],
            "holidays": [],
            "id": -1,
            "project_key": "0",
        }
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)
        self.assertEqual(rsp.data["data"]["name"], "测试服务名称")


class TestTicketHighlight(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ticket_highlight(self):
        url = "/api/sla/ticket_highlight/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], dict)


class TestPriorityMatrix(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ticket_highlight(self):
        url = "/api/sla/matrixs/priority_value/"
        data = {
            "api_instance_id": 0,
            "kv_relation": {},
            "urgency": "1",
            "impact": "1",
            "service_type": "request",
        }
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)
        self.assertEqual(rsp.data["data"], "1")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_matrix_of_service_type(self):
        url = "/api/sla/matrixs/matrix_of_service_type/"
        data = {"service_type": "request"}
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], dict)

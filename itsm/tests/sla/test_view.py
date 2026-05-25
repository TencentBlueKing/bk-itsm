# -*- coding: utf-8 -*-
import json

import mock
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
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.has_permission")
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_put_protocols(self, patch_iam_auth, patch_has_permission):
        patch_iam_auth.return_value = True
        patch_has_permission.return_value = True
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
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.has_permission")
    def test_post_protocols(self, patch_has_permission):
        patch_has_permission.return_value = True
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
        self.assertEqual(
            rsp.data["message"], "参数验证失败: 服务协议名称：[7*24] 已存在"
        )

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
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.has_permission")
    def test_post_chedules(self, patch_has_permission):
        patch_has_permission.return_value = True
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
    @mock.patch("itsm.sla.permissions.SlaMatrixPermit.has_permission")
    def test_matrix_of_service_type(self, patch_has_permission):
        patch_has_permission.return_value = True
        url = "/api/sla/matrixs/matrix_of_service_type/"
        data = {"service_type": "request"}
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], dict)


class TestSlaTimerRuleAuthz(TestCase):
    """spec round1 H-5：SlaTimerRule 视为系统配置，权限切到 IamAuthSystemPermit。"""

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.component.drf.permissions.IamAuthSystemPermit.iam_auth",
        return_value=False,
    )
    def test_create_rejects_when_iam_denied(self, _iam):
        rsp = self.client.post(
            "/api/sla/policy/timers/",
            data=json.dumps({"name": "t", "service_type": "request"}),
            content_type="application/json",
        )

        self.assertEqual(rsp.status_code, 403)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.component.drf.permissions.IamAuthSystemPermit.iam_auth",
        return_value=False,
    )
    def test_list_rejects_when_iam_denied(self, _iam):
        rsp = self.client.get("/api/sla/policy/timers/")
        # IamAuthSystemPermit 不区分 SAFE，统一走 operational_data_view
        self.assertEqual(rsp.status_code, 403)


class TestSlaProtocolTicketHighlightAuthz(TestCase):
    """spec round2 M-C：SlaViewSet.ticket_highlight 切系统级。"""

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.component.drf.permissions.IamAuthSystemPermit.iam_auth",
        return_value=False,
    )
    def test_ticket_highlight_put_rejects_when_iam_denied(self, _iam):
        rsp = self.client.put(
            "/api/sla/protocols/ticket_highlight/",
            data=json.dumps({"alert_color": "#fff", "timeout_color": "#000"}),
            content_type="application/json",
        )

        self.assertEqual(rsp.status_code, 403)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.component.drf.permissions.IamAuthSystemPermit.iam_auth",
        return_value=True,
    )
    def test_ticket_highlight_put_passes_when_iam_allows(self, _iam):
        from itsm.sla.models import SlaTicketHighlight

        SlaTicketHighlight.objects.all().delete()
        SlaTicketHighlight.objects.create(
            reply_timeout_color="#aaa", handle_timeout_color="#bbb"
        )
        rsp = self.client.put(
            "/api/sla/protocols/ticket_highlight/",
            data=json.dumps({"alert_color": "#fff", "timeout_color": "#000"}),
            content_type="application/json",
        )

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], True)
        latest = SlaTicketHighlight.objects.first()
        self.assertEqual(latest.reply_timeout_color, "#fff")
        self.assertEqual(latest.handle_timeout_color, "#000")


class TestDayViewSetAuthz(TestCase):
    """spec round1 M-5：DayViewSet 收紧到 IamAuthSystemPermit。"""

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.component.drf.permissions.IamAuthSystemPermit.iam_auth",
        return_value=False,
    )
    def test_list_rejects_when_iam_denied(self, _iam):
        rsp = self.client.get("/api/sla/days/")
        self.assertEqual(rsp.status_code, 403)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.component.drf.permissions.IamAuthSystemPermit.iam_auth",
        return_value=False,
    )
    def test_post_rejects_when_iam_denied(self, _iam):
        rsp = self.client.post(
            "/api/sla/days/",
            data=json.dumps({"type_of_day": "NORMAL", "day_of_week": "0"}),
            content_type="application/json",
        )
        self.assertEqual(rsp.status_code, 403)


class TestPriorityValueAuthz(TestCase):
    """spec round1 M-5：priority_value 仅要求登录态，未登录拒绝。"""

    @override_settings(MIDDLEWARE=())
    def test_priority_value_rejects_anonymous(self):
        rsp = self.client.post(
            "/api/sla/matrixs/priority_value/",
            data=json.dumps(
                {"urgency": "1", "impact": "1", "service_type": "request"}
            ),
            content_type="application/json",
        )
        self.assertIn(rsp.status_code, (401, 403))

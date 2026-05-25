# -*- coding: utf-8 -*-

import json

import mock
from django.test import TestCase, override_settings

from itsm.postman.rpc.core.request import CompRequest


class TestCompRequestSafeMode(TestCase):
    def test_parse_params_safe_mode_should_render_whitelisted_placeholders(self):
        params = {
            "source_uri": "demo_rpc",
            "ip": "1.1.1.1",
            "username": "admin",
            "profile": {"city": "shenzhen"},
            "ip_list": ["1.1.1.1", "2.2.2.2"],
            "meta": {
                "ip": "${params_ip}",
                "name": "user-${params_username}",
                "profile": "${params_profile}",
                "city": "${params_profile['city']}",
                "first_ip": "${params_ip_list[0]}",
            },
        }

        result, request_params = CompRequest.parse_params(params, safe_mode=True)

        self.assertTrue(result)
        self.assertEqual(request_params["ip"], "1.1.1.1")
        self.assertEqual(request_params["name"], "user-admin")
        self.assertEqual(request_params["profile"], {"city": "shenzhen"})
        self.assertEqual(request_params["city"], "shenzhen")
        self.assertEqual(request_params["first_ip"], "1.1.1.1")

    def test_parse_params_safe_mode_should_reject_unsafe_expression(self):
        params = {
            "source_uri": "demo_rpc",
            "meta": {
                "cmd": "${__import__('os').system('id')}",
            },
        }

        result, request_params = CompRequest.parse_params(params, safe_mode=True)

        self.assertFalse(result)
        self.assertEqual(request_params, [])


class TestRpcApiView(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.postman.views.ComponentLibrary.get_component_class")
    def test_post_should_reject_unsafe_meta(self, patch_get_component_class):
        resp = self.client.post(
            "/api/postman/rpc_api/",
            data=json.dumps(
                {
                    "source_uri": "demo_rpc",
                    "meta": {
                        "cmd": "${__import__('os').system('id')}",
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["code"], "OK")
        self.assertEqual(
            resp.data["message"], "Render context error, see the log for details"
        )
        self.assertEqual(resp.data["data"], [])
        patch_get_component_class.assert_not_called()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.postman.views.ComponentLibrary.get_component_class")
    def test_post_should_invoke_component_when_meta_is_safe(
        self, patch_get_component_class
    ):
        class FakeComponent(object):
            def __init__(self, request):
                self.request = request

            def invoke(self):
                return {
                    "result": True,
                    "code": "OK",
                    "data": {
                        "ip": self.request.data["ip"],
                        "name": self.request.data["name"],
                    },
                }

        patch_get_component_class.return_value = FakeComponent

        resp = self.client.post(
            "/api/postman/rpc_api/",
            data=json.dumps(
                {
                    "source_uri": "demo_rpc",
                    "ip": "1.1.1.1",
                    "username": "admin",
                    "meta": {
                        "ip": "${params_ip}",
                        "name": "user-${params_username}",
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")
        self.assertEqual(resp.data["data"]["ip"], "1.1.1.1")
        self.assertEqual(resp.data["data"]["name"], "user-admin")
        patch_get_component_class.assert_called_once_with("rpc", "demo_rpc")


class TestRpcApiPermission(TestCase):
    """spec round2 H-6：RpcApiViewSet 仅管理员可写，登录态可读。"""

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    @mock.patch(
        "itsm.role.models.UserRole.is_workflow_manager", return_value=False
    )
    def test_post_rejects_non_manager(self, _wm, _su):
        resp = self.client.post(
            "/api/postman/rpc_api/",
            data=json.dumps({"source_uri": "demo_rpc"}),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 403)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    @mock.patch(
        "itsm.role.models.UserRole.is_workflow_manager", return_value=False
    )
    def test_get_allows_authenticated_user(self, _wm, _su):
        resp = self.client.get("/api/postman/rpc_api/")

        self.assertEqual(resp.status_code, 200)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.postman.views.ComponentLibrary.get_component_class")
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=True)
    @mock.patch(
        "itsm.role.models.UserRole.is_workflow_manager", return_value=False
    )
    def test_post_allows_itsm_superuser(
        self, _wm, _su, patch_get_component_class
    ):
        class FakeComponent(object):
            def __init__(self, request):
                self.request = request

            def invoke(self):
                return {"result": True, "code": "OK", "data": {}}

        patch_get_component_class.return_value = FakeComponent

        resp = self.client.post(
            "/api/postman/rpc_api/",
            data=json.dumps({"source_uri": "demo_rpc"}),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], True)

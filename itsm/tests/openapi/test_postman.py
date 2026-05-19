# -*- coding: utf-8 -*-
import json

import mock
from django.test import TestCase, override_settings
from rest_framework import status

from itsm.meta.models import Context


class PostManOpenApiTest(TestCase):
    @staticmethod
    def _mock_context_value(allowed_host_suffixes=None):
        context_map = {
            "postman_run_api_allowed_host_suffixes": allowed_host_suffixes,
        }
        return lambda key: context_map.get(key)

    def setUp(self):
        Context.objects.filter(
            key__in=[
                "postman_run_api_allowed_host_suffixes",
            ]
        ).delete()

    def tearDown(self):
        Context.objects.filter(
            key__in=[
                "postman_run_api_allowed_host_suffixes",
            ]
        ).delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_run_api_should_reject_when_missing_allowed_host_suffix_config(
        self, patch_jwt_client
    ):
        patch_jwt_client.is_valid.return_value = True

        with mock.patch(
            "itsm.openapi.base_service.views.postman.ContextService.get_context_value",
            side_effect=self._mock_context_value(),
        ):
            resp = self.client.post(
                "/openapi/v2/postman/run_api/",
                data=json.dumps(
                    {
                        "method": "GET",
                        "url": "https://api.example.com/test",
                        "headers": {
                            "x-bkapi-authorization": json.dumps(
                                {"bk_app_code": "demo", "bk_app_secret": "secret"}
                            )
                        },
                    }
                ),
                content_type="application/json",
            )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["code"], "GET_CUSTOM_API_DATA_ERROR")
        self.assertEqual(
            resp.data["message"], "获取自定义数据异常: 请求失败，未配置可访问的授权域名"
        )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_run_api_should_reject_unsupported_scheme(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True
        Context.objects.update_or_create(
            key="postman_run_api_allowed_host_suffixes",
            defaults={"value": ".example.com"},
        )

        resp = self.client.post(
            "/openapi/v2/postman/run_api/",
            data=json.dumps(
                {
                    "method": "GET",
                    "url": "ftp://api.example.com/test",
                    "headers": {
                        "x-bkapi-authorization": json.dumps(
                            {"bk_app_code": "demo", "bk_app_secret": "secret"}
                        )
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["code"], "GET_CUSTOM_API_DATA_ERROR")
        self.assertEqual(
            resp.data["message"], "获取自定义数据异常: 请求失败，仅支持 http/https 协议"
        )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_run_api_should_reject_unauthorized_hostname(self, patch_jwt_client):
        patch_jwt_client.is_valid.return_value = True

        with mock.patch(
            "itsm.openapi.base_service.views.postman.ContextService.get_context_value",
            side_effect=self._mock_context_value(".example.com,.bk.tencent.com"),
        ):
            resp = self.client.post(
                "/openapi/v2/postman/run_api/",
                data=json.dumps(
                    {
                        "method": "GET",
                        "url": "https://api.evil.com/test",
                        "headers": {
                            "x-bkapi-authorization": json.dumps(
                                {"bk_app_code": "demo", "bk_app_secret": "secret"}
                            )
                        },
                    }
                ),
                content_type="application/json",
            )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["code"], "GET_CUSTOM_API_DATA_ERROR")
        self.assertEqual(
            resp.data["message"],
            "获取自定义数据异常: 请求失败，目标域名未被授权访问，hostname=api.evil.com",
        )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_run_api_should_reject_when_missing_authorization_header(
        self, patch_jwt_client
    ):
        patch_jwt_client.is_valid.return_value = True

        with mock.patch(
            "itsm.openapi.base_service.views.postman.ContextService.get_context_value",
            side_effect=self._mock_context_value("*.example.com"),
        ):
            resp = self.client.post(
                "/openapi/v2/postman/run_api/",
                data=json.dumps(
                    {
                        "method": "GET",
                        "url": "https://api.example.com/test",
                        "headers": {},
                    }
                ),
                content_type="application/json",
            )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["code"], "GET_CUSTOM_API_DATA_ERROR")
        self.assertEqual(
            resp.data["message"],
            "获取自定义数据异常: 请求失败，缺少 x-bkapi-authorization 请求头",
        )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    def test_run_api_should_reject_subdomain_when_only_exact_hostname_allowed(
        self, patch_jwt_client
    ):
        patch_jwt_client.is_valid.return_value = True

        with mock.patch(
            "itsm.openapi.base_service.views.postman.ContextService.get_context_value",
            side_effect=self._mock_context_value("example.com"),
        ):
            resp = self.client.post(
                "/openapi/v2/postman/run_api/",
                data=json.dumps(
                    {
                        "method": "GET",
                        "url": "https://api.example.com/test",
                        "headers": {
                            "x-bkapi-authorization": json.dumps(
                                {"bk_app_code": "demo", "bk_app_secret": "secret"}
                            )
                        },
                    }
                ),
                content_type="application/json",
            )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["code"], "GET_CUSTOM_API_DATA_ERROR")
        self.assertEqual(
            resp.data["message"],
            "获取自定义数据异常: 请求失败，目标域名未被授权访问，hostname=api.example.com",
        )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.decorators.JWTClient")
    @mock.patch("itsm.openapi.base_service.views.postman.requests.request")
    def test_run_api_should_pass_for_allowed_wildcard_host(
        self, patch_request, patch_jwt_client
    ):
        patch_jwt_client.is_valid.return_value = True

        response = mock.Mock()
        response.json.return_value = {"result": True, "message": "success"}
        patch_request.return_value = response

        with mock.patch(
            "itsm.openapi.base_service.views.postman.ContextService.get_context_value",
            side_effect=self._mock_context_value("*.example.com,api.bk.tencent.com"),
        ):
            resp = self.client.post(
                "/openapi/v2/postman/run_api/",
                data=json.dumps(
                    {
                        "method": "GET",
                        "url": "https://api.example.com/test",
                        "headers": {
                            "x-bkapi-authorization": json.dumps(
                                {"bk_app_code": "demo", "bk_app_secret": "secret"}
                            )
                        },
                        "query_params": {"page": 1},
                    }
                ),
                content_type="application/json",
            )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")
        self.assertEqual(resp.data["message"], "success")
        self.assertEqual(resp.data["data"], {"result": True, "message": "success"})
        patch_request.assert_called_once_with(
            "GET",
            "https://api.example.com/test",
            data=json.dumps({}),
            params={"page": 1},
            headers={
                "x-bkapi-authorization": json.dumps(
                    {"bk_app_code": "demo", "bk_app_secret": "secret"}
                ),
                "Content-Type": "application/json",
            },
            timeout=10,
            allow_redirects=False,
        )

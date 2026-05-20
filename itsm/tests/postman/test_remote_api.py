# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from unittest import mock

from django.test import TestCase, override_settings

from itsm.postman.models import RemoteApi, RemoteSystem, RemoteApiInstance
from itsm.postman.serializers import RemoteApiSerializer, ApiInstanceSerializer


class TestRemoteApi(TestCase):
    
    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    def test_list(self):
        url = "/api/postman/remote_api/"

        resp = self.client.get(url)

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")
        self.assertIsInstance(resp.data["data"], list)

    @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    @mock.patch("itsm.postman.views.bk.http")
    def test_run_api_should_ignore_request_code_override(self, mock_http):
        remote_system = RemoteSystem.objects.create(
            creator="admin",
            updated_by="admin",
            name="test-system",
            code="TEST_SYSTEM",
            domain="https://example.com",
            desc="",
            owners="admin",
            project_key="public",
        )
        remote_api = RemoteApi.objects.create(
            creator="admin",
            updated_by="admin",
            remote_system=remote_system,
            name="test-api",
            path="/test/api/",
            version="v1",
            func_name="test_api",
            method="GET",
            desc="",
            owners="admin",
            req_headers=[],
            req_params=[],
            req_body={},
            rsp_data={},
            before_req="stored_before_req",
            map_code="stored_map_code",
            is_activated=True,
        )
        mock_http.return_value = {"result": True, "message": "success", "data": {}}

        url = "/api/postman/remote_api/{}/run_api/".format(remote_api.id)
        payload = {
            "req_params": {"foo": "bar"},
            "before_req": "query_params['__local_poc_marker__'] = 'executed'",
            "map_code": "response['data'] = {'__local_poc_marker__': 'executed'}",
        }

        resp = self.client.post(url, data=payload, content_type="application/json")

        self.assertEqual(resp.data["result"], True)
        mock_http.assert_called_once()
        config = mock_http.call_args.kwargs["config"]
        self.assertEqual(config["query_params"], {"foo": "bar"})
        self.assertEqual(config["before_req"], "stored_before_req")
        self.assertEqual(config["map_code"], "stored_map_code")

    def test_remote_api_serializer_should_reject_custom_script_fields(self):
        remote_system = RemoteSystem.objects.create(
            creator="admin",
            updated_by="admin",
            name="test-system",
            code="TEST_SYSTEM",
            domain="https://example.com",
            desc="",
            owners="admin",
            project_key="public",
        )
        serializer = RemoteApiSerializer(
            data={
                "remote_system": remote_system.id,
                "name": "test-api",
                "owners": "admin",
                "path": "/test/api/",
                "version": "v1",
                "method": "GET",
                "func_name": "test_api",
                "desc": "",
                "is_activated": True,
                "req_headers": [],
                "req_params": [],
                "req_body": {},
                "rsp_data": {},
                "before_req": "query_params['x'] = 1",
                "map_code": "response['data'] = {}",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("before_req", serializer.errors)
        self.assertIn("map_code", serializer.errors)

    def test_api_instance_serializer_should_reject_custom_script_fields(self):
        remote_system = RemoteSystem.objects.create(
            creator="admin",
            updated_by="admin",
            name="test-system-2",
            code="TEST_SYSTEM_2",
            domain="https://example.com",
            desc="",
            owners="admin",
            project_key="public",
        )
        remote_api = RemoteApi.objects.create(
            creator="admin",
            updated_by="admin",
            remote_system=remote_system,
            name="test-api-2",
            path="/test/api/2/",
            version="v1",
            func_name="test_api_2",
            method="GET",
            desc="",
            owners="admin",
            req_headers=[],
            req_params=[],
            req_body={},
            rsp_data={},
            is_activated=True,
        )
        serializer = ApiInstanceSerializer(
            data={
                "remote_api": remote_api.id,
                "remote_api_id": remote_api.id,
                "req_params": {},
                "req_body": {},
                "rsp_data": "",
                "before_req": "query_params['x'] = 1",
                "map_code": "response['data'] = {}",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("before_req", serializer.errors)
        self.assertIn("map_code", serializer.errors)

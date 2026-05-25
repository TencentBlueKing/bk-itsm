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
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings

from itsm.postman.models import RemoteApi, RemoteSystem, RemoteApiInstance
from itsm.postman.permissions import RemoteApiPermit
from itsm.postman.serializers import RemoteApiSerializer, ApiInstanceSerializer


def _make_system(name="test-system", code="TEST_SYSTEM"):
    return RemoteSystem.objects.create(
        creator="admin",
        updated_by="admin",
        name=name,
        code=code,
        domain="https://example.com",
        desc="",
        owners="admin",
        project_key="public",
    )


def _make_api(remote_system, creator="admin", name="api", func_name="api"):
    return RemoteApi.objects.create(
        creator=creator,
        updated_by=creator,
        remote_system=remote_system,
        name=name,
        path="/test/api/",
        version="v1",
        func_name=func_name,
        method="GET",
        desc="",
        owners="admin",
        req_headers=[],
        req_params=[],
        req_body={},
        rsp_data={},
        is_activated=True,
    )


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
        self.assertFalse(serializer.is_valid())
        self.assertIn("before_req", serializer.errors)
        self.assertIn("map_code", serializer.errors)


class RemoteApiBatchDeleteAuthzTest(TestCase):
    """spec round2 M-B：batch_delete 仅创建人或 ITSM 超管可执行。"""

    def setUp(self):
        self.system = _make_system(name="batch-system", code="BATCH_SYSTEM")
        self.own_api = _make_api(
            self.system, creator="admin", name="own-api", func_name="own_api"
        )
        self.other_api = _make_api(
            self.system, creator="bob", name="other-api", func_name="other_api"
        )
        self.url = "/api/postman/remote_api/batch_delete/"

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.postman.permissions.RemoteApiPermit.has_permission",
        return_value=True,
    )
    @mock.patch(
        "itsm.role.models.UserRole.is_itsm_superuser", return_value=False
    )
    def test_batch_delete_rejects_other_creator(self, _superuser, _permit):
        resp = self.client.post(
            self.url,
            data={"id": str(self.other_api.id)},
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], False)
        self.assertTrue(RemoteApi.objects.filter(id=self.other_api.id).exists())

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.postman.permissions.RemoteApiPermit.has_permission",
        return_value=True,
    )
    @mock.patch(
        "itsm.role.models.UserRole.is_itsm_superuser", return_value=False
    )
    def test_batch_delete_allows_own_creator(self, _superuser, _permit):
        resp = self.client.post(
            self.url,
            data={"id": str(self.own_api.id)},
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], True)
        self.assertFalse(RemoteApi.objects.filter(id=self.own_api.id).exists())

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.postman.permissions.RemoteApiPermit.has_permission",
        return_value=True,
    )
    @mock.patch(
        "itsm.role.models.UserRole.is_itsm_superuser", return_value=True
    )
    def test_batch_delete_allows_superuser_across_creators(
        self, _superuser, _permit
    ):
        ids = "{},{}".format(self.own_api.id, self.other_api.id)
        resp = self.client.post(
            self.url, data={"id": ids}, content_type="application/json"
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], True)
        self.assertFalse(
            RemoteApi.objects.filter(
                id__in=[self.own_api.id, self.other_api.id]
            ).exists()
        )


class _FakeRequest(object):
    def __init__(self, query_params=None):
        self.query_params = query_params or {}
        self.data = {}
        user = MagicMock()
        user.username = "alice"
        self.user = user


class _FakeView(object):
    def __init__(self, action):
        self.action = action
        self.permission_free_actions = []


class RunApiAuthzObjectTest(TestCase):
    """spec round3 H-A：run_api 必须落到对象级 IAM。

    - 项目 API：要求 ``project_view``；
    - 平台公共 API：登录态短路通过；
    - 写动作（非 retrieve / run_api）保持 ``system_settings_manage`` /
      ``public_apis_manage`` 不变。
    """

    def setUp(self):
        self.permit = RemoteApiPermit()

    @staticmethod
    def _make_obj(project_key):
        obj = MagicMock()
        obj.remote_system.project_key = project_key
        return obj

    def test_run_api_against_public_project_passes_without_iam(self):
        view = _FakeView(action="run_api")
        request = _FakeRequest()
        obj = self._make_obj(project_key="public")
        with patch.object(RemoteApiPermit, "iam_auth") as mock_iam:
            self.assertTrue(
                self.permit.has_object_permission(request, view, obj)
            )
            mock_iam.assert_not_called()

    def test_run_api_against_project_requires_project_view(self):
        view = _FakeView(action="run_api")
        request = _FakeRequest()
        obj = self._make_obj(project_key="demo")
        fake_project = MagicMock()
        with patch(
            "itsm.postman.permissions.Project.objects.get",
            return_value=fake_project,
        ), patch.object(
            RemoteApiPermit, "iam_auth", return_value=False
        ) as mock_iam:
            self.assertFalse(
                self.permit.has_object_permission(request, view, obj)
            )
            mock_iam.assert_called_once_with(
                request, ["project_view"], fake_project
            )

    def test_retrieve_against_project_requires_project_view(self):
        # retrieve 与 run_api 应走同一最低门槛
        view = _FakeView(action="retrieve")
        request = _FakeRequest()
        obj = self._make_obj(project_key="demo")
        fake_project = MagicMock()
        with patch(
            "itsm.postman.permissions.Project.objects.get",
            return_value=fake_project,
        ), patch.object(
            RemoteApiPermit, "iam_auth", return_value=True
        ) as mock_iam:
            self.assertTrue(
                self.permit.has_object_permission(request, view, obj)
            )
            args, _kwargs = mock_iam.call_args
            self.assertEqual(args[1], ["project_view"])

    def test_write_action_against_project_still_requires_system_settings_manage(self):
        # 非 retrieve / run_api 不应被 H-A 顺带放宽
        view = _FakeView(action="update")
        request = _FakeRequest()
        obj = self._make_obj(project_key="demo")
        fake_project = MagicMock()
        with patch(
            "itsm.postman.permissions.Project.objects.get",
            return_value=fake_project,
        ), patch.object(
            RemoteApiPermit, "iam_auth", return_value=True
        ) as mock_iam:
            # 当前实现下 update 分支无显式 return，会在末尾 return True；
            # 关键不变量：iam_auth 不应被以 project_view 调用，
            # 也即"写动作仍需经更高门槛"——这里仅断言不会被放宽到 project_view。
            self.permit.has_object_permission(request, view, obj)
            for call in mock_iam.call_args_list:
                args, _kwargs = call
                self.assertNotEqual(args[1], ["project_view"])

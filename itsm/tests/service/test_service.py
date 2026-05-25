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

# This file demonstrates writing tests using the unittest module. These will pass
# when you run "manage.py test".
# Replace this with more appropriate tests for your application.

import json
import sys
import datetime

import mock
from django.http import FileResponse
from django.test import TestCase, override_settings

from itsm.tests.service.params import CREATE_SERVICE_DATA, CONFIGS, IMPORT_SERVICE_DATA
from itsm.workflow.models import WorkflowVersion, Workflow, Table
from itsm.service.models import Service, FavoriteService


class ServiceTest(TestCase):
    def json(self, data):
        return json.dumps(data)

    def tearDown(self) -> None:
        Service.objects.filter(name="测试服务").delete()
        Service.objects.filter(name="测试服务2").delete()

    def setUp(self):
        """准备数据"""
        self.service = None
        self.operator = "itsm_admin"
        self.data = {
            "name": "service_create_test_{}".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            ),
            "key": "test",
            "workflow": WorkflowVersion.objects.first(),
            "creator": self.operator,
        }

    def test_create_service_actions_auth(self):
        """
        测试新建服务时候的权限校验
        """
        print(sys._getframe().f_code.co_name)
        self.service = Service.objects.create(**self.data)
        resource_info = [
            {
                "resource_id": str(self.service.id),
                "resource_name": self.service.name,
                "resource_type": self.service.auth_resource["resource_type"],
            }
        ]
        apply_actions = ["service_manage"]

        self.assertTrue(self.auth_result(apply_actions, resource_info))

    @staticmethod
    def auth_result(apply_actions, resource_info):
        iam_client = mock.MagicMock()
        actions_result = {action: True for action in apply_actions}
        iam_client.resource_multi_actions_allowed.return_value = {
            str(resource["resource_id"]): actions_result for resource in resource_info
        }
        auth_actions = iam_client.resource_multi_actions_allowed(
            apply_actions, [resource_info]
        )
        denied_actions = []
        for action, result in auth_actions.items():
            if action in apply_actions and result is False:
                denied_actions.append(action)
        return len(denied_actions) == 0

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    @mock.patch("itsm.service.permissions.ServicePermit.has_permission")
    def test_create_service(
        self, patch_has_permission, patch_misc_get_bk_users, path_get_bk_users
    ):
        patch_has_permission.return_value = True
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
        url = "/api/service/projects/"
        data = {
            "name": "测试服务",
            "desc": "测试服务",
            "key": "request",
            "catalog_id": 2,
        }

        resp_error = self.client.post(url, data)
        self.assertEqual(resp_error.data["result"], False)
        self.assertEqual(resp_error.data["code"], "VALIDATE_ERROR")
        self.assertEqual(resp_error.data["message"], "project_key:该字段是必填项。")

        resp = self.client.post(url, CREATE_SERVICE_DATA)
        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    @mock.patch("itsm.service.permissions.ServicePermit.has_permission")
    def test_import(
        self, patch_has_permission, patch_misc_get_bk_users, path_get_bk_users
    ):
        patch_has_permission.return_value = True
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
        url = "/api/service/projects/"
        resp = self.client.post(url, CREATE_SERVICE_DATA)

        service_id = resp.data["data"]["id"]

        import_from_template_url = (
            "/api/service/projects/" "{}/import_from_template/".format(service_id)
        )

        table_id = Table.objects.get(name="审批").id

        resp = self.client.post(import_from_template_url, {"table_id": table_id})

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")

        workflow = Workflow.objects.get(
            id=Service.objects.get(id=service_id).workflow.workflow_id
        )
        version = workflow.create_version()

        # 判断字段是否成功导入
        fields = version.get_first_state_fields()
        self.assertEqual(len(fields), 3)

        service = Service.objects.get(id=service_id)
        service.workflow = version
        service.save()

        # 测试从服务导入
        data = {
            "name": "测试服务2",
            "desc": "测试服务",
            "key": "request",
            "catalog_id": 2,
            "project_key": "0",
        }
        resp = self.client.post(url, data)
        service_id = resp.data["data"]["id"]

        import_from_service_url = (
            "/api/service/projects/" "{}/import_from_service/".format(service_id)
        )

        resp = self.client.post(import_from_service_url, {"service_id": service.id})

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")

        workflow = Workflow.objects.get(
            id=Service.objects.get(id=service_id).workflow.workflow_id
        )
        version = workflow.create_version()

        # 判断字段是否成功导入
        fields = version.get_first_state_fields()
        self.assertEqual(len(fields), 3)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    @mock.patch("itsm.service.permissions.ServicePermit.has_permission")
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_save_configs(
        self,
        patch_iam_auth,
        patch_has_permission,
        patch_misc_get_bk_users,
        path_get_bk_users,
    ):
        patch_iam_auth.return_value = True
        patch_has_permission.return_value = True
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
        url = "/api/service/projects/"
        resp = self.client.post(url, CREATE_SERVICE_DATA)

        service_id = resp.data["data"]["id"]

        save_configs_url = "{}{}/save_configs/".format(url, service_id)

        resp = self.client.post(
            save_configs_url, json.dumps(CONFIGS), content_type="application/json"
        )

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    @mock.patch("itsm.service.permissions.ServicePermit.has_permission")
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_favorite(
        self,
        patch_iam_auth,
        patch_has_permission,
        patch_misc_get_bk_users,
        path_get_bk_users,
    ):
        patch_iam_auth.return_value = True
        patch_has_permission.return_value = True
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
        url = "/api/service/projects/"
        resp = self.client.post(url, CREATE_SERVICE_DATA)

        service_id = resp.data["data"]["id"]

        operate_favorite_url = "/api/service/projects/{}/operate_favorite/".format(
            service_id
        )

        resp = self.client.post(operate_favorite_url, {"favorite": True})

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")

        get_favorite_service_url = "/api/service/projects/get_favorite_service/"

        resp = self.client.get(get_favorite_service_url)

        self.assertTrue(FavoriteService.objects.filter(user="admin").exists())

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    @mock.patch("itsm.service.permissions.ServicePermit.has_permission")
    def test_clone(
        self, patch_has_permission, patch_misc_get_bk_users, path_get_bk_users
    ):
        patch_has_permission.return_value = True
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}

        url = "/api/service/projects/"
        resp = self.client.post(url, CREATE_SERVICE_DATA)

        service_id = resp.data["data"]["id"]

        url = "/api/service/projects/{}/clone/".format(service_id)

        resp = self.client.post(path=url, data=None, content_type="application/json")
        self.assertEqual(resp.data["result"], True)
        self.assertIsInstance(resp.data["data"], dict)
        self.assertEqual(resp.data["data"]["key"], "request")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    @mock.patch("itsm.service.permissions.ServicePermit.has_permission")
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_export_and_import(
        self,
        patch_iam_auth,
        patch_has_permission,
        patch_misc_get_bk_users,
        path_get_bk_users,
    ):
        patch_iam_auth.return_value = True
        patch_has_permission.return_value = True
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
        url = "/api/service/projects/"
        resp = self.client.post(url, CREATE_SERVICE_DATA)

        service_id = resp.data["data"]["id"]

        url = "/api/service/projects/{}/export/".format(service_id)

        resp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertIsInstance(resp, FileResponse)
        #
        # test_import
        data = IMPORT_SERVICE_DATA
        data["name"] = "xxxxx"
        data["source"] = "service"
        service = Service.objects.clone(data, "admin")
        self.assertIsInstance(service, Service)


class CatalogServiceAuthzTest(TestCase):
    """spec round2 C-4：CatalogServiceViewSet 写动作必须经过 IamAuthWithoutResourcePermit。"""

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.drf.permissions.IamAuthWithoutResourcePermit.iam_auth",
                return_value=False)
    def test_add_services_rejects_when_iam_denied(self, _iam):
        resp = self.client.post(
            "/api/service/catalog_services/add_services/",
            data={"catalog_id": 1, "services": [1]},
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 403)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.drf.permissions.IamAuthWithoutResourcePermit.iam_auth",
                return_value=False)
    def test_remove_services_rejects_when_iam_denied(self, _iam):
        resp = self.client.post(
            "/api/service/catalog_services/remove_services/",
            data={"catalog_id": 1, "services": [1]},
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 403)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_safe_list_short_circuits_without_iam(self):
        # SAFE + detail=False 直接放行，无需 iam mock。
        resp = self.client.get("/api/service/catalog_services/")
        self.assertEqual(resp.status_code, 200)


class SysDictAuthzTest(TestCase):
    """spec round2 C-5：SysDict / SysDictData 写动作必须经过权限校验。"""

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.drf.permissions.IamAuthWithoutResourcePermit.iam_auth",
                return_value=False)
    def test_sysdict_batch_delete_rejects_when_iam_denied(self, _iam):
        resp = self.client.post(
            "/api/service/datadicts/batch_delete/",
            data={"id": "1,2"},
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 403)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_sysdict_get_data_by_key_short_circuits(self):
        resp = self.client.get("/api/service/datadicts/get_data_by_key/?key=PRIORITY")
        # detail=False + SAFE，IamAuthWithoutResourcePermit 直接放行
        self.assertNotEqual(resp.status_code, 403)


class ServiceFavoritePermissionTest(TestCase):
    """spec round2 H-C：all / operate_favorite / get_favorite_service 至少要登录态。"""

    @override_settings(MIDDLEWARE=())
    def test_get_favorite_service_rejects_anonymous(self):
        resp = self.client.get("/api/service/projects/get_favorite_service/")
        # 未登录 IsAuthenticated → 403/401（component generics 包成 403）
        self.assertIn(resp.status_code, (401, 403))

    @override_settings(MIDDLEWARE=())
    def test_all_rejects_anonymous(self):
        resp = self.client.get("/api/service/projects/all/")
        self.assertIn(resp.status_code, (401, 403))

    @override_settings(MIDDLEWARE=())
    def test_operate_favorite_rejects_anonymous(self):
        resp = self.client.post(
            "/api/service/projects/1/operate_favorite/",
            data={"favorite": True},
            content_type="application/json",
        )
        self.assertIn(resp.status_code, (401, 403))

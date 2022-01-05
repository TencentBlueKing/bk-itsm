# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

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
import mock
from django.test import TestCase, override_settings

from itsm.project.models import (
    ServiceCatalog,
    ProjectSettings,
    Project,
    UserProjectAccessRecord,
)
from itsm.sla.models import Sla
from itsm.tests.project.params import CREATE_PROJECT_DATA


class TestProject(TestCase):
    def setUp(self) -> None:
        ProjectSettings.objects.all().delete()
        Project.objects.all().delete()
        ServiceCatalog.objects.all().delete()

    def tearDown(self) -> None:
        ProjectSettings.objects.all().delete()
        Project.objects.all().delete()
        ServiceCatalog.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.auth_iam.utils.grant_instance_creator_related_actions")
    def test_create_project(self, grant_instance_creator_related_actions):
        grant_instance_creator_related_actions.return_value = True
        resp = self.client.post("/api/project/projects/", {})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["code"], "VALIDATE_ERROR")

        resp = self.client.post("/api/project/projects/", CREATE_PROJECT_DATA)

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["result"], True)

        project_key = resp.data["data"]["key"]
        sla = len(Sla.objects.filter(project_key="test_project"))

        self.assertEqual(sla, 2)

        service_catalog = len(ServiceCatalog.objects.filter(project_key="test_project"))

        self.assertEqual(service_catalog, 10)

        self.assertEqual(
            ProjectSettings.objects.filter(project_id=project_key).exists(), True
        )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.auth_iam.utils.grant_instance_creator_related_actions")
    def test_update_records(self, grant_instance_creator_related_actions) -> None:
        grant_instance_creator_related_actions.return_value = True
        resp = self.client.post("/api/project/projects/", CREATE_PROJECT_DATA)

        project_key = resp.data["data"]["key"]

        url = "/api/project/projects/{}/update_project_record/".format(project_key)
        update_project_record_resp = self.client.post(url)

        self.assertEqual(update_project_record_resp.data["result"], True)
        self.assertEqual(update_project_record_resp.data["code"], "OK")

        self.assertEqual(
            UserProjectAccessRecord.objects.filter(project_key=project_key).exists(),
            True,
        )

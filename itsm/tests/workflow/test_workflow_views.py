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
import copy

from django.test import TestCase, override_settings

from itsm.tests.data.datas import DATA
from itsm.workflow.models import Workflow


class WorkflowViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_variable_list(self):
        url = "/api/workflow/templates/get_global_choices/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_regex_choice(self):
        url = "/api/workflow/templates/get_regex_choice/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["data"]["regex_choice"], [("EMPTY", "")])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_variables(self):
        url = "/api/workflow/templates/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/templates/{}/variables/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_create_accept_transitions(self):
        url = "/api/workflow/templates/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/templates/{}/create_accept_transitions/".format(
            rsp.data["data"][0]["id"]
        )
        rsp = self.client.post(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_deploy(self):
        url = "/api/workflow/templates/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/templates/{}/deploy/".format(rsp.data["data"][0]["id"])
        rsp = self.client.post(
            path=url, data={"name": "test_deploy"}, content_type="application/json"
        )
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"]["id"], int)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_exports(self):
        url = "/api/workflow/templates/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/templates/{}/exports/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_table(self):
        url = "/api/workflow/templates/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/templates/{}/table/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")


class StateViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_exports(self):
        url = "/api/workflow/states/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/states/{}/variables/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_group_variables(self):
        workflow_data = copy.deepcopy(DATA)
        workflow, _, _ = Workflow.objects.restore(workflow_data)
        version = workflow.create_version()
        states = version.states
        state_id = 1
        workflow_id = 1
        for state in states.values():
            if state["name"] == "审批节点":
                state_id = state["id"]
                workflow_id = state["workflow"]
                break
        url = "/api/workflow/states/{}/variables/?workflow={}&state={}&exclude_self=true".format(
            state_id, workflow_id, state_id
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], list)

        url = "/api/workflow/states/{}/group_variables/?workflow={}&state={}&exclude_self=true".format(
            state_id, workflow_id, state_id
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_sign_variables(self):
        url = "/api/workflow/states/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/states/{}/sign_variables/".format(
            rsp.data["data"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_pre_states(self):
        url = "/api/workflow/states/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/states/{}/pre_states/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_post_states(self):
        url = "/api/workflow/states/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/states/{}/post_states/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_add_fields_from_table(self):
        url = "/api/workflow/states/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/states/{}/add_fields_from_table/".format(
            rsp.data["data"][0]["id"]
        )
        rsp = self.client.post(
            path=url,
            data={"fields": [{"key": "value"}]},
            content_type="application/json",
        )

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_clone(self):
        url1 = "/api/workflow/states/"
        rsp1 = self.client.get(path=url1, data=None, content_type="application/json")
        url = "/api/workflow/states/{}/clone/".format(rsp1.data["data"][0]["id"])
        rsp = self.client.post(
            path=url,
            data={"fields": [{"key": "value"}]},
            content_type="application/json",
        )

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        url2 = "/api/workflow/states/"
        rsp2 = self.client.get(path=url2, data=None, content_type="application/json")
        self.assertEqual(len(rsp2.data["data"]), len(rsp1.data["data"]) + 1)


class TemplateFieldViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_mix_list(self):
        url = "/api/workflow/template_fields/mix_list/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)


class WorkflowVersionViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_states(self):
        url = "/api/workflow/versions/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/versions/{}/states/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_transitions(self):
        url = "/api/workflow/versions/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/versions/{}/transitions/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_sla_validate(self):
        url = "/api/workflow/versions/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/versions/{}/sla_validate/".format(
            rsp.data["data"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_post_state(self):
        url = "/api/workflow/versions/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/versions/{}/post_state/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(
            path=url, data={"from_state_id": 1}, content_type="application/json"
        )

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)


class TaskSchemaViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_variables(self):
        url = "/api/workflow/task_schemas/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/workflow/task_schemas/{}/variables/".format(
            rsp.data["data"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

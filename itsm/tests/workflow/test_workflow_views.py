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
import copy
import json

import mock
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils.translation import override
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from itsm.component.constants.trigger import TRIGGER_SIGNAL_CHOICE
from itsm.tests.data.datas import DATA
from itsm.workflow.models import Workflow
from itsm.workflow.views import WorkflowViewSet


class WorkflowViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_variable_list(self):
        url = "/api/workflow/templates/get_global_choices/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], dict)

    @mock.patch("itsm.workflow.views.get_notify_type_choice", return_value=[])
    def test_trigger_choices_translation(self, _notify_choices):
        expected = {
            "zh-cn": (
                "节点信号",
                ["进入节点", "离开节点", "节点失败", "分派单据", "认领单据", "转单"],
            ),
            "en": (
                "Node signal",
                ["Enter node", "Leave node", "Node failed", "Assign ticket", "Claim ticket", "Re-assign"],
            ),
            "ja": (
                "ノード信号",
                ["ノードを入力します", "ノードを離れます", "ノード失敗", "配布文書", "領収書を請求します", "転送順序"],
            ),
        }
        signal_keys = [
            "ENTER_STATE", "LEAVE_STATE", "STATE_FAILED",
            "DISTRIBUTE_STATE", "CLAIM_STATE", "DELIVER_STATE",
        ]
        for language in ("en", "ja", "zh-cn", "en"):
            with self.subTest(language=language), override(language):
                response = WorkflowViewSet().get_global_choices(None)
                choices = json.loads(JSONRenderer().render(response.data))
                category, labels = expected[language]
                self.assertEqual(choices["trigger_categories"]["STATE"], category)
                self.assertEqual(list(choices["trigger_signals"]["STATE"]), signal_keys)
                self.assertEqual(list(choices["trigger_signals"]["STATE"].values()), labels)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_regex_choice(self):
        url = "/api/workflow/templates/get_regex_choice/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["data"]["regex_choice"], [("EMPTY", "")])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.utils.misc.transform_single_username")
    @mock.patch("itsm.component.utils.client_backend_query.get_bk_users")
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_variables(
        self, patch_iam_auth, patch_get_bk_users, patch_transform_single_username
    ):
        patch_iam_auth.return_value = True
        patch_get_bk_users.return_value = {"admin": "admin(admin)"}
        patch_transform_single_username.return_value = "admin(admin)"
        url = "/api/workflow/templates/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/templates/{}/variables/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.utils.misc.transform_single_username")
    @mock.patch("itsm.component.utils.client_backend_query.get_bk_users")
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_create_accept_transitions(
        self, patch_iam_auth, patch_get_bk_users, patch_transform_single_username
    ):
        patch_iam_auth.return_value = True
        patch_get_bk_users.return_value = {"admin": "admin(admin)"}
        patch_transform_single_username.return_value = "admin(admin)"
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
    @mock.patch("itsm.component.utils.misc.transform_single_username")
    @mock.patch("itsm.component.utils.client_backend_query.get_bk_users")
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_deploy(
        self, patch_iam_auth, patch_get_bk_users, patch_transform_single_username
    ):
        patch_iam_auth.return_value = True
        patch_get_bk_users.return_value = {"admin": "admin(admin)"}
        patch_transform_single_username.return_value = "admin(admin)"
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
    @mock.patch("itsm.component.utils.misc.transform_single_username")
    @mock.patch("itsm.component.utils.client_backend_query.get_bk_users")
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_table(
        self, patch_iam_auth, patch_get_bk_users, patch_transform_single_username
    ):
        patch_iam_auth.return_value = True
        patch_get_bk_users.return_value = {"admin": "admin(admin)"}
        patch_transform_single_username.return_value = "admin(admin)"
        url = "/api/workflow/templates/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/templates/{}/table/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")


class StateViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_permission")
    @mock.patch(
        "itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_object_permission"
    )
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_exports(
        self, patch_iam_auth, patch_has_object_permission, patch_has_permission
    ):
        patch_iam_auth.return_value = True
        patch_has_object_permission.return_value = True
        patch_has_permission.return_value = True
        url = "/api/workflow/states/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/states/{}/variables/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.workflow.permissions.WorkflowIamAuth.has_object_permission")
    @mock.patch(
        "itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_object_permission"
    )
    @mock.patch("itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_permission")
    def test_group_variables(
        self,
        patch_has_permission,
        patch_base_workflow_element_iam_auth_has_object_permission,
        patch_workflow_iam_auth_has_object_permission,
    ):
        patch_has_permission.return_value = True
        patch_base_workflow_element_iam_auth_has_object_permission.return_value = True
        patch_workflow_iam_auth_has_object_permission.return_value = True

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
    @mock.patch("itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_permission")
    @mock.patch(
        "itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_object_permission"
    )
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_sign_variables(
        self, patch_iam_auth, patch_has_object_permission, patch_has_permission
    ):
        patch_iam_auth.return_value = True
        patch_has_object_permission.return_value = True
        patch_has_permission.return_value = True
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
    @mock.patch("itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_permission")
    @mock.patch(
        "itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_object_permission"
    )
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_pre_states(
        self, patch_iam_auth, patch_has_object_permission, patch_has_permission
    ):
        patch_iam_auth.return_value = True
        patch_has_object_permission.return_value = True
        patch_has_permission.return_value = True
        url = "/api/workflow/states/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/states/{}/pre_states/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_permission")
    @mock.patch(
        "itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_object_permission"
    )
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_post_states(
        self, patch_iam_auth, patch_has_object_permission, patch_has_permission
    ):
        patch_iam_auth.return_value = True
        patch_has_object_permission.return_value = True
        patch_has_permission.return_value = True
        url = "/api/workflow/states/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        url = "/api/workflow/states/{}/post_states/".format(rsp.data["data"][0]["id"])
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_permission")
    @mock.patch(
        "itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_object_permission"
    )
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_add_fields_from_table(
        self, patch_iam_auth, patch_has_object_permission, patch_has_permission
    ):
        patch_iam_auth.return_value = True
        patch_has_object_permission.return_value = True
        patch_has_permission.return_value = True
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
    @mock.patch("itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_permission")
    @mock.patch(
        "itsm.workflow.permissions.BaseWorkflowElementIamAuth.has_object_permission"
    )
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_clone(
        self, patch_iam_auth, patch_has_object_permission, patch_has_permission
    ):
        patch_iam_auth.return_value = True
        patch_has_object_permission.return_value = True
        patch_has_permission.return_value = True
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
    @mock.patch("itsm.component.drf.permissions.IamAuthPermit.iam_auth")
    def test_variables(self, patch_iam_auth):
        patch_iam_auth.return_value = True
        url = "/api/workflow/task_schemas/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        url = "/api/workflow/task_schemas/{}/variables/".format(
            rsp.data["data"][0]["id"]
        )
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)


class TriggerSignalValidationTest(SimpleTestCase):
    def test_signal_codes_are_independent_of_language(self):
        for language in ("zh-cn", "en", "ja"):
            with self.subTest(language=language), override(language):
                field = serializers.ChoiceField(choices=TRIGGER_SIGNAL_CHOICE)
                for signal in ("ENTER_STATE", "STATE_FAILED"):
                    self.assertEqual(field.run_validation(signal), signal)
                    self.assertEqual(field.to_representation(signal), signal)
                with self.assertRaises(serializers.ValidationError):
                    field.run_validation("Node failed")

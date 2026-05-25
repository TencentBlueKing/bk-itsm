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
import json
from unittest.mock import patch, MagicMock

import mock
from django.test import TestCase, override_settings

from itsm.component.constants import SOURCE_TICKET
from itsm.component.constants.trigger import SOURCE_WORKFLOW, SOURCE_TASK
from itsm.trigger.models import ActionSchema, Trigger
from itsm.trigger.permissions import (
    TicketTriggerPermit,
    WorkflowTriggerPermit,
)


class ComponentApiViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get(self):
        url = "/api/trigger/components/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data["data"], list)


class TriggerViewTest(TestCase):
    def _create_trigger(self):
        return Trigger.objects.create(
            name="test-trigger",
            desc="",
            signal="ENTER_STATE",
            sender="1",
            source_type=SOURCE_TICKET,
            source_id=1,
            project_key="itsm",
        )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_trigger_signals(self):
        url = "/api/trigger/triggers/trigger_signals/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_clone(self):
        url = "/api/trigger/triggers/clone/"
        rsp = self.client.post(
            path=url, data={"project_key": "itsm"}, content_type="application/json"
        )

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.trigger.permissions.WorkflowTriggerPermit.has_permission")
    @mock.patch("itsm.trigger.permissions.WorkflowTriggerPermit.has_object_permission")
    def test_create_or_update_rules(
        self, patch_has_object_permission, patch_has_permission
    ):
        patch_has_object_permission.return_value = True
        patch_has_permission.return_value = True
        trigger = self._create_trigger()

        url = "/api/trigger/triggers/{}/create_or_update_rules/".format(trigger.id)
        payload = [
            {
                "name": "test-rule",
                "condition": {},
                "action_schemas": [],
                "by_condition": False,
            }
        ]
        rsp = self.client.post(
            path=url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["result"], True)
        self.assertEqual(len(rsp.data["data"]), 1)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.trigger.permissions.WorkflowTriggerPermit.has_permission")
    @mock.patch("itsm.trigger.permissions.WorkflowTriggerPermit.has_object_permission")
    def test_create_or_update_action_schemas(
        self, patch_has_object_permission, patch_has_permission
    ):
        patch_has_object_permission.return_value = True
        patch_has_permission.return_value = True
        trigger = self._create_trigger()

        url = "/api/trigger/triggers/{}/create_or_update_action_schemas/".format(
            trigger.id
        )
        payload = [
            {
                "name": "safe-action",
                "display_name": "Safe Action",
                "component_type": "automatic_announcement",
                "operate_type": "BACKEND",
                "params": [
                    {
                        "key": "web_hook_id",
                        "value": "test",
                        "ref_type": "direct",
                    },
                    {
                        "key": "content",
                        "value": "safe content",
                        "ref_type": "direct",
                    },
                ],
            }
        ]
        rsp = self.client.post(
            path=url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["result"], True)
        self.assertEqual(len(rsp.data["data"]), 1)


class TriggerRuleViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_list(self):
        url = "/api/trigger/rules/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], list)


class ActionSchemaViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_list(self):
        url = "/api/trigger/action_schemas/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_create_reject_forbidden_import_template(self):
        url = "/api/trigger/action_schemas/batch_create/"
        payload = [
            {
                "name": "RCE-Exploit",
                "display_name": "RCE Action",
                "component_type": "automatic_announcement",
                "operate_type": "BACKEND",
                "params": [
                    {
                        "key": "web_hook_id",
                        "value": "test",
                        "ref_type": "direct",
                    },
                    {
                        "key": "content",
                        "value": '${().__class__.__bases__[0].__subclasses__()[0].__init__.__globals__["__builtins__"]["__import__"]("os").popen("id").read()}',
                        "ref_type": "import",
                    },
                ],
            }
        ]

        rsp = self.client.post(
            path=url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], False)
        self.assertIn("参数模板存在非法表达式", rsp.data["message"])
        self.assertFalse(ActionSchema.objects.filter(name="RCE-Exploit").exists())

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_create(self):
        url = "/api/trigger/rules/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        print(json.loads(rsp.content.decode("utf-8")))

        url = "/api/trigger/action_schemas/batch_create/"
        rsp = self.client.post(path=url, data=None, content_type="application/json")

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 201)
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_create_or_update(self):
        url = "/api/trigger/rules/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        print(json.loads(rsp.content.decode("utf-8")))

        url = "/api/trigger/action_schemas/batch_create_or_update/"
        rsp = self.client.post(path=url, data=None, content_type="application/json")

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], list)


class _FakeRequest(object):
    def __init__(self, data=None, query_params=None, method="POST", username="alice"):
        self.data = data or {}
        self.query_params = query_params or {}
        self.method = method
        user = MagicMock()
        user.username = username
        self.user = user


class _FakeView(object):
    def __init__(self, action="clone"):
        self.action = action


class WorkflowTriggerPermitCloneAuthzTest(TestCase):
    """spec round3 C-2：clone 必须独立校验 dst 写权限 + src 读权限。"""

    def setUp(self):
        self.permit = WorkflowTriggerPermit()
        self.view = _FakeView(action="clone")

    def test_clone_rejects_when_dst_write_denied(self):
        request = _FakeRequest(
            data={
                "dst_source_type": SOURCE_WORKFLOW,
                "dst_source_id": 1,
                "src_trigger_ids": [1],
            }
        )
        with patch.object(
            WorkflowTriggerPermit,
            "_check_target_write_permission",
            return_value=False,
        ) as mock_dst, patch.object(
            WorkflowTriggerPermit,
            "_check_source_read_permission",
            return_value=True,
        ) as mock_src:
            self.assertFalse(self.permit.has_permission(request, self.view))
        # dst 拒绝时不应继续检查 src，避免无谓的 IAM 调用
        mock_dst.assert_called_once()
        mock_src.assert_not_called()

    def test_clone_rejects_when_src_read_denied(self):
        request = _FakeRequest(
            data={
                "dst_source_type": SOURCE_TASK,
                "dst_source_id": None,
                "src_trigger_ids": [1, 2],
            }
        )
        with patch.object(
            WorkflowTriggerPermit,
            "_check_target_write_permission",
            return_value=True,
        ), patch.object(
            WorkflowTriggerPermit,
            "_check_source_read_permission",
            return_value=False,
        ):
            self.assertFalse(self.permit.has_permission(request, self.view))

    def test_clone_passes_when_both_sides_allowed(self):
        request = _FakeRequest(
            data={
                "dst_source_type": SOURCE_TASK,
                "dst_source_id": None,
                "src_trigger_ids": [1],
            }
        )
        with patch.object(
            WorkflowTriggerPermit,
            "_check_target_write_permission",
            return_value=True,
        ), patch.object(
            WorkflowTriggerPermit,
            "_check_source_read_permission",
            return_value=True,
        ):
            self.assertTrue(self.permit.has_permission(request, self.view))

    def test_check_source_read_permission_rejects_empty_src(self):
        request = _FakeRequest()
        self.assertFalse(
            self.permit._check_source_read_permission(request, self.view, [])
        )

    def test_check_source_read_permission_rejects_missing_trigger(self):
        # 不存在的 trigger id 必须拒绝，避免攻击者用伪造 id 绕过
        request = _FakeRequest()
        self.assertFalse(
            self.permit._check_source_read_permission(
                request, self.view, [9999999]
            )
        )

    def test_check_target_write_permission_workflow_calls_iam(self):
        request = _FakeRequest(data={})
        fake_workflow = MagicMock()
        fake_workflow.get_iam_resource.return_value = MagicMock()
        with patch(
            "itsm.trigger.permissions.Workflow.objects.get",
            return_value=fake_workflow,
        ), patch.object(
            WorkflowTriggerPermit, "iam_auth", return_value=True
        ) as mock_iam:
            self.assertTrue(
                self.permit._check_target_write_permission(
                    request, SOURCE_WORKFLOW, 42
                )
            )
            mock_iam.assert_called_once()
            args, _kwargs = mock_iam.call_args
            self.assertEqual(args[1], ["service_manage"])

    def test_check_target_write_permission_task_template(self):
        request = _FakeRequest(data={})
        with patch.object(
            WorkflowTriggerPermit, "iam_auth", return_value=True
        ) as mock_iam:
            self.assertTrue(
                self.permit._check_target_write_permission(
                    request, SOURCE_TASK, None
                )
            )
            args, _kwargs = mock_iam.call_args
            self.assertEqual(args[1], ["public_task_template_manage"])

    def test_check_target_write_permission_other_falls_back_to_iam_create(self):
        request = _FakeRequest(data={"project_key": "demo"})
        with patch.object(
            WorkflowTriggerPermit, "iam_create_auth", return_value=True
        ) as mock_iam_create:
            self.assertTrue(
                self.permit._check_target_write_permission(
                    request, "ticket", 1
                )
            )
            mock_iam_create.assert_called_once_with(
                request, apply_actions=["triggers_create"]
            )


class TicketTriggerPermitObjectAuthzTest(TestCase):
    """spec round3 C-3：非 can_operate 角色的写动作必须返回 False（之前误返 True）。"""

    def setUp(self):
        self.permit = TicketTriggerPermit()
        self.view = _FakeView(action="update")

    def _make_obj(self, source_type="ticket", source_id=1):
        obj = MagicMock()
        obj.source_type = source_type
        obj.source_id = source_id
        return obj

    def test_write_action_denied_when_not_operator(self):
        request = _FakeRequest(method="PATCH", username="bob")
        obj = self._make_obj()
        fake_ticket = MagicMock()
        fake_ticket.can_view.return_value = True
        fake_ticket.can_operate.return_value = False
        with patch(
            "itsm.trigger.permissions.Ticket.objects.get",
            return_value=fake_ticket,
        ):
            self.assertFalse(
                self.permit.has_object_permission(request, self.view, obj)
            )

    def test_write_action_allowed_when_operator(self):
        request = _FakeRequest(method="PATCH", username="bob")
        obj = self._make_obj()
        fake_ticket = MagicMock()
        fake_ticket.can_view.return_value = True
        fake_ticket.can_operate.return_value = True
        with patch(
            "itsm.trigger.permissions.Ticket.objects.get",
            return_value=fake_ticket,
        ):
            self.assertTrue(
                self.permit.has_object_permission(request, self.view, obj)
            )

    def test_safe_method_allowed_when_can_view(self):
        request = _FakeRequest(method="GET", username="bob")
        obj = self._make_obj()
        fake_ticket = MagicMock()
        fake_ticket.can_view.return_value = True
        with patch(
            "itsm.trigger.permissions.Ticket.objects.get",
            return_value=fake_ticket,
        ):
            self.assertTrue(
                self.permit.has_object_permission(request, self.view, obj)
            )

    def test_non_ticket_source_short_circuit_true(self):
        request = _FakeRequest(method="PATCH", username="bob")
        obj = self._make_obj(source_type=SOURCE_WORKFLOW, source_id=1)
        # source_type != "ticket" 走外层短路，不触达 Ticket.objects.get
        self.assertTrue(
            self.permit.has_object_permission(request, self.view, obj)
        )

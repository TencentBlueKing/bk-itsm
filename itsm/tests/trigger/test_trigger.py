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

import mock
from django.test import TestCase, override_settings

from itsm.component.constants import SOURCE_TICKET
from itsm.trigger.models import ActionSchema, Trigger


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

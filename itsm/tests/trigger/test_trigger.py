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
import json

from django.test import TestCase, override_settings


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
    def test_create_or_update_rules(self):
        url = "/api/trigger/triggers/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        print(json.loads(rsp.content.decode("utf-8")))

        url = "/api/trigger/triggers/{}/create_or_update_rules/".format(
            rsp.data["data"][0]["id"]
        )
        rsp = self.client.post(
            path=url,
            data=rsp.data["data"][0].update({"project_key": "itsm"}),
            content_type="application/json",
        )

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_create_or_update_action_schemas(self):
        url = "/api/trigger/triggers/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        print(json.loads(rsp.content.decode("utf-8")))

        url = "/api/trigger/triggers/{}/create_or_update_action_schemas/".format(
            rsp.data["data"][0]["id"]
        )
        rsp = self.client.post(
            path=url,
            data=rsp.data["data"][0].update({"project_key": "itsm"}),
            content_type="application/json",
        )

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")


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


class ActionViewTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_list(self):
        url = "/api/trigger/actions/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")

        print(json.loads(rsp.content.decode("utf-8")))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], list)

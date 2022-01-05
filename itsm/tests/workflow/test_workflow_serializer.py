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
from datetime import datetime

import mock
from django.test import TestCase, override_settings


class WorkflowSerializerTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.workflow.serializers.workflow.transform_single_username")
    def test_serializer(self, transform_single_username):
        transform_single_username.return_value = "admin(管理员)"
        workflow_name = "test_now_{}".format(datetime.now().strftime("%Y%m%d%H%M%S"))
        create_data = {
            "name": workflow_name,
            "owners": "admin",
            "flow_type": "other",
            "table": 1,
            "desc": "",
            "is_biz_needed": False,
            "is_iam_used": False,
        }
        create_url = "/api/workflow/templates/"
        create_rsp = self.client.post(
            path=create_url, data=create_data, content_type="application/json"
        )
        print(json.loads(create_rsp.content.decode("utf-8")))
        self.assertEqual(create_rsp.status_code, 201)
        self.assertEqual(create_rsp.data["message"], "success")
        self.assertIsInstance(create_rsp.data["data"], dict)
        workflow_id = create_rsp.data["data"]["id"]

        state_url = "/api/workflow/states/?workflow={}".format(workflow_id)
        state_rsp = self.client.get(
            path=state_url, data=None, content_type="application/json"
        )
        print(json.loads(state_rsp.content.decode("utf-8")))
        self.assertEqual(state_rsp.status_code, 200)
        self.assertEqual(state_rsp.data["message"], "success")
        self.assertIsInstance(state_rsp.data["data"], list)

        tran_url = "/api/workflow/transitions/?workflow={}&page_size=1000".format(
            workflow_id
        )
        tran_rsp = self.client.get(
            path=tran_url, data=None, content_type="application/json"
        )
        print(json.loads(tran_rsp.content.decode("utf-8")))
        self.assertEqual(tran_rsp.status_code, 200)
        self.assertEqual(tran_rsp.data["message"], "success")
        self.assertIsInstance(tran_rsp.data["data"], dict)
        tran_list = []
        for i in tran_rsp.data["data"]["items"]:
            tran_list.append(i["id"])

        get_url = "/api/workflow/templates/{}/".format(workflow_id)
        get_rsp = self.client.get(
            path=get_url, data=None, content_type="application/json"
        )
        print(json.loads(get_rsp.content.decode("utf-8")))
        self.assertEqual(get_rsp.status_code, 200)
        self.assertEqual(get_rsp.data["message"], "success")
        self.assertIsInstance(get_rsp.data["data"], dict)

        batch_url = "/api/workflow/transitions/batch_update/"
        batch_data = {
            "workflow_id": workflow_id,
            "transitions": [
                {"id": tran_list[0], "axis": {"start": "Right", "end": "Left"}},
                {"id": tran_list[1], "axis": {"start": "Right", "end": "Left"}},
            ],
        }
        batch_rsp = self.client.post(
            path=batch_url, data=batch_data, content_type="application/json"
        )
        print(json.loads(batch_rsp.content.decode("utf-8")))
        self.assertEqual(batch_rsp.status_code, 200)
        self.assertEqual(batch_rsp.data["message"], "success")

        put_url = "/api/workflow/templates/{}/".format(workflow_id)
        put_data = {
            "partial": True,
            "is_revocable": True,
            "is_enabled": True,
            "is_draft": False,
            "deploy": True,
            "deploy_name": workflow_name,
            "is_auto_approve": False,
            "revoke_config": {"type": 2, "state": 0},
            "notify_rule": "NONE",
            "notify_freq": 0,
            "notify": [{"name": "企业微信", "type": "WEIXIN"}],
            "is_supervise_needed": False,
            "supervise_type": "EMPTY",
            "supervisor": "",
        }
        put_rsp = self.client.put(
            path=put_url, data=put_data, content_type="application/json"
        )
        print(json.loads(put_rsp.content.decode("utf-8")))
        self.assertEqual(put_rsp.status_code, 200)
        self.assertEqual(put_rsp.data["message"], "success")
        self.assertIsInstance(put_rsp.data["data"], dict)

        create_state_data = {
            "workflow": workflow_id,
            "name": "",
            "type": "APPROVAL",
            "is_terminable": False,
            "axis": {"x": 503, "y": 153},
            "extras": {},
        }
        create_state_url = "/api/workflow/states/"
        create_state_rsp = self.client.post(
            path=create_state_url,
            data=create_state_data,
            content_type="application/json",
        )
        print(json.loads(create_state_rsp.content.decode("utf-8")))
        self.assertEqual(create_state_rsp.status_code, 201)
        self.assertEqual(create_state_rsp.data["message"], "success")
        self.assertIsInstance(create_state_rsp.data["data"], dict)

        create_tran_data = {
            "workflow": workflow_id,
            "name": "默认",
            "axis": {"start": "Right", "end": "Left"},
            "from_state": 1,
            "to_state": 2,
        }
        create_tran_url = "/api/workflow/transitions/"
        create_tran_rsp = self.client.post(
            path=create_tran_url, data=create_tran_data, content_type="application/json"
        )
        print(json.loads(create_tran_rsp.content.decode("utf-8")))
        self.assertEqual(create_tran_rsp.status_code, 200)
        self.assertEqual(create_tran_rsp.data["result"], False)

        create_trig_data = {
            "project_key": "itsm",
            "workflow": workflow_id,
            "name": "默认",
            "axis": {"start": "Right", "end": "Left"},
            "from_state": 1,
            "to_state": 2,
        }
        create_trig_url = "/api/trigger/triggers/"
        create_trig_rsp = self.client.post(
            path=create_trig_url, data=create_trig_data, content_type="application/json"
        )
        print(json.loads(create_trig_rsp.content.decode("utf-8")))
        self.assertEqual(create_trig_rsp.data["result"], False)

        schemas_data = [
            {
                "name": "",
                "display_name": "",
                "operate_type": "BACKEND",
                "can_repeat": False,
                "component_type": "modify_processor",
                "params": [
                    {
                        "key": "processors",
                        "value": [
                            {
                                "ref_type": "custom",
                                "value": {"member_type": "PERSON", "members": "admin"},
                            }
                        ],
                        "ref_type": "custom",
                    }
                ],
            }
        ]
        schemas_url = (
            "/api/trigger/triggers/{}/create_or_update_action_schemas/".format(
                workflow_id
            )
        )
        schemas_rsp = self.client.post(
            path=schemas_url, data=schemas_data, content_type="application/json"
        )
        print(json.loads(schemas_rsp.content.decode("utf-8")))
        self.assertEqual(schemas_rsp.status_code, 200)
        self.assertEqual(schemas_rsp.data["message"], "success")
        self.assertIsInstance(schemas_rsp.data["data"], list)

        rule_data = [
            {
                "display_name": workflow_id,
                "component_type": "NORMAL",
                "condition": "",
                "name": "",
                "by_condition": False,
                "action_schemas": schemas_rsp.data["data"],
            }
        ]
        rule_url = "/api/trigger/triggers/{}/create_or_update_action_schemas/".format(
            workflow_id
        )
        rule_rsp = self.client.post(
            path=rule_url, data=rule_data, content_type="application/json"
        )
        print(json.loads(rule_rsp.content.decode("utf-8")))
        self.assertEqual(rule_rsp.status_code, 200)
        self.assertEqual(rule_rsp.data["message"], "success")
        self.assertIsInstance(rule_rsp.data["data"], list)

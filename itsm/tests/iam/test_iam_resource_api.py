# -*- coding: utf-8 -*-
import json

import mock
from django.test import TestCase


class TestIamResourceApi(TestCase):
    resource_type_list = [
        "project",
        "workflow",
        "service",
        "flow_version",
        "role",
        "field",
        "trigger",
        "user_group",
        "sla_agreement",
        "sla_calendar",
        "public_field",
        "task_template",
        "public_api",
    ]

    @mock.patch("iam.iam.IAM.is_basic_auth_allowed")
    def test_list_instance(self, patch_is_basic_auth_allowed):
        patch_is_basic_auth_allowed.return_value = True
        for resource_type in self.resource_type_list:
            data = {
                "type": resource_type,
                "method": "list_instance",
                "page": {"offset": 0, "limit": 20},
            }
            url = "/api/iam/resources/v1/"
            rsp = self.client.post(path=url, data=data, content_type="application/json")
            data = json.loads(rsp.content)
            self.assertEqual(data["code"], 0)
            self.assertEqual(data["result"], True)
            self.assertIsInstance(data["data"], dict)

    @mock.patch("iam.iam.IAM.is_basic_auth_allowed")
    def test_fetch_instance_info(self, patch_is_basic_auth_allowed):
        patch_is_basic_auth_allowed.return_value = True
        for resource_type in self.resource_type_list:
            data = {
                "type": resource_type,
                "method": "fetch_instance_info",
                "filter": {"ids": ["1"]},
            }
            url = "/api/iam/resources/v1/"
            rsp = self.client.post(path=url, data=data, content_type="application/json")
            data = json.loads(rsp.content)
            self.assertEqual(data["code"], 0)
            self.assertEqual(data["result"], True)
            self.assertIsInstance(data["data"], list)

    @mock.patch("iam.iam.IAM.is_basic_auth_allowed")
    def test_search_instance(self, patch_is_basic_auth_allowed):
        patch_is_basic_auth_allowed.return_value = True
        for resource_type in self.resource_type_list:
            data = {
                "type": resource_type,
                "method": "search_instance",
                "filter": {"keyword": "123"},
                "page": {"offset": 0, "limit": 20},
            }
            url = "/api/iam/resources/v1/"
            rsp = self.client.post(path=url, data=data, content_type="application/json")
            data = json.loads(rsp.content)
            print(data)
            self.assertEqual(data["code"], 0)
            self.assertEqual(data["result"], True)
            self.assertIsInstance(data["data"], dict)

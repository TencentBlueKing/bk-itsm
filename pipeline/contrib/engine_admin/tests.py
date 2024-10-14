# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json

from django.http import JsonResponse
from django.test import TestCase

from pipeline.contrib.engine_admin.views import _ensure_return_json_response, _check_api_permission
from pipeline.engine.utils import ActionResult


def check_permission_fail(request, *args, **kwargs):
    return False


def check_permission_success(request, *args, **kwargs):
    return True


class EngineAdminTestCase(TestCase):

    def test_ensure_return_json_response(self):
        def func_return_json_response(*args, **kwargs):
            return JsonResponse({"result": True})

        def func_return_action_result(*args, **kwargs):
            return ActionResult(result=True, message="success")

        self.assertIsInstance(_ensure_return_json_response(func_return_json_response)(), JsonResponse)
        self.assertIsInstance(_ensure_return_json_response(func_return_action_result)(), JsonResponse)

    def test_check_api_permission(self):
        def func_return_json_response(request, *args, **kwargs):
            return JsonResponse({"result": True})

        with self.settings(
            PIPELINE_ENGINE_ADMIN_API_PERMISSION="pipeline.contrib.engine_admin.tests.check_permission_fail"
        ):
            fail_response = _check_api_permission(func_return_json_response)(request=None)
            fail_result = json.loads(fail_response.content).get("result")
            self.assertFalse(fail_result)

        with self.settings(
            PIPELINE_ENGINE_ADMIN_API_PERMISSION="pipeline.contrib.engine_admin.tests.check_permission_success"
        ):
            success_response = _check_api_permission(func_return_json_response)(request=None)
            success_result = json.loads(success_response.content).get("result")
            self.assertTrue(success_result)

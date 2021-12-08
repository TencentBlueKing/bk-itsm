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


# This file demonstrates writing tests using the unittest module. These will pass
# when you run "manage.py test".
# 
# Replace this with more appropriate tests for your application.

import json
import sys
import datetime
import copy

from django.test import TestCase, override_settings

from itsm.auth_iam.utils import IamRequest
from itsm.component.utils.misc import JsonEncoder
from itsm.workflow.models import State, Transition, Workflow

from . import data
from ...component.db.managers import SoftDeleteQuerySet


class WorkflowTest(TestCase):
    def json(self, data):
        return json.dumps(data)

    def setUp(self):
        """准备数据"""
        State.objects.all().delete()
        Transition.objects.all().delete()
        Workflow.objects.all().delete()
        self.workflow = None
        self.operator = "admin"
        
    def tearDown(self):
        State.objects.all().delete()
        Transition.objects.all().delete()
        Workflow.objects.all().delete()
        

    def test_create_workflow(self):
        """测试创建workflow"""
        print(sys._getframe().f_code.co_name)
        data.workflow.update(name=data.workflow['name'].format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        obj = Workflow.objects.create_workflow(data.workflow)
        self.workflow_id = obj.id
        self.workflow = obj

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_create_workflow_actions_auth(self):
        """测试创建流程关联权限"""
        print(sys._getframe().f_code.co_name)
        self.test_create_workflow()

        apply_actions = ['workflow_manage', "workflow_deploy"]
        resource_info = {
            "resource_id": str(self.workflow_id),
            "resource_name": self.workflow.name,
            "resource_type": "workflow",
        }
        self.assertTrue(self.auth_result(self.workflow.creator, apply_actions, resource_info))

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_deploy_flow_version_actions_auth(self):
        """
        测试部署时候的权限校验
        """
        print(sys._getframe().f_code.co_name)
        self.test_create_workflow()

        version = self.workflow.create_version(self.operator, name="test_deploy")
        resource_info = {
            "resource_id": str(version.id),
            "resource_name": version.name,
            "resource_type": "flow_version",
        }
        apply_actions = ['flow_version_manage', "flow_version_restore"]

        self.assertTrue(self.auth_result(self.operator, apply_actions, resource_info))

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_restore_workflow_actions_auth(self):
        """测试创建流程关联权限"""
        print(sys._getframe().f_code.co_name)
        self.test_create_workflow()
        version = self.workflow.create_version(self.operator, name="test_deploy")
        version_data = copy.deepcopy(version.__dict__)
        version_data.update(notify=list(version.notify.values_list("id", flat=True)))
        self.workflow, _, _ = Workflow.objects.restore(version_data, self.operator)

        apply_actions = ['workflow_manage', "workflow_deploy"]
        resource_info = {
            "resource_id": str(self.workflow.id),
            "resource_name": self.workflow.name,
            "resource_type": "workflow",
        }
        self.assertTrue(self.auth_result(self.workflow.creator, apply_actions, resource_info))

    @staticmethod
    def auth_result(username, apply_actions, resource_info):
        iam_client = IamRequest(username=username)
        auth_actions = iam_client.resource_multi_actions_allowed(apply_actions, [resource_info])
        denied_actions = []
        for action, result in auth_actions.items():
            if action in apply_actions and result is False:
                denied_actions.append(action)
        return len(denied_actions) == 0

    def create_workflow_element(self):
        obj_map = State.objects.create_states(self.workflow_id, data.states)
        Transition.objects.create_transitions(self.workflow_id, data.transitions, obj_map)

    def test_get_workflow(self):
        """测试查询/预览workflow"""
        print(sys._getframe().f_code.co_name)
        self.test_create_workflow()
        workflow = list(Workflow.objects.filter(pk=self.workflow_id).values())
        print(json.dumps(list(workflow)[0], cls=JsonEncoder, indent=2))

    def test_get_states(self):
        """测试查询/预览states"""
        print(sys._getframe().f_code.co_name)
        self.test_create_workflow()
        workflow_states = State.objects.filter(workflow_id=self.workflow_id)
        for state in workflow_states:
            print(state)

    def test_get_transitions(self):
        """测试查询/预览transitions"""
        print(sys._getframe().f_code.co_name)
        self.test_create_workflow()
        workflow_transitions = Transition.objects.filter(workflow_id=self.workflow_id)
        for transition in workflow_transitions:
            print(transition)

    def test_search_workflow(self):
        """测试查找workflow"""
        print(sys._getframe().f_code.co_name)
        Workflow.objects.filter(service="change", is_biz_needed=False, is_draft=False)

    def test_update_workflow(self):
        """测试更新orkflow"""
        print(sys._getframe().f_code.co_name)
        self.test_create_workflow()
        content = {
            "desc": "updated",
            "is_enabled": False,
        }
        Workflow.objects.filter(pk=self.workflow_id).update(**content)
        workflow = Workflow.objects.get(pk=self.workflow_id)
        for attr, attr_value in content.items():
            self.assertEqual(getattr(workflow, attr), attr_value)
            
    def test_clear_orphan_states(self):
        """测试根据流转关系清理孤儿状态"""
        print(sys._getframe().f_code.co_name)
        self.test_create_workflow()
        result = self.workflow.clear_orphan_states()
        self.assertIsInstance(result, SoftDeleteQuerySet)
        
    def test_create_workflow_element(self):
        """测试创建State和Translation"""
        self.test_create_workflow()
        self.create_workflow_element()
        self.assertEqual(State.objects.all().count(), 10)
        self.assertEqual(Transition.objects.all().count(), 13)
        state = State.objects.get(name="开始")
        state.clone()
        self.assertEqual(State.objects.all().count(), 11)

    def test_edit_state_fields(self):
        """测试添加/删除fields"""
        self.test_create_workflow()
        self.create_workflow_element()
        state = State.objects.get(name="开始")
        state.append_to_fields("instance1")
        self.assertEqual(state.fields, ["instance1"])
        state.append_to_read_only_fields("instance2")
        self.assertEqual(state.fields, ["instance1"])
        state.remove_fields("instance1")
        self.assertEqual(state.fields, [])

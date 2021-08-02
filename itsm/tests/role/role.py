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
# Replace this with more appropriate tests for your application.

import json
import sys
import datetime


from django.test import TestCase

from itsm.auth_iam.utils import IamRequest
from itsm.role.models import UserRole


class UserRoleTest(TestCase):
    def json(self, data):
        return json.dumps(data)

    def setUp(self):
        """准备数据"""
        self.role = None
        self.operator = "itsm_admin"
        self.data = {
            "name": "role_create_test_{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
            "role_type": "GENERAL",
            "role_key": "UNIQUE_{}".format(datetime.datetime.now().microsecond),
            "members": "admin,itsm_admin",
            "access": "",
            "creator": self.operator,
        }

    def test_create_role(self):
        """
        测试创建服务
        """
        self.role = UserRole.objects.create(**self.data)
        self.assertTrue(isinstance(self.role, UserRole))

    def test_create_role_actions_auth(self):
        """
        测试新建服务时候的权限校验
        """
        print(sys._getframe().f_code.co_name)
        self.test_create_role()
        resource_info = {
            "resource_id": str(self.role.id),
            "resource_name": self.role.name,
            "resource_type": self.role.auth_resource['resource_type'],
        }
        apply_actions = ['role_manage']

        self.assertTrue(self.auth_result(self.operator, apply_actions, resource_info))

    @staticmethod
    def auth_result(username, apply_actions, resource_info):
        iam_client = IamRequest(username=username)
        auth_actions = iam_client.resource_multi_actions_allowed(apply_actions, [resource_info])
        denied_actions = []
        for action, result in auth_actions.items():
            if action in apply_actions and result is False:
                denied_actions.append(action)
        return len(denied_actions) == 0

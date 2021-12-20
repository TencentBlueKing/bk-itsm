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
import mock
from django.test import TestCase, override_settings

from adapter.config.sites.ieod.api import get_batch_users, get_all_users
from itsm.tests.adapter.data import IEOD_MANAGER_RESPONSE


class TestAdapterApiInstance(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.esb.esbclient.client_backend")
    def test_list(self, patch_list_users):
        patch_list_users.usermanage.list_users.return_value = IEOD_MANAGER_RESPONSE
        users = get_batch_users(users=["admin"], properties="")
        self.assertIsInstance(users, dict)
        self.assertEqual(users["id"], 1)
        self.assertEqual(users["username"], "admin")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.esb.esbclient.client_backend")
    def test_get_all_users(self, patch_client):
        patch_client.usermanage.list_users.return_value = {
            "count": 1,
            "results": [{"username": "admin", "display_name": "admin"}],
        }
        users = get_all_users(users=["admin"])
        self.assertIsInstance(users, list)
        self.assertEqual(users[0]["id"], "admin")
        self.assertEqual(users[0]["bk_username"], "admin")

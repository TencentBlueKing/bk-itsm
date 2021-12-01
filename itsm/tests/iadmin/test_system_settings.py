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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

from django.test import TestCase, override_settings


class SystemSettingsTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_configrations(self):
        url = "/api/iadmin/system_settings/configrations/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data, dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_change_settings(self):
        url = "/api/iadmin/system_settings/3/"
        data = {"key": "FIRST_STATE_SWITCH", "type": "FUNCTION", "value": "off"}
        rsp = self.client.put(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["data"]["id"], 3)
        self.assertEqual(rsp.data["data"]["type"], "FUNCTION")
        self.assertEqual(rsp.data["data"]["key"], "FIRST_STATE_SWITCH")
        self.assertEqual(rsp.data["data"]["value"], "off")

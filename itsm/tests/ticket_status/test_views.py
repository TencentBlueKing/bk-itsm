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

from itsm.ticket_status.models import StatusTransit, TicketStatusConfig, TicketStatus


class TicketStatusTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_variable_list(self):
        url = "/api/ticket_status/status/get_configs/"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(len(rsp.data), 4)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertIsInstance(rsp.data, dict)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_save_status_of_service_type(self):
        data = {
            "service_type": "change",
            "ticket_status_ids": [1, 2, 3, 4, 5, 6, 7, 8],
            "start_status_id": 2,
            "over_status_ids": [6, 7, 8],
        }
        url = "/api/ticket_status/status/save_status_of_service_type/"

        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["result"], True)

        data = {
            "service_type": "",
            "ticket_status_ids": [1, 2, 3, 4, 5, 6, 7, 8],
            "start_status_id": 2,
            "over_status_ids": [6, 7, 8],
        }
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "0:服务类型不合法")
        self.assertEqual(rsp.data["result"], False)

        data = {
            "service_type": "change",
            "ticket_status_ids": [1, 2, 3, 4, 5, 6, 7, 8],
            "over_status_ids": [6, 7, 8],
        }
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "0:设置为起始状态的工单状态不存在，请联系管理员")
        self.assertEqual(rsp.data["result"], False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_list(self):
        url = "/api/ticket_status/transit/is_auto/?service_type=change"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["result"], True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ticket_status_list(self):
        url = "/api/ticket_status/status/?service_type=change&ordering=order"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(len(rsp.data["data"]), 8)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["result"], True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_patch(self):
        url = "/api/ticket_status/status/3/"
        data = {"name": "已解决", "desc": "", "color_hex": "#3A84FF"}
        rsp = self.client.patch(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["result"], True)

        data = {"name": "已解决", "desc": "", "color_hex": ""}
        rsp = self.client.patch(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "color_hex:二进制颜色不能为空")
        self.assertEqual(rsp.data["result"], False)

        data = {"name": "", "desc": "", "color_hex": "#3A84FF"}
        rsp = self.client.patch(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "name:请输入状态名称")
        self.assertEqual(rsp.data["result"], False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ticket_status_config_model(self):
        config = TicketStatusConfig.objects.get(id=1)
        config.init_ticket_status_config()
        self.assertEqual(config.service_type_name, "变更管理")
        self.assertEqual(config.ticket_status, "新/处理中/已解决/待确认/挂起/已完成/已终止/已撤销")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ticket_status_model(self):
        status = TicketStatus.objects.get(id=1)
        status.init_ticket_status()
        self.assertIsInstance(status.all_status_info(), dict)


class TransitTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_list(self):
        url = "/api/ticket_status/transit/?service_type=change"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["result"], True)
        self.assertEqual(len(rsp.data["data"]), 39)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_save_transit_of_service_type(self):
        url = "/api/ticket_status/transit/save_transit_of_service_type/"
        data = {
            "service_type": "change",
            "transits": [
                {"from_status": 1, "to_status": 1},
                {"from_status": 1, "to_status": 2},
                {"from_status": 1, "to_status": 6},
                {"from_status": 1, "to_status": 7},
                {"from_status": 1, "to_status": 8},
                {"from_status": 1, "to_status": 3},
                {"from_status": 2, "to_status": 2},
                {"from_status": 2, "to_status": 3},
                {"from_status": 2, "to_status": 4},
                {"from_status": 2, "to_status": 5},
                {"from_status": 2, "to_status": 6},
                {"from_status": 2, "to_status": 7},
                {"from_status": 2, "to_status": 8},
                {"from_status": 3, "to_status": 2},
                {"from_status": 3, "to_status": 3},
                {"from_status": 3, "to_status": 4},
                {"from_status": 3, "to_status": 5},
                {"from_status": 3, "to_status": 6},
                {"from_status": 3, "to_status": 7},
                {"from_status": 3, "to_status": 8},
                {"from_status": 4, "to_status": 2},
                {"from_status": 4, "to_status": 3},
                {"from_status": 4, "to_status": 4},
                {"from_status": 4, "to_status": 5},
                {"from_status": 4, "to_status": 6},
                {"from_status": 4, "to_status": 7},
                {"from_status": 4, "to_status": 8},
                {"from_status": 5, "to_status": 2},
                {"from_status": 5, "to_status": 3},
                {"from_status": 5, "to_status": 4},
                {"from_status": 5, "to_status": 5},
                {"from_status": 5, "to_status": 6},
                {"from_status": 5, "to_status": 7},
                {"from_status": 5, "to_status": 8},
            ],
        }
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["result"], True)

        data.pop("service_type")
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "0:服务类型不合法")
        self.assertEqual(rsp.data["result"], False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_set_transit_rule(self):
        url = "/api/ticket_status/status/1/set_transit_rule/"
        data = {"to_status": 6, "threshold": "1", "threshold_unit": "m"}
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["result"], True)

        data.pop("to_status")
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "0:流转目标的单据状态不存在，请联系管理员")
        self.assertEqual(rsp.data["result"], False)

        data = {"to_status": 6, "threshold": "1", "threshold_unit": "m"}
        data.pop("threshold")
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "0:阈值必须为正整数，请重新输入")
        self.assertEqual(rsp.data["result"], False)

        data = {"to_status": 6, "threshold": "1", "threshold_unit": "m"}
        data.pop("threshold_unit")
        rsp = self.client.post(path=url, data=data, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "0:阈值单位错误，请重新输入")
        self.assertEqual(rsp.data["result"], False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_auto_detail(self):
        url = "/api/ticket_status/transit/get_auto_detail/?from_status_id=1"
        rsp = self.client.get(path=url, data=None, content_type="application/json")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.data["message"], "success")
        self.assertEqual(rsp.data["result"], True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ticket_transit_model(self):
        transit = StatusTransit.objects.get(id=1)
        transit.init_status_transit()

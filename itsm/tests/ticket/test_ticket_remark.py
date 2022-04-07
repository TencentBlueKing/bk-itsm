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

import json
import mock
from blueapps.core.celery.celery import app

from django.test import TestCase, override_settings

from itsm.service.models import CatalogService
from itsm.ticket.models import Ticket, AttentionUsers


class TicketRemarkTest(TestCase):
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        Ticket.objects.all().delete()
        AttentionUsers.objects.all().delete()

        CatalogService.objects.create(
            service_id=1, is_deleted=False, catalog_id=3, creator="admin"
        )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_remark(self, patch_get_user_departments):
        patch_get_user_departments.return_value = {}
        data = {
            "catalog_id": 3,
            "service_id": 1,
            "service_type": "request",
            "fields": [
                {
                    "type": "STRING",
                    "id": 1,
                    "key": "title",
                    "value": "test_ticket",
                    "choice": [],
                },
                {
                    "type": "STRING",
                    "id": 5,
                    "key": "apply_content",
                    "value": "测试内容",
                },
                {
                    "type": "STRING",
                    "key": "ZHIDINGSHENPIREN",
                    "value": "test",
                },
                {
                    "type": "STRING",
                    "key": "apply_reason",
                    "value": "test",
                },
            ],
            "creator": "admin",
            "attention": True,
        }
        url = "/api/ticket/receipts/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        ticket_id = rsp.data["data"]["id"]

        remark_list_url = "/api/ticket/remark/?ticket_id={}&show_type=PUBLIC&page=1&page_size=10".format(
            ticket_id
        )

        rsp = self.client.get(
            path=remark_list_url, data=None, content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"]["items"], list)
        self.assertEqual(len(rsp.data["data"]["items"]), 1)
        self.assertEqual(rsp.data["data"]["items"][0]["remark_type"], "ROOT")

        root_id = rsp.data["data"]["items"][0]["id"]

        # 测试回复, 创建一条内部评论
        create_remark_url = "/api/ticket/remark/"

        create_remark_data = {
            "content": "外部评论",
            "ticket_id": ticket_id,
            "parent__id": root_id,
            "remark_type": "PUBLIC",
            "users": [],
        }

        rsp = self.client.post(
            path=create_remark_url,
            data=create_remark_data,
            content_type="application/json",
        )
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], dict)

        # 测试回复, 创建一条外部评论
        create_remark_url = "/api/ticket/remark/"

        create_remark_data = {
            "content": "内部评论",
            "ticket_id": ticket_id,
            "parent__id": root_id,
            "remark_type": "INSIDE",
            "users": [],
        }

        rsp = self.client.post(
            path=create_remark_url,
            data=create_remark_data,
            content_type="application/json",
        )
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], dict)

        remark_id = rsp.data["data"]["id"]

        # 测试编辑
        update_data = {
            "content": "外部评论123",
            "users": [],
            "remark_type": "INSIDE",
            "id": remark_id,
        }

        update_url = "/api/ticket/remark/{}/".format(remark_id)

        rsp = self.client.put(
            path=update_url,
            data=update_data,
            content_type="application/json",
        )

        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], dict)
        self.assertEqual(rsp.data["data"]["content"], "外部评论123")

        # 再次测试查询
        remark_list_url = "/api/ticket/remark/?ticket_id={}&show_type=PUBLIC&page=1&page_size=10".format(
            ticket_id
        )

        rsp = self.client.get(
            path=remark_list_url, data=None, content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], dict)
        self.assertEqual(len(rsp.data["data"]["items"]), 2)

        # 再次测试查询
        remark_list_url = "/api/ticket/remark/?ticket_id={}&show_type=INSIDE&page=1&page_size=10".format(
            ticket_id
        )

        rsp = self.client.get(
            path=remark_list_url, data=None, content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], dict)
        self.assertEqual(len(rsp.data["data"]["items"]), 2)

        # 再次测试查询
        remark_list_url = (
            "/api/ticket/remark/?ticket_id={}&show_type=ALL&page=1&page_size=10".format(
                ticket_id
            )
        )

        rsp = self.client.get(
            path=remark_list_url, data=None, content_type="application/json"
        )
        self.assertEqual(rsp.data["result"], True)
        self.assertIsInstance(rsp.data["data"], dict)
        self.assertEqual(len(rsp.data["data"]["items"]), 3)

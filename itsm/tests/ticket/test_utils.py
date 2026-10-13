# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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
from django.test import SimpleTestCase

from itsm.component.constants import NODE_FAILED
from itsm.ticket.utils import build_message


class BuildMessageTest(SimpleTestCase):
    @mock.patch("itsm.ticket.utils.get_custom_notify")
    def test_custom_ticket_fields_are_rendered(self, get_custom_notify):
        custom_notify = mock.Mock(
            title_template="${title}-${custom_field}",
            content_template="${custom_field}/${custom_field__display}/${message}",
        )
        get_custom_notify.return_value = custom_notify

        ticket = mock.Mock()
        ticket.get_output_fields.return_value = {
            "custom_field": "field value",
            "custom_field__display": "display value",
            "title": "custom title",
        }
        ticket.get_notify_context.return_value = {"title": "ticket title"}

        content, title = build_message(
            mock.Mock(type="EMAIL"), None, ticket, "failure message", NODE_FAILED
        )

        self.assertEqual(content, "field value/display value/failure message")
        self.assertEqual(title, "ticket title-field value")
        ticket.get_output_fields.assert_called_once_with(
            return_format="dict", need_display=True
        )

    @mock.patch("itsm.ticket.utils.get_custom_notify")
    def test_fields_context_error_does_not_raise(self, get_custom_notify):
        """第 2 项：单据字段上下文获取失败时降级为空上下文，不允许中断通知任务。"""
        get_custom_notify.return_value = mock.Mock(
            title_template="${title}", content_template="${message}"
        )

        ticket = mock.Mock()
        ticket.id = 1
        ticket.get_output_fields.side_effect = RuntimeError("fields exploded")
        ticket.get_notify_context.return_value = {"title": "ticket title"}

        content, title = build_message(
            mock.Mock(type="EMAIL"), None, ticket, "failure message", NODE_FAILED
        )

        self.assertEqual(content, "failure message")
        self.assertEqual(title, "ticket title")

    @mock.patch("itsm.ticket.utils.get_custom_notify")
    def test_given_ticket_fields_are_reused_without_mutation(self, get_custom_notify):
        """第 2 项：传入缓存的 ticket_fields 时不再查询，且缓存对象不被污染。"""
        get_custom_notify.return_value = mock.Mock(
            title_template="${custom_field}", content_template="${message}"
        )

        ticket = mock.Mock()
        ticket.get_notify_context.return_value = {}
        cached_fields = {"custom_field": "field value"}

        content, title = build_message(
            mock.Mock(type="EMAIL"),
            None,
            ticket,
            "failure message",
            NODE_FAILED,
            ticket_fields=cached_fields,
        )

        self.assertEqual(title, "field value")
        self.assertEqual(content, "failure message")
        ticket.get_output_fields.assert_not_called()
        # 缓存对象不能被 message/action 等通知变量污染
        self.assertEqual(cached_fields, {"custom_field": "field value"})

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
from django.test import TestCase

from itsm.trigger.models import ActionSchema, Trigger, TriggerRule, Action
from itsm.trigger.rules.manager import TriggerRuleManager
from itsm.trigger.signal import trigger_signal
from itsm.component.constants import SOURCE_TICKET
from itsm.component.notify import WeixinNotifier, EmailNotifier, SmsNotifier


class SubComponentTriggerTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        self.test_source_id = 1146
        self.ticket_id = 1123
        params = {
            "name": "组合通知发送",
            "display_name": "发送通知",
            "component_type": "send_message",
            "operate_type": "BACKEND",
            "can_repeat": False,
            "params": [
                {
                    "key": "sub_message_component",
                    "sub_components": [
                        {
                            "key": "send_email_message",
                            "params": [
                                {"key": "title", "value": "【ITSM通知】您有待处理工单${sn}", "ref_type": "import"},
                                {
                                    "key": "content",
                                    "value": "工单编号:<a>${sn}</a> <br/> 标题：<a>${title}</a>",
                                    "ref_type": "import",
                                },
                                {
                                    "key": "receivers",
                                    "value": [
                                        {
                                            "ref_type": "reference",
                                            "value": {
                                                "member_type": "VARIABLE",
                                                "members": "current_processors,creator",
                                            },
                                        }
                                    ],
                                },
                            ],
                            "inputs": ["title", "content"],
                        },
                        {
                            "key": "send_wechat_message",
                            "params": [
                                {"key": "title", "value": "【ITSM通知】您有待处理工单${sn}", "ref_type": "import"},
                                {"key": "content", "value": "工单编号:${sn} 标题：${title}", "ref_type": "import"},
                                {
                                    "key": "receivers",
                                    "value": [
                                        {
                                            "ref_type": "reference",
                                            "value": {
                                                "member_type": "VARIABLE",
                                                "members": "current_processors,creator",
                                            },
                                        }
                                    ],
                                },
                            ],
                            "inputs": ["content"],
                        },
                    ],
                }
            ],
        }
        self.email_task = ActionSchema.objects.create(**params)

        self.trigger = Trigger.objects.create(
            signal="ENTER_STATE",
            sender="1",
            inputs=["status"],
            source_type=SOURCE_TICKET,
            source_id=self.test_source_id,
        )

        TriggerRule.objects.create(
            condition={
                "all": [
                    {
                        "name": "variable_by_name",
                        "key": "current_status",
                        "value": None,
                        "type": "reference",
                        "ref_key": "status",
                        "operator": "equal_to",
                        "field_type": "numeric",
                    }
                ]
            },
            action_schemas=[self.email_task.id],
            trigger_id=self.trigger.id,
        )

        self.rule_manager = TriggerRuleManager(trigger=self.trigger)

        super(SubComponentTriggerTestCase, self).__init__(*args, **kwargs)

    # @mock.patch.object(EmailNotifier, "send")
    # @mock.patch.object(SmsNotifier, "send")
    # @mock.patch.object(WeixinNotifier, "send")
    # def test_true_trigger(self, mock_send_weixin, mock_send_sms, mock_send_email):
    #     mock_send_weixin.return_value = None
    #     mock_send_sms.return_value = None
    #     mock_send_email.return_value = None
    #     context = {
    #         "status": True,
    #         "current_status": True,
    #         "sn": "REQ20200317000005",
    #         "title": "这是一个测试，看看能不能发邮件",
    #         "current_processors": "rubi_normal",
    #         "history_processors": "rubi_admin",
    #         "creator": "rubi_admin",
    #     }
    # 
    #     trigger_signal.send(
    #         "ENTER_STATE",
    #         sender='1',
    #         source_type='ticket',
    #         source_id=self.ticket_id,
    #         context=context,
    #         rule_source_id=self.test_source_id,
    #         rule_source_type=SOURCE_TICKET,
    #     )
    #     self.assertTrue(Action.objects.filter(source_id=self.ticket_id).exists())

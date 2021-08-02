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

import unittest

# from django.test import TestCase
from itsm.sla.models import SlaTimerRule


class SlaTimerRuleTest(unittest.TestCase):
    def setUp(self):
        start_rules = [
            {
                "name": "跟状态相关的触发器",
                "service_type": "request",
                "condition_type": "START",
                "condition": {
                    "type": "all",
                    "expressions": [
                        {"name": "current_status", "value": "running", "operator": "equal_to", "type": "STRING"}
                    ],
                },
            },
            {
                "name": "跟状态相关的触发器",
                "service_type": "request",
                "condition_type": "PAUSE",
                "condition": {
                    "type": "and",
                    "expressions": [{"name": "priority", "value": "high", "operator": "equal_to", "type": "STRING"}],
                },
            },
        ]
        for item in start_rules:
            SlaTimerRule.objects.create(**item)

    def test_build_rules(self):
        rules = {}
        event_status_conditions = {
            "START": {"name": "sla_task_status", "value": "UNACTIVATED", "operator": "equal_to"},
            "RESUME": {"name": "sla_task_status", "value": "PAUSED", "operator": "equal_to"},
            "PAUSE": {"any": [{"name": "sla_task_status", "value": "SUSPENDED", "operator": "equal_to"}]},
            "END": {
                "any": [
                    {"name": "sla_task_status", "value": "RUNNING", "operator": "equal_to"},
                    {"name": "sla_task_status", "value": "PAUSED", "operator": "equal_to"},
                ]
            },
            "STOP": {"name": "sla_task_status", "value": "RUNNING", "operator": "equal_to"},
        }

        for rule in SlaTimerRule.objects.filter(service_type="request"):
            operator_type = rule.condition["type"]
            condition = {
                "all": [event_status_conditions[rule.condition_type], {operator_type: rule.condition["expressions"]}]
            }
            if rule.condition_type in rules:
                rules[rule.condition_type]["conditions"]["any"].append(condition)
            else:
                rules[rule.condition_type] = {
                    "conditions": {"any": [condition]},
                    "actions": [{"name": rule.condition_type}],
                }
        print(list(rules.values()))


"""
        {
            "any": [
                {
                    "all": [
                        {
                            "any": [
                                {"operator": "equal_to", "name": "sla_task_status", "value": "RUNNING"},
                                {"operator": "equal_to", "name": "sla_task_status", "value": "PAUSED"},
                            ]
                        },
                        {
                            "all": [
                                {"operator": "equal_to", "type": "STRING", "name": "current_status", "value": "running"}
                            ]
                        },
                    ]
                },
                {
                    "all": [
                        {
                            "any": [
                                {"operator": "equal_to", "name": "sla_task_status", "value": "RUNNING"},
                                {"operator": "equal_to", "name": "sla_task_status", "value": "PAUSED"},
                            ]
                        },
                        {"all": [{"operator": "equal_to", "type": "STRING", "name": "priority", "value": "high"}]},
                    ]
                },
            ]
        }
"""

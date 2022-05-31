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

from business_rules.actions import BaseActions, rule_action
from business_rules.fields import FIELD_NUMERIC, FIELD_TEXT
from common.log import logger

from itsm.component.constants import BACKEND
from itsm.component.utils.lock import share_lock
from itsm.trigger.models import Action


class ResponseActions(BaseActions):
    def __init__(self, trigger, context):
        self.trigger = trigger
        self.context = context

    @rule_action(
        params={
            "rule": FIELD_NUMERIC,
            "source_type": FIELD_TEXT,
            "source_id": FIELD_NUMERIC,
        }
    )
    def trigger_handle(self, rule, source_type, source_id):
        """
        针对当前触发器规则满足条件的actions进行操作
        """
        tasks = []
        for action in rule.actions:
            action_obj = self.can_repeat(source_type, source_id, action, rule)
            if action_obj:
                tasks.append(
                    Action.objects.create(
                        signal=self.trigger.signal,
                        sender=self.trigger.sender,
                        context=self.context,
                        source_type=source_type,
                        source_id=source_id,
                        schema_id=action.id,
                        rule_id=rule.id,
                        trigger_id=self.trigger.id,
                    )
                )
        for task in tasks:
            if task.action_schema.operate_type == BACKEND:
                # 当任务为自动执行的时候，直接调用执行接口
                task.execute()

    @share_lock()
    def can_repeat(self, source_type, source_id, action, rule):

        if action.can_repeat:
            return True

        action_count = Action.objects.filter(
            signal=self.trigger.signal,
            sender=self.trigger.sender,
            source_type=source_type,
            source_id=source_id,
            schema_id=action.id,
            rule_id=rule.id,
            trigger_id=self.trigger.id,
        ).count()
        logger.info(
            "[can_repeat] source_type={}, source_id={}. action={}, rule={}, action_count={}".format(
                source_type, source_id, action.id, rule.id, action_count
            )
        )
        if action_count == 0:
            return True

        return False

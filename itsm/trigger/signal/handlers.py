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

from common.log import logger
from itsm.trigger.models import Trigger, Action
from itsm.trigger.rules.manager import TriggerRuleManager
from itsm.component.constants import SOURCE_TICKET
from .signals import post_action_finish


def event_dispatcher(
    sender, source_type=SOURCE_TICKET, source_id=None, context=None, **kwargs
):
    """
    :param sender:   {"signal":"真实信号", "sender": "发送者", "source_type":"规则类型", source_id}
    :param context:
    :param kwargs:
    :return:
    """
    # first 根据sender的内容获取 trigger rules
    triggers = Trigger.objects.filter(**sender)
    logger.info(
        "[handlers->event_dispatcher] 收到一个触发器事件, source_type={}, sender={}, trigger_num={}".format(
            source_type, sender, len(triggers)
        )
    )
    # 每个触发器进行各自的规则运行
    for trigger in triggers:
        logger.info(
            "[handlers->event_dispatcher] 正在执行触发器 -> name={}".format(trigger.name)
        )
        if not trigger.is_enabled:
            logger.info(
                "[handlers->event_dispatcher] 检测到当前触发器未开启，跳过执行 -> name={}".format(
                    trigger.name
                )
            )
            continue

        rule_manager = TriggerRuleManager(trigger, source_type, source_id, context)
        rule_manager.run()


def action_finish_handler(sender, action_id, result, error_message, **kwargs):
    """响应事件处理完成的处理器"""
    try:
        action = Action.objects.get(id=action_id)
    except Action.DoesNotExist:
        return
    outputs = kwargs.get("outputs")
    action.set_finished(result, error_message, outputs)

    post_action_finish.send(Action, instance=action)

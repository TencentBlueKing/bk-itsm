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

import datetime
import logging

from common.redis import Cache
from itsm.sla_engine.constants import (
    SLA_ACTION_TIME,
    PERCENT,
    TO_SECOND,
    REPLY_WARING,
    HANDLE_WARING,
    REPLY_TIMEOUT,
    HANDLE_TIMEOUT,
)
from itsm.sla_engine.models import SlaActionHistory
from itsm.sla_engine.utils import action_time

logger = logging.getLogger(__name__)


class SlaTaskAction(object):
    """任务动作集合"""

    def __init__(self, action, ticket, sla_task, action_policy_type, ac_time):
        self.action = action
        self.ticket = ticket
        self.sla_task = sla_task
        self.action_policy_type = action_policy_type
        self.ac_time = ac_time
        self.redis_inst = Cache("SLA")
        self.ac_key = "{ticket_id}-{sla_task_id}-{action_policy_type}".format(
            ticket_id=ticket.id, sla_task_id=sla_task.id, action_policy_type=action_policy_type
        )

    @staticmethod
    def success_result(data=None, message=""):
        """成功的输出结果"""
        if data is None:
            data = {}
        return {"result": True, "data": data, "message": message}

    def failed_result(self, message):
        """失败的输出结果"""
        return {"result": False, "data": {"ac_key": self.ac_key, "ac_time": self.ac_time, },
                "message": message}

    def failure_handler(self, error):
        """Action错误的统一处理"""

        SlaActionHistory.objects.create(
            action_id=self.action.id,
            status="FAILED",
            action_type=self.action.action_type,
            action_detail=self.failed_result("异常错误: %s" % error),
            condition=[],
        )

    def success_handler(self, data):
        SlaActionHistory.objects.create(
            action_id=self.action.id,
            status="SUCCESS",
            action_type=self.action.action_type,
            action_detail=self.success_result(data),
            condition=[],
        )

    def alert(self):
        # 1、设置下次提醒时间
        # 2、提醒
        # 3、更新状态

        # 计算出当前耗时

        if self.action.config["notify_rule"] == "retry":
            self.set_next_alert(self.action.config["notify_freq"], self.action.config["freq_unit"])

        try:
            self.action.do_alert_action(self.ticket)
        except Exception as e:
            return self.failure_handler(str(e))

        return self.success_handler({"cost_time": self.sla_task.cost_time})

    def set_next_alert(self, notify_freq, freq_unit):

        # 以下情况不需要再次设置时间
        # 下次告警时间大于超时时间

        next_action_time, ignore_action = self.get_next_action(notify_freq, freq_unit)
        if ignore_action:
            self.redis_inst.delete(self.ac_key)
            return

        # 查看当前ac_key对应的时间集合
        ac_time = datetime.datetime.strftime(next_action_time, "%Y-%m-%d %H:%M")
        ac_value = [self.action.id]
        # 插入数据到redis
        self.redis_inst.hsetnx(name=ac_time, key=self.ac_key, value=ac_value)
        self.redis_inst.sadd(self.ac_key, ac_time)
        self.redis_inst.sadd(SLA_ACTION_TIME, ac_time)

    def get_next_action(self, notify_freq, freq_unit):
        """
        return: next_action_time, ignore_action

        """

        def get_seconds(time, freq, unit):
            """根据频率单位freq_unit构建用时"""
            if unit == "%":
                return time * freq * PERCENT
            return freq * TO_SECOND[unit]

        if self.action_policy_type == REPLY_WARING:
            seconds = get_seconds(self.sla_task.reply_time, notify_freq, freq_unit)
            next_action_time = action_time(seconds, self.sla_task.sla_id, self.ticket.priority)
            return next_action_time, next_action_time >= self.sla_task.reply_deadline

        if self.action_policy_type == REPLY_TIMEOUT:
            seconds = get_seconds(self.sla_task.reply_time, notify_freq, freq_unit)
            next_action_time = action_time(seconds, self.sla_task.sla_id, self.ticket.priority)
            return next_action_time, False

        if self.action_policy_type == HANDLE_WARING:
            seconds = get_seconds(self.sla_task.handle_time, notify_freq, freq_unit)
            next_action_time = action_time(seconds, self.sla_task.sla_id, self.ticket.priority)
            return next_action_time, next_action_time >= self.sla_task.deadline

        if self.action_policy_type == HANDLE_TIMEOUT:
            seconds = get_seconds(self.sla_task.handle_time, notify_freq, freq_unit)
            next_action_time = action_time(seconds, self.sla_task.sla_id, self.ticket.priority)
            return next_action_time, False

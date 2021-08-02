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
import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext as _
from jsonfield import JSONField
from django.db import transaction
from common.redis import Cache
from itsm.component.constants import EMPTY_DICT, EMPTY_LIST, LEN_LONG, EMPTY_INT
from itsm.sla.models import ActionPolicy
from itsm.sla_engine.constants import (
    HANDLE_WARING,
    NORMAL,
    PAUSED,
    REPLY_WARING,
    RUNNING,
    SLA_ACTION_TIME,
    STOPPED,
    TO_SECOND,
    UNACTIVATED,
    REPLY_TIMEOUT,
    HANDLE_TIMEOUT,
    PERCENT,
    SLA_TASK_STATUS,
    SLA_TIMING_STATUS,
)
from itsm.sla_engine.decorators import _frozen_check
from itsm.sla_engine.utils import action_time, action_time_delta


class SlaTask(models.Model):
    """sla任务
    记录sla任务信息，
    sla状态：正常->已升级->已违规
    任务状态：未激活->计时中|暂停中|已停止
    """

    sla_id = models.IntegerField(_("关联的sla协议ID"))
    name = models.CharField(_("任务名称"), max_length=LEN_LONG, null=True)
    ticket_id = models.IntegerField(_("关联的单据ID"), null=True)
    start_node_id = models.IntegerField(_("计时开始节点ID"), null=True)
    end_node_id = models.IntegerField(_("计时结束节点ID"), null=True)
    deadline = models.DateTimeField(_("任务截止时间"), null=True)
    cost_time = models.IntegerField(_("经过的时长(s)"), default=0)
    begin_at = models.DateTimeField(_("任务开始计时的时间"), null=True)
    end_at = models.DateTimeField(_("任务结束计时的时间"), null=True)
    upgrade_at = models.DateTimeField(_("任务升级时间"), null=True)
    last_settlement_time = models.DateTimeField(_("上次结算时间"), null=True)
    sla_status = models.IntegerField(_("sla状态"), choices=SLA_TIMING_STATUS, default=NORMAL)
    task_status = models.IntegerField(_("任务状态"), choices=SLA_TASK_STATUS, default=UNACTIVATED)
    is_reply_need = models.BooleanField(_("是否需要响应"), default=False)
    is_replied = models.BooleanField(_("是否已响应"), default=False)
    reply_deadline = models.DateTimeField(_("响应截至时间"), null=True)
    reply_cost = models.IntegerField(_("响应耗时(s)"), default=0)
    replied_at = models.DateTimeField(_("响应时间"), null=True)

    class Meta:
        app_label = "sla_engine"
        verbose_name = _("sla任务")
        verbose_name_plural = _("sla任务")

    def __unicode__(self):
        return "{}({})".format(self.ticket_id, self.deadline)

    @property
    def protocol(self):
        """sla任务对应的sla协议"""
        from itsm.sla.models import Sla

        return Sla._objects.get(id=self.sla_id)

    @property
    def ticket(self):
        """任务关联的ticket"""
        from itsm.ticket.models import Ticket

        return Ticket._objects.get(id=self.ticket_id)

    @property
    def action_policies(self):
        """服务升级事件策略"""
        return self.protocol.action_policies.all().order_by("order")

    def calc_deadline(self, start_time=None):
        """
        计算deadline 即处理超时的时间
        """
        remain_time = self.handle_time - self.cost_time
        return action_time(remain_time, self.sla_id, self.ticket.priority, start_time)

    def calc_reply_deadline(self, start_time=None):
        """
        计算响应超时时间
        """
        remain_time = self.reply_time - self.cost_time
        return action_time(remain_time, self.sla_id, self.ticket.priority, start_time)

    @property
    def handle_time(self):
        """当前优先级对应的服务时长（s）"""
        try:
            priority_policy = self.protocol.policies.get(priority=self.ticket.priority)
        except ObjectDoesNotExist:
            self.frozen()
        else:
            return priority_policy.handle_time * TO_SECOND[priority_policy.handle_unit]

    @property
    def reply_time(self):
        """当前优先级对应的响应时长（s）"""
        try:
            priority_policy = self.protocol.policies.get(priority=self.ticket.priority)
        except ObjectDoesNotExist:
            self.frozen()
        else:
            return priority_policy.reply_time * TO_SECOND[priority_policy.reply_unit]

    def policy_action_time(self, action_policy, start_time=None):
        """获取策略的动作时间"""

        percent = action_policy.condition["expressions"][0]["value"]

        # 获取响应、处理对应的优先级计算出来的总耗时
        if action_policy.type in [REPLY_WARING, REPLY_TIMEOUT]:
            total_time = getattr(self, "reply_time", 0)
        else:
            total_time = getattr(self, "handle_time", 0)

        total_time = total_time * percent * PERCENT
        remain_time = total_time - self.cost_time
        return action_time(remain_time, self.sla_id, self.ticket.priority, start_time)

    def reply_waring_time(self, start_time=None):
        """
        响应预警时间, 勾选响应提醒则存在
        """
        try:
            action_policy = self.protocol.action_policies.get(type=REPLY_WARING)
        except ActionPolicy.DoesNotExist:
            return None

        percent = action_policy.condition["expressions"][0]["value"]
        seconds = self.reply_time * percent * PERCENT
        return action_time(seconds, self.sla_id, self.ticket.priority, start_time)

    def handle_waring_time(self, start_time=None):
        """
        处理预警时间
        """
        action_policy = self.protocol.action_policies.get(type=HANDLE_WARING)
        percent = action_policy.condition["expressions"][0]["value"]
        seconds = self.handle_time * percent * PERCENT
        return action_time(seconds, self.sla_id, self.ticket.priority, start_time)

    def reply_timeout_time(self, start_time=None):
        """
        响应超时时间
        """
        return action_time(self.reply_time, self.sla_id, self.ticket.priority, start_time)

    def handle_timeout_time(self, start_time=None):
        """
        处理超时时间
        """
        return action_time(self.handle_time, self.sla_id, self.ticket.priority, start_time)

    @property
    def protocol_name(self):
        return self.protocol.name

    @property
    def start_node_name(self):
        return self.ticket.state(self.start_node_id)["name"]

    @property
    def end_node_name(self):
        return self.ticket.state(self.end_node_id)["name"]

    @_frozen_check
    def update_cost_duration(self, current_time=None):
        """
        更新经过的时间和百分比
        当前时间与上次结算时间对比
        """
        # 经过的时长
        self.cost_time = self.get_cost_time(current_time)
        self.last_settlement_time = current_time
        self.save()

    def get_cost_time(self, current_time=None):
        if current_time is None:
            current_time = datetime.datetime.now()

        start_time = self.last_settlement_time
        if not start_time:
            start_time = self.begin_at

        new_duration = action_time_delta(start_time, current_time, self.sla_id,
                                         self.ticket.priority)

        cost_time = self.cost_time + new_duration
        return cost_time

    @_frozen_check
    def update_sla_status(self, current_time):
        """更新sla等级状态"""
        """
        两个时间：响应时长，处理时长。响应时长是处理时长的一部分。
        提醒和超时：
        1、在响应时长的提醒规则里，如果用户还没有响应。这里视为响应提醒，提醒并不会变颜色！
        在响应时长内一直没响应，达到响应时长后，则视为响应超时。这里按照响应超时设置的颜色高亮单据颜色。比如，浅红。
        2、处理时长的逻辑相似：在处理时长的过程中，设置了提醒规则。
        是指希望在一定阶段提醒用户抓紧时间处理，不要超时。所有提醒只是发通知，并不会改单据颜色！只有超出了规定的预计要求时间，才会高亮颜色！
        """

        # 处理超时
        if current_time > self.deadline:
            self.sla_status = HANDLE_TIMEOUT
            self.save()
            return

        # 响应超时
        if self.is_reply_need and not self.is_replied and current_time > self.reply_deadline:
            self.sla_status = REPLY_TIMEOUT
            self.save()
            return

        return

    @_frozen_check
    def start(self, begin_at):
        """
        1、记录任务开始时间
        2、把SLA协议中的动作拆分为任务，并计算好触发时间，分钟级
        3、redis set存储触发时间，用于后面补偿
        4、redis hash存储  ac_time: time, ac_key: {ticket_id}-{sla_task_id}-{action_policy_type}, ac_value: [action_id]
        """
        SlaEventLog.objects.create_start_event(self.id, self.ticket.priority)

        self.deadline = self.calc_deadline(start_time=begin_at)
        self.begin_at = begin_at
        self.task_status = RUNNING
        if self.is_reply_need:
            self.reply_deadline = self.calc_reply_deadline(start_time=begin_at)
        self.save()

        sla_redis_inst = Cache("SLA")
        for action_policy in self.action_policies:
            action_trigger_time = self.policy_action_time(action_policy, begin_at)

            ac_time = action_trigger_time.strftime("%Y-%m-%d %H:%M")
            ac_key = "{ticket_id}-{sla_task_id}-{action_policy_type}".format(
                ticket_id=self.ticket_id, sla_task_id=self.id, action_policy_type=action_policy.type
            )
            # 任务用到的必要参数
            
            ac_value = json.dumps([action.id for action in action_policy.actions.all()])

            # 插入数据到redis
            # 按时间记录任务
            sla_redis_inst.hsetnx(name=ac_time, key=ac_key, value=ac_value)
            # 按任务记录触发时间
            sla_redis_inst.sadd(ac_key, ac_time)
            sla_redis_inst.sadd(SLA_ACTION_TIME, ac_time)

    @_frozen_check
    def reply(self, replied_at):

        with transaction.atomic():
            self.update_cost_duration(replied_at)
            self.replied_at = replied_at
            self.is_replied = True
            self.reply_cost = self.cost_time
            self.save()

            action_policies = self.action_policies.filter(type__in=[REPLY_WARING, REPLY_TIMEOUT])
            self.delete_redis_task(action_policies)

    @_frozen_check
    def resume(self, resume_at):
        """恢复计时任务"""

        with transaction.atomic():
            SlaEventLog.objects.create_resume_event(self.id, self.ticket.priority)
            self.deadline = self.calc_deadline(start_time=resume_at)
            # 更新上次结算时间为恢复挂起时间
            self.last_settlement_time = resume_at
            self.task_status = RUNNING
            if self.is_reply_need and not self.is_replied:
                self.reply_deadline = self.calc_reply_deadline(start_time=resume_at)
            self.save()

            action_policies = self.action_policies
            # 已响应的去除响应策略
            if self.is_reply_need and self.is_replied:
                action_policies = action_policies.exclude(type__in=[REPLY_WARING, REPLY_TIMEOUT])

            self._refresh_redis_task(action_policies, resume_at)

    @_frozen_check
    def pause(self, pause_at):
        """暂停计时任务，归档时间"""
        with transaction.atomic():
            SlaEventLog.objects.create_pause_event(self.id, self.ticket.priority)
            self.update_cost_duration(pause_at)
            self.task_status = PAUSED
            self.save()

            self.delete_redis_task(self.action_policies)

    @_frozen_check
    def stop(self, end_at):
        """停止计时任务，归档最后一段时间"""
        with transaction.atomic():
            SlaEventLog.objects.create_stop_event(self.id, self.ticket.priority)
            self.update_cost_duration()
            self.task_status = STOPPED
            self.end_at = end_at
            self.save()

            # 删除
            self.delete_redis_task(self.action_policies)

    @_frozen_check
    def refresh(self, refresh_at):
        """更新单据优先级后刷新SLA任务"""
        with transaction.atomic():
            self.deadline = self.calc_deadline(start_time=refresh_at)
            self.last_settlement_time = refresh_at
            self.task_status = RUNNING
            if self.is_reply_need and not self.is_replied:
                self.reply_deadline = self.calc_reply_deadline(start_time=refresh_at)
            self.save()

            action_policies = self.action_policies
            # 已响应的去除响应策略
            if self.is_reply_need and self.is_replied:
                action_policies = action_policies.exclude(type__in=[REPLY_WARING, REPLY_TIMEOUT])

            self.delete_redis_task(action_policies)
            self._refresh_redis_task(action_policies, refresh_at)

    def _refresh_redis_task(self, action_policies, refresh_at):
        """重新计算触发任务"""
        from itsm.sla_engine.actions import SlaTaskAction

        sla_redis_inst = Cache("SLA")
        for action_policy in action_policies:
            action_trigger_time = self.policy_action_time(action_policy, refresh_at)
            ac_time = action_trigger_time.strftime("%Y-%m-%d %H:%M")
            # 策略触发时间大于恢复时间，重新入库redis
            if action_trigger_time > refresh_at:
                ac_key = "{ticket_id}-{sla_task_id}-{action_policy_type}".format(
                    ticket_id=self.ticket_id, sla_task_id=self.id,
                    action_policy_type=action_policy.type
                )
                # 任务用到的必要参数
                ac_value = json.dumps([action.id for action in action_policy.actions.all()])
                # 插入数据到redis
                # 按时间记录任务
                sla_redis_inst.hsetnx(name=ac_time, key=ac_key, value=ac_value)
                # 按任务记录触发时间
                sla_redis_inst.sadd(ac_key, ac_time)
                sla_redis_inst.sadd(SLA_ACTION_TIME, ac_time)
            else:
                for action in action_policy.actions.all():
                    sla_task_action = SlaTaskAction(action, self.ticket, self, action_policy.type,
                                                    ac_time)
                    sla_task_action.alert()

    def delete_redis_task(self, action_policies):
        if not action_policies:
            return
        ac_keys = self.get_ac_keys(action_policies)
        self._delete_redis_task(ac_keys)

    def get_ac_keys(self, action_policies):
        ac_keys = [
            "{ticket_id}-{sla_task_id}-{action_policy_type}".format(
                ticket_id=self.ticket_id, sla_task_id=self.id, action_policy_type=action_policy.type
            )
            for action_policy in action_policies
        ]
        return ac_keys

    @staticmethod
    def _delete_redis_task(ac_keys):
        redis_inst = Cache("SLA")
        ac_times = set()
        for ac_key in ac_keys:
            ac_times.update(redis_inst.smembers(ac_key))
        for ac_time in ac_times:
            redis_inst.hdel(ac_time, *ac_keys)
        redis_inst.delete(*ac_keys)

    def frozen(self):
        """sla任务冻结"""
        self.is_frozen = True
        self.save()


class SlaEventLogManager(models.Manager):
    def get_last_start_event(self, sla_task_id):
        """获取最后一次启动计时的事件"""
        return self.filter(sla_task_id=sla_task_id, tick_flag='START', is_archived=False).last()

    def get_last_stop_event(self, sla_task_id):
        """获取最后一次停止计时的事件"""
        return self.filter(sla_task_id=sla_task_id, tick_flag='END', is_archived=False).last()

    def create_start_event(self, sla_task_id, priority):
        """创建开始事件"""
        return self.create(sla_task_id=sla_task_id, priority=priority, event_type='START',
                           tick_flag='START', )

    def create_pause_event(self, sla_task_id, priority):
        """创建暂停事件"""
        return self.create(sla_task_id=sla_task_id, priority=priority, event_type='PAUSE',
                           tick_flag='END', )

    def create_resume_event(self, sla_task_id, priority):
        """创建恢复事件"""
        return self.create(sla_task_id=sla_task_id, priority=priority, event_type='RESUME',
                           tick_flag='START', )

    def create_stop_event(self, sla_task_id, priority):
        """创建停止事件"""
        return self.create(sla_task_id=sla_task_id, priority=priority, event_type='STOP',
                           tick_flag='END', )


class SlaEventLog(models.Model):
    """sla事件日志
    记录影响sla任务状态的事件，
    目前主要有：启动、停止、暂停、恢复
    """

    sla_task_id = models.IntegerField(_("SLA TASK ID"), db_index=True, default=EMPTY_INT)
    priority = models.CharField(_("优先级"), max_length=LEN_LONG)
    event_type = models.CharField(
        _("事件类型"), max_length=LEN_LONG,
        choices=[('PAUSE', "暂停"), ('RESUME', "恢复"), ('STOP', "停止"), ('START', "启动"), ]
    )
    is_archived = models.BooleanField(_("是否已归档"), default=False)
    tick_flag = models.CharField(
        _("计时标志"), max_length=LEN_LONG,
        choices=[('START', "开始计时"), ('END', "结束计时"), ('KEEP', "保持"), ], default='KEEP'
    )
    create_time = models.DateTimeField(_("事件发生时间"), auto_now_add=True)

    objects = SlaEventLogManager()

    class Meta:
        app_label = "sla_engine"
        verbose_name = _("sla事件日志")
        verbose_name_plural = _("sla事件日志")

    def __unicode__(self):
        return "{}({})".format(self.event_type, self.create_time)

    def mark_archived(self):
        """标记为归档"""

        self.is_archived = True
        self.save()


class SlaActionHistoryManager(models.Manager):
    def get_last_success_action(self, action_id, action_type):
        """获取最后一次成功执行的sla行为"""
        return self.filter(action_id=action_id, action_type=action_type, status="SUCCESS").first()


class SlaActionHistory(models.Model):
    """sla行为历史记录"""

    action_id = models.IntegerField(_("任务ID"), db_index=True, default=EMPTY_INT)
    status = models.CharField(_("结果状态"), max_length=LEN_LONG,
                              choices=[("SUCCESS", _("成功")), ("FAILED", _("失败"))])
    action_type = models.CharField(_("行为类型"), max_length=LEN_LONG)
    action_detail = JSONField(_("行为详情"), default=EMPTY_DICT)
    create_time = models.DateTimeField(_("动作发生时间"), auto_now_add=True)
    condition = JSONField(_("触发的规则"), default=EMPTY_LIST)

    objects = SlaActionHistoryManager()

    class Meta:
        app_label = "sla_engine"
        ordering = ("-create_time",)
        verbose_name = _("sla行为历史记录")
        verbose_name_plural = _("sla行为历史记录")

    def __unicode__(self):
        return "{}({})".format(self.action_type, self.status)

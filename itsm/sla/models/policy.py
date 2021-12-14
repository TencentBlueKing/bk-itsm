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

import copy

from django.db import models
from django.utils.translation import ugettext as _
from jsonfield import JSONField
from mako.template import Template

from itsm.component.constants import (
    EMPTY_DICT,
    EMPTY_INT,
    EMPTY_STRING,
    LEN_LONG,
    LEN_NORMAL,
    LEN_SHORT,
    PRIORITYS,
    SERVICE_CATEGORY,
)
from itsm.component.notify import BaseNotifier
from itsm.component.utils.bk_bunch import bunchify
from itsm.iadmin.contants import ACTION_CHOICES_DICT
from itsm.iadmin.models import CustomNotice
from itsm.service.models import Service, ServiceSla
from itsm.sla import managers
from itsm.sla_engine.constants import (
    NORMAL,
    TO_SECOND,
    ACTION_POLICY_TYPES,
    REPLY_WARING,
    REPLY_TIMEOUT,
    REPLY_TIMEOUT_COLOR,
    HANDLE_TIMEOUT_COLOR,
)
from .basic import Model


class PriorityPolicy(Model):
    """服务策略"""

    name = models.CharField(_("策略名称"), max_length=LEN_LONG)
    priority = models.CharField(_("优先级"), max_length=LEN_LONG)
    schedule = models.ForeignKey(
        help_text=_("服务时间"),
        to="Schedule",
        related_name="policies",
        on_delete=models.CASCADE,
    )
    handle_time = models.IntegerField(_("处理期限"), default=EMPTY_INT)
    handle_unit = models.CharField(
        _("时长单位"),
        max_length=LEN_SHORT,
        default="m",
        choices=[
            ("m", "分钟"),
            ("h", "小时"),
            ("d", "天"),
        ],
    )
    reply_time = models.IntegerField(_("应答时长"), blank=True, null=True)
    reply_unit = models.CharField(
        _("应答时长单位"),
        max_length=LEN_SHORT,
        default="m",
        choices=[
            ("m", "分钟"),
            ("h", "小时"),
            ("d", "天"),
        ],
    )

    class Meta:
        app_label = "sla"
        verbose_name = _("服务策略")
        verbose_name_plural = _("服务策略")

    def __unicode__(self):
        return "{}({})".format(self.name, self.priority)

    def schedule_days(self):
        """服务日"""
        from itsm.sla.models import Schedule

        ret = {}
        schedule = Schedule.objects.prefetch_related(
            "days__duration", "workdays__duration", "holidays__duration"
        ).get(id=self.schedule_id)
        for day_type in ["days", "workdays", "holidays"]:
            days = []
            ret.update({day_type: []})

            for day in getattr(schedule, day_type).all():
                day_dict = {
                    "day_of_week": day.day_of_week,
                    "type_of_day": day.type_of_day,
                    "start_date": day.start_date,
                    "end_date": day.end_date,
                    "duration": list(day.duration.values("start_time", "end_time")),
                }
                days.append(day_dict)
                ret.update({day_type: days})
        return ret


class PriorityMatrix(Model):
    """
    优先级矩阵
    """

    service_type = models.CharField(_("服务类型"), max_length=LEN_NORMAL)

    # 紧急程度x影响范围=优先级
    urgency = models.CharField(_("紧急程度"), max_length=LEN_LONG)
    impact = models.CharField(_("影响范围"), max_length=LEN_LONG)
    priority = models.CharField(_("优先级"), max_length=LEN_LONG, blank=True)

    objects = managers.PriorityMatrixManager()

    class Meta:
        unique_together = ("service_type", "urgency", "impact")
        app_label = "sla"
        verbose_name = _("优先级矩阵")
        verbose_name_plural = _("优先级矩阵")

    def __unicode__(self):
        return "{}({})".format(self.service_type, self.priority)


class SlaTimerRule(Model):
    """
    计时规则
    """

    service_type = models.CharField(_("服务类型"), max_length=LEN_NORMAL)

    name = models.CharField(_("规则名称"), max_length=LEN_LONG, default=EMPTY_STRING)
    condition_type = models.CharField(
        _("条件类型"),
        max_length=LEN_NORMAL,
        choices=[("START", _("开始")), ("STOP", _("结束")), ("PAUSE", _("暂停"))],
        default="START",
    )
    condition = JSONField(_("条件"), default=EMPTY_DICT)

    """
    # 条件表达式的格式如下
    {"expressions": [{
                "value": "running",
                "name": "status",
                "type": "STRING",
                "operator": "equal_to"
            }, {
                "value": "processing",
                "name": "status",
                "operator": "equal_to",
                "type": "STRING"
            }
            ],
            "type": "any"
        }
    """

    class Meta:
        app_label = "sla"
        verbose_name = _("计时规则")
        verbose_name_plural = _("计时规则")

    def __unicode__(self):
        return "{}({})".format(self.name, self.service_type)

    @classmethod
    def get_not_sla_ticket_status_keys(cls, service_type):
        """获取不属于sla计算状态下的对应单据状态key组成的集合"""
        from itsm.ticket_status.models import TicketStatus

        def expression_values(expressions):
            """获取表达式的value集合"""
            return set([expression["value"] for expression in expressions])

        over_ticket_status_keys = TicketStatus.objects.filter(
            service_type=service_type, is_over=True
        ).values_list("key", flat=True)

        # 获取sla不计时对应单据状态key
        not_sla_ticket_status_keys = set(over_ticket_status_keys)
        sla_timer_rules = cls.objects.filter(
            service_type=service_type, condition_type__in=["STOP", "PAUSE"]
        )

        for sla_timer_rule in sla_timer_rules:
            expressions = sla_timer_rule.condition.get("expressions", [])
            not_sla_ticket_status_keys = not_sla_ticket_status_keys.union(
                expression_values(expressions)
            )

        return not_sla_ticket_status_keys

    @classmethod
    def init_sla_timer_rule(cls):
        """初始化sla timer rule"""
        if cls.objects.exists():
            print("sla timer rule exists, skip init sla timer rule")
            return
        timer_rules = []
        for service_type, v in list(SERVICE_CATEGORY.items()):
            timer_rules.append(
                cls(
                    service_type=service_type,
                    name="启动",
                    condition_type="START",
                    condition={
                        "type": "all",
                        "expressions": [
                            {
                                "name": "current_status",
                                "value": "RUNNING",
                                "operator": "equal_to",
                            }
                        ],
                    },
                )
            )
            timer_rules.append(
                cls(
                    service_type=service_type,
                    name="启动",
                    condition_type="STOP",
                    condition={"expressions": [], "type": "any"},
                )
            )
            timer_rules.append(
                cls(
                    service_type=service_type,
                    name="启动",
                    condition_type="PAUSE",
                    condition={"type": "any", "expressions": []},
                )
            )
        cls.objects.bulk_create(timer_rules)


class Action(Model):
    """
    Sla升级事件
    """

    action_type = models.CharField(
        "事件类型",
        max_length=LEN_SHORT,
        choices=[
            ("alert", "告警事件"),
            ("update_ticket", "更新单据信息"),
        ],
    )

    config = JSONField("事件配置", help_text="类型详细配置", default=EMPTY_DICT)

    """
        # alert告警配置
        {
            "receivers": "PROCESSORS",
            "notify_rule": "retry",
            "notify_freq": 5,
            "freq_unit": "%",  # ["%", "m", "h", "d"]
            "notify": [
                {
                    "notify_type": "weixin",
                    "notify_template": 1
                },
                {
                    "notify_type": "email",
                    "notify_template": 2
                },
                {
                    "notify_type": "sms",
                    "notify_template": 3
                }
            ]
        }
    """

    class Meta:
        app_label = "sla"
        verbose_name = _("升级事件配置")
        verbose_name_plural = _("升级事件配置")

    def __unicode__(self):
        return "{}".format(self.get_action_type_display())

    def do_alert_action(self, ticket):
        """告警动作"""

        alert_config = bunchify(self.config)

        notify_objs = CustomNotice.objects.filter(
            id__in=[notify["notify_template"] for notify in alert_config.notify]
        )
        # 获取变量上下文：单据/字段
        context = ticket.get_notify_context()

        for notify in notify_objs:
            context.update(action=_(ACTION_CHOICES_DICT.get(notify.action, "待处理")))
            content = Template(notify.content_template).render(**context)
            title = Template(notify.title_template).render(**context)
            receivers = self.receivers(ticket, alert_config.receivers)

            notifier = BaseNotifier(
                title=title, receivers=receivers, message=content
            ).get_notify_class(notify.notify_type)

            notifier.send()

    @staticmethod
    def receivers(ticket, receiver_roles):
        roles = receiver_roles.split(",")
        all_users = set()
        for role in roles:
            if role == "PROCESSORS":
                all_users.update(ticket.real_current_processors)
            elif role == "ADMIN":
                all_users.update(ticket.service_instance.owners.split(","))
            elif role == "HISTORY_HANDLER":
                all_users.update(ticket.history_handlers)
        return ",".join([user for user in all_users if user])


class ActionPolicy(Model):
    """
    升级事件策略
    """

    name = models.CharField(_("策略名称"), max_length=LEN_LONG)
    type = models.IntegerField(_("升级事件类型"), choices=ACTION_POLICY_TYPES, default=1)
    order = models.IntegerField(_("策略顺序"), default=-1)
    condition = JSONField("升级条件", help_text="当达到条件的时候，可以触发不同的动作")
    actions = models.ManyToManyField(Action, help_text=_("处理事件"))

    class Meta:
        app_label = "sla"
        verbose_name = _("升级策略")
        verbose_name_plural = _("升级策略")

    def __unicode__(self):
        return "{}({})".format(self.name, self.id)

    def build_upgrade_rule(self, include_actions=True):
        """构造升级条件
        :param: include_actions: 是否包括升级动作
        """
        # 升级条件
        operator_type = self.condition["type"]
        upgrade_condition = {operator_type: self.condition["expressions"]}

        # 升级动作
        upgrade_actions = []

        if include_actions:
            # 升级动作, 例如: 告警
            for action in self.actions.all():
                upgrade_actions.append(
                    {
                        "name": action.action_type,
                        "params": {
                            "action_id": action.id,
                        },
                    }
                )

        return {
            "conditions": upgrade_condition,
            "actions": upgrade_actions,
        }

    def build_downgrade_rule(self):
        """构造降级条件"""
        # 降级条件
        operator_type = self.condition["type"]

        # 仅适配当前升级条件格式, 升级条件格式一旦修改, 此处逻辑也需要重新适配
        expressions = copy.deepcopy(self.condition["expressions"])
        for expression in expressions:
            expression["operator"] = "less_than_or_equal_to"

        # 降级动作: 取消/减弱单据高亮显示, 由于降级动作是由升级动作映射而来，所以没有匹配的可选动作
        downgrade_actions = [
            {"name": "downgrade_sla", "params": {"sla_status": NORMAL}}
        ]

        return {
            "conditions": {operator_type: expressions},
            "actions": downgrade_actions,
        }


class Sla(Model):
    """
    服务协议
    """

    name = models.CharField(_("Sla名称"), max_length=LEN_LONG)
    policies = models.ManyToManyField(
        help_text=_("服务优先级策略"), to="PriorityPolicy", related_name="p_slas"
    )
    action_policies = models.ManyToManyField(
        help_text=_("服务升级事件策略"), to="ActionPolicy", related_name="a_slas"
    )
    is_enabled = models.BooleanField(_("是否启用"), default=False)
    is_builtin = models.BooleanField(_("是否内置"), default=False)
    is_reply_need = models.BooleanField(_("是否启用响应约定"), default=False)
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    need_auth_grant = True

    auth_resource = {"resource_type": "sla_agreement", "resource_type_name": "SLA 协议"}
    resource_operations = [
        "sla_agreement_view",
        "sla_agreement_edit",
        "sla_agreement_delete",
    ]

    class Meta:
        app_label = "sla"
        verbose_name = _("服务协议")
        verbose_name_plural = _("服务协议")
        ordering = ["-id"]

    def __unicode__(self):
        return "{}({})".format(self.name, self.is_enabled)

    def get_priority_policy(self, priority):
        """根据优先级获取服务策略"""
        return self.policies.filter(priority=priority).first()

    @property
    def service_count(self):
        """应用服务数"""
        return (
            ServiceSla.objects.filter(sla_id=self.id)
            .values("service_id")
            .distinct()
            .count()
        )

    @property
    def service_names(self):
        """应用了该协议的服务的名字"""
        service_ids = ServiceSla.objects.filter(sla_id=self.id).values_list(
            "service_id", flat=True
        )
        return Service.objects.filter(id__in=service_ids).values_list("name", flat=True)

    @property
    def has_response_time(self):
        """是否有约定响应时间"""
        return self.action_policies.filter(
            type__in=[REPLY_WARING, REPLY_TIMEOUT]
        ).exists()

    def get_tickets(self):
        """绑定当前sla的所有单据"""
        from itsm.ticket.models import Ticket
        from itsm.sla_engine.models import SlaTask

        ticket_ids = SlaTask.objects.filter(sla_id=self.id).values_list(
            "ticket_id", flat=True
        )
        return Ticket.objects.filter(id__in=ticket_ids)

    def get_default_policy(self):
        """获取默认优先级"""
        policies = self.policies.values("priority", "handle_time", "handle_unit")
        # 预期解决时长越长, 说明优先级越低
        # 没有以数据字典顺序做为优先级高低的衡量标准, 是因为在"服务协议管理"中, 可能会出现优先级未设定"服务模式"和"约定解决时长"的情况
        lowest_policy = max(
            policies, key=lambda x: x["handle_time"] * TO_SECOND[x["handle_unit"]]
        )
        return lowest_policy["priority"]

    @classmethod
    def init_sla(cls, default_schedules, project_key="0"):
        """初始化服务协议"""
        default_sla_name = ["5*8", "7*24"]
        default_keys = [priority[0] for priority in PRIORITYS]

        if cls.objects.filter(project_key=project_key).exists():
            print("sla exists, skip init")
            return

        sla_list = []

        for index, sla in enumerate(default_sla_name):
            priority_policies = []

            for key in default_keys:
                priority_policy = PriorityPolicy.objects.create(
                    priority=key,
                    schedule=default_schedules[index],
                    handle_time=1,
                    handle_unit="h",
                )
                priority_policies.append(priority_policy)

            sla = cls.objects.create(
                name=sla, is_builtin=True, is_enabled=True, project_key=project_key
            )
            sla.policies.add(*priority_policies)
            sla.save()
            sla_list.append(sla)

        return sla_list


class SlaTicketHighlight(models.Model):
    """
    单据背景颜色
    """

    reply_timeout_color = models.CharField(_("预警单据背景色"), max_length=LEN_SHORT)
    handle_timeout_color = models.CharField(_("超时单据背景色"), max_length=LEN_SHORT)

    @classmethod
    def init_sla_ticket_hightlight(cls):
        if cls.objects.exists():
            print("sla ticket highlight exists, skip init")
            return

        SlaTicketHighlight.objects.create(
            reply_timeout_color=REPLY_TIMEOUT_COLOR,
            handle_timeout_color=HANDLE_TIMEOUT_COLOR,
        )

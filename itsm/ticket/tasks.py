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

import threading
import time
from datetime import date, datetime, timedelta

from celery import Task
from celery.schedules import crontab
from celery.task import periodic_task, task
from django.db.models import Q
from django.db import connection
from django.utils.translation import ugettext as _
from mako.template import Template

from common.log import logger
from common.mymako import render_mako_tostring
from config.default import AUTO_COMMENT_DAYS, CLOSE_NOTIFY

from itsm.component.constants import (
    PROCESS_RUNNING,
    PROCESS_SUSPENDED,
    SLAVE_SYNC_ATTRS,
    ADMIN_SUPERUSER_KEY,
)
from itsm.component.exceptions import ComponentCallError
from itsm.component.utils.basic import now, namedtuplefetchall
from itsm.component.utils.lock import share_lock
from itsm.component.notify import EmailNotifier
from itsm.component.utils.client_backend_query import get_biz_choices
from itsm.iadmin.contants import ACTION_CHOICES_DICT
from itsm.iadmin.models import CustomNotice, SystemSettings
from itsm.sla_engine.constants import TO_SECOND
from itsm.role.models import UserRole
from itsm.service.models import Service
from itsm.ticket.models import TicketToTicket, Ticket
from itsm.task.models import Task as TicketTask
from itsm.ticket.rules import TicketRuleManager
from itsm.ticket.rules.actions import TicketActions
from itsm.ticket.rules.variables import TicketVariables
from itsm.ticket_status.models import StatusTransit


@periodic_task(run_every=crontab(minute=0, hour="*/2"))
def auto_comment():
    """周期任务：为超时的评价添加默认评价"""
    if AUTO_COMMENT_DAYS > 0:
        from itsm.ticket.models import TicketComment

        now = datetime.now()
        logger.info(_("添加默认评价"))
        TicketComment.objects.filter(
            stars=0, create_at__lte=now - timedelta(days=AUTO_COMMENT_DAYS)
        ).update(**{"stars": 4, "comments": "系统默认评价：满意！", "creator": "系统评价"})


@periodic_task(run_every=crontab(hour=0, minute=0, day_of_week=1))
def weekly_statical():
    """每周的单据统计任务"""
    try:
        need_weekly_statical = (
            SystemSettings.objects.get(key="weekly_statical").value == "1"
        )
    except SystemSettings.DoesNotExist:
        # 不存在配置，直接返回
        return

    if not need_weekly_statical:
        # 配置不生效，直接返回
        return

    try:
        receivers = UserRole.objects.get(role_key=ADMIN_SUPERUSER_KEY).members
    except UserRole.DoesNotExist:
        logger.info("统计日报发送错误, 没有超级管理员配置")
        return

    if not receivers:
        logger.info("统计日报发送失败, 没有超级管理员配置")
        return

    # 所有历史记录
    sql_group_by_serivce_template = (
        "select service_id, count(*) as ticket_count from ticket_ticket "
        "where is_deleted = false  {where_condition} group by service_id "
        "order by ticket_count desc;"
    )
    sql_group_by_biz_template = (
        "select bk_biz_id, count(*) as ticket_count from ticket_ticket "
        "where is_deleted = false {where_condition}  group by bk_biz_id "
        "order by ticket_count desc;"
    )

    all_bizs = {int(biz["key"]): biz["name"] for biz in get_biz_choices()}
    all_services = {s.id: s.name for s in Service.objects.all()}
    all_services_include_deleted = {s.id: s.name for s in Service._objects.all()}
    with connection.cursor() as cursor:
        cursor.execute(sql_group_by_serivce_template.format(where_condition=""))
        tickets_group_by_service = namedtuplefetchall(cursor)
        total_tickets_count = sum(
            [item.ticket_count for item in tickets_group_by_service]
        )

    with connection.cursor() as cursor:
        cursor.execute(sql_group_by_biz_template.format(where_condition=""))
        tickets_group_by_biz = namedtuplefetchall(cursor)

    # 上一周记录
    last_week_time = (datetime.now() - timedelta(days=7)).strftime(
        format="%Y-%m-%d %H:%M:%S"
    )
    with connection.cursor() as cursor:
        cursor.execute(
            sql_group_by_serivce_template.format(
                where_condition=" and create_at > '%s'" % last_week_time
            )
        )
        tickets_group_by_service_of_last_week = namedtuplefetchall(cursor)
        total_tickets_count_of_last_week = sum(
            [item.ticket_count for item in tickets_group_by_service_of_last_week]
        )

    with connection.cursor() as cursor:
        cursor.execute(
            sql_group_by_biz_template.format(
                where_condition=" and create_at > '%s'" % last_week_time
            )
        )
        tickets_group_by_biz_of_last_week = namedtuplefetchall(cursor)

    # 增加的服务信息
    sql_new_services = (
        "select name from service_service where create_at >= '%s' and is_deleted = false group by name"
        % last_week_time
    )
    new_services = []  # 新增的服务
    with connection.cursor() as cursor:
        cursor.execute(sql_new_services)
        new_services = [service.name for service in namedtuplefetchall(cursor)]

    # 增加的业务信息
    sql_bizs_last_week_ago = "select bk_biz_id from ticket_ticket where create_at > '%s' and is_deleted = false group by bk_biz_id "  # noqa
    new_bizs = []  # 新增的业务
    with connection.cursor() as cursor:
        cursor.execute(sql_bizs_last_week_ago)
        bizs_last_week_ago = [item.bk_biz_id for item in namedtuplefetchall(cursor)]
        new_bizs = [item.bk_biz_id for item in tickets_group_by_biz_of_last_week]
        new_bizs = [
            "{biz_name}({biz_id})".format(biz_name=all_bizs[biz_id], biz_id=biz_id)
            for biz_id in set(new_bizs).difference(set(bizs_last_week_ago))
        ]

    message = render_mako_tostring("weekly_statical_report.html", locals())

    notifier = EmailNotifier(title="流程服务统计周报", receivers=receivers, message=message)
    try:
        notifier.send()
    except ComponentCallError as error:
        logger.info("统计日报发送失败, 组件错误： %s" % str(error))


@task
def start_pipeline(ticket, **kwargs):
    ticket.start(**kwargs)


class ClonePipelineCallback(Task):
    abstract = True

    def on_success(self, retval, task_id, args, kwargs):
        """克隆流程成功的回调函数"""
        from_ticket_id = args[0].id
        to_ticket_id = args[1].id

        TicketToTicket.objects.filter(
            from_ticket_id=from_ticket_id, to_ticket_id=to_ticket_id
        ).update(is_deleted=True, related_status="UNBIND_SUCCESS", end_at=now())

        # 子单同步母单的单据属性
        slave_ticket = Ticket.objects.get(id=from_ticket_id)
        master_ticket = Ticket.objects.get(id=to_ticket_id)
        for sync_attr in SLAVE_SYNC_ATTRS:
            if hasattr(master_ticket, sync_attr):
                setattr(slave_ticket, sync_attr, getattr(master_ticket, sync_attr))
        slave_ticket.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """克隆流程失败的回调函数"""
        logger.exception(exc)
        TicketToTicket.objects.filter(
            from_ticket_id=args[0].id, to_ticket_id=args[1].id
        ).update(related_status="UNBIND_FAILED")


@task(base=ClonePipelineCallback)
def clone_pipeline(ticket, parent_ticket):
    ticket.clone_pipeline(parent_ticket)


# ================================================================================
# 通知相关后台任务
# ================================================================================


def dispatch_retry_notify_event(ticket, state_id, receivers):
    # 启动后台定时任务
    next_datetime = "%s 00:00:00" % (date.today() + timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    next_send_time = datetime.strptime(next_datetime, "%Y-%m-%d %H:%M:%S") + timedelta(
        hours=ticket.flow.notify_freq / 3600
    )

    countdown = int((next_send_time - datetime.now()).total_seconds())
    retry_notify.apply_async(args=[ticket, state_id, receivers], countdown=countdown)


@task
def retry_notify(ticket, state_id, receivers):
    # 每次发通知前查看一下当前单据的最新状态，并更新之后的单据对象
    ticket.refresh_from_db()
    logger.info(_("当前单据的状态, current_status={}".format(ticket.current_status)))

    # 需要停止发送消息的状态列表
    status = ["REVOKED", "TERMINATED", "FINISHED"]
    if ticket.current_status in status or not ticket.is_current_step(state_id):
        logger.info(_("当前任务已过期, ticket_id={}, state_id={}".format(ticket.id, state_id)))
    else:
        # 当前状态存在，才发送通知
        logger.info(
            _("开始定时发送通知, ticket_id={}, state_id={}".format(ticket.id, state_id))
        )
        ticket.notify(state_id, receivers)


@task
def notify_task(ticket, receivers, message, action, **kwargs):
    """发送通知"""
    task_id = kwargs.get("task_id")

    # 关闭通知服务
    if CLOSE_NOTIFY == "close":
        return

    # 不通知
    if ticket.flow.notify_rule == "NONE" or not receivers:
        return

    # 根据流程设定的通知方式通知
    for _notify in ticket.flow.notify.all():
        if task_id:
            custom_notify = CustomNotice.objects.get(
                action=action, notify_type=_notify.type, used_by="TASK"
            )
        else:
            custom_notify = CustomNotice.objects.get(
                action=action, notify_type=_notify.type
            )

        # 获取单据上下文
        context = ticket.get_notify_context()
        context.update(
            message=message, action=_(ACTION_CHOICES_DICT.get(action, "待处理")), **kwargs
        )

        # 获取任务上下文
        if task_id:
            try:
                task = TicketTask.objects.get(id=task_id)
                context.update(
                    {item["key"]: item["value"] for item in task.get_output_context()}
                )
            except TicketTask.DoesNotExist:
                return

        try:
            content = Template(custom_notify.content_template).render(**context)
            title = Template(custom_notify.title_template).render(**context)
            logger.info(
                "[tasks->notify_task] is executed, title={}, receivers={}, ticket_id={}, "
                "custom_notify={}".format(title, receivers, ticket.id, custom_notify)
            )
            _notify.send_message(title, receivers, content, ticket_id=ticket.id)
        except NameError as error:
            logger.error(
                "context render failed, error: %s, title: %s->%s, content: %s->%s"
                % (
                    str(error),
                    context,
                    custom_notify.title_template,
                    context,
                    custom_notify.content_template,
                )
            )
        except ComponentCallError as error:
            logger.warning("send notify failed, error: %s" % str(error))
        except Exception as e:
            logger.exception("send email exception: %s" % str(e))


@periodic_task(run_every=(crontab(minute="*/1")), ignore_result=True)
@share_lock()
def status_auto_transit():
    """单据状态自动流转"""
    from itsm.ticket.models import Ticket, TicketStatus

    start_time = time.time()

    tickets_status = TicketStatus.objects.all().only(
        "id", "service_type", "key", "flow_status"
    )

    status_map = {"{}_{}".format(ts.service_type, ts.key): ts for ts in tickets_status}

    # 构造单据查询条件: 在指定服务类型下, 单据状态对应的流程状态为运行中/挂起
    condition = get_tickets_condition(tickets_status)
    tickets = Ticket.objects.filter(condition).only(
        "id", "service_type", "pre_status", "current_status"
    )

    auto_transits_map = get_auto_transits()

    threads = []
    for ticket in tickets:
        from_status = status_map[
            "{}_{}".format(ticket.service_type, ticket.current_status)
        ].id
        auto_transits = auto_transits_map.get(
            "{}_{}".format(ticket.service_type, from_status)
        )
        if auto_transits:
            rules = build_auto_transit_rules(ticket, auto_transits)
            run_func = TicketRuleManager(
                ticket, rules, TicketVariables, TicketActions
            ).run
            threads.append(threading.Thread(target=run_func))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    logger.info("status_auto_transit elapsed: %s" % (end_time - start_time))


def get_tickets_condition(tickets_status):
    con = Q()
    for ts in tickets_status:
        if ts.flow_status in [PROCESS_RUNNING, PROCESS_SUSPENDED]:
            sub_con = Q()
            sub_con.connector = "AND"
            sub_con.children.append(("current_status", ts.key))
            sub_con.children.append(("service_type", ts.service_type))
            con.add(sub_con, "OR")
    return con


def get_auto_transits():
    auto_transits = StatusTransit.objects.filter(is_auto=True).only(
        "service_type", "from_status_id", "threshold", "threshold_unit"
    )

    auto_transits_map = {}
    for at in auto_transits:
        auto_transits_map.setdefault(
            "{}_{}".format(at.service_type, at.from_status_id), []
        ).append(at)
    return auto_transits_map


def build_auto_transit_rules(ticket, auto_transits):
    """构造指定单据的状态流转规则"""
    # 若出现同一个来源状态能够自动流转到多个单据状态, 则取阈值最小的自动流转
    sorted_auto_transits = sorted(
        auto_transits, key=lambda x: x.threshold * TO_SECOND[x.threshold_unit]
    )
    auto_transit = sorted_auto_transits[0]

    rules = [
        {
            "conditions": {
                "all": [
                    {
                        "name": "current_status",
                        "operator": "equal_to",
                        "value": ticket.current_status,
                    },
                    {
                        "name": "service_type",
                        "operator": "equal_to",
                        "value": ticket.service_type,
                    },
                    {
                        "name": "status_keep_time",
                        "operator": "greater_than_or_equal_to",
                        "value": auto_transit.threshold
                        * TO_SECOND[auto_transit.threshold_unit],
                    },
                ]
            },
            "actions": [
                {
                    "name": "auto_transit",
                    "params": {"to_status": auto_transit.to_status.key},
                }
            ],
        }
    ]
    return rules

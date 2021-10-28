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
from django.db.models import Q
from django.utils.translation import gettext as _
from itsm.component.constants import TASK_PI_PREFIX, SOURCE_TICKET, MANUAL
from itsm.ticket_status.models import TicketStatus
from itsm.service.models import Service
from .models import StatusTransitLog, Ticket, TicketEventLog


def pipeline_end_handler(sender, root_pipeline_id, **kwargs):
    """
    流程结束之后的处理器
    """
    if str(root_pipeline_id).startswith(TASK_PI_PREFIX):
        task_pipeline_end_handler(root_pipeline_id, **kwargs)
    else:
        ticket_pipeline_end_handler(root_pipeline_id, **kwargs)


def task_pipeline_end_handler(root_pipeline_id, **kwargs):
    """任务流程结束之后的处理器"""
    pass


def ticket_pipeline_end_handler(root_pipeline_id, **kwargs):
    """单据流程结束之后的处理器"""
    ticket = Ticket.objects.get(id=root_pipeline_id)
    ticket.do_before_end_pipeline(by_flow=kwargs.get("by_flow"))


def after_ticket_created(sender, instance, created, *args, **kwargs):
    """单据创建后的处理器"""
    if created:
        start_status = TicketStatus.objects.get(service_type=instance.service_type, is_start=True)
        StatusTransitLog.objects.create(ticket_id=instance.id, from_status="DRAFT", to_status=start_status.key)


def before_ticket_status_updated(sender, instance, *args, **kwargs):
    """单据状态修改前的处理器"""
    # 更新ticket模型字段触发
    if not instance.id:
        return
    ticket = Ticket._objects.get(id=instance.id)
    # 单据状态发生修改
    if ticket.current_status != instance.current_status:
        StatusTransitLog.objects.create(
            ticket_id=instance.id, from_status=ticket.current_status, to_status=instance.current_status
        )


def create_trigger_action_log(sender, instance, **kwargs):
    if instance.source_type != SOURCE_TICKET or instance.action_schema.operate_type != MANUAL:
        # 如果非单据的触发器， 不做操作记录
        return
    ticket = Ticket.objects.get(id=instance.source_id)
    result = "成功" if instance.status == "SUCCEED" else "失败"
    message = "{operator} {action} 【{name}】. 处理结果: %s {detail_message}" % result

    # 由于name的渲染是通过from_state_name来的，所以直接把响应动作的名称赋值给他
    TicketEventLog.objects.create_log(
        ticket=ticket,
        state_id=0,
        log_operator=instance.operator,
        message=message,
        action=_("处理"),
        from_state_name=instance.display_name,
        fields=instance.get_fields(flat=True),
        detail_message=instance.ex_data[0].get('message') or "",
    )


class ProjectOperationalData:
    """项目级别的运营数据"""

    def __init__(self, service_id=None, scope=None, project_key=None):
        """
        当project_key为None时，本类的方法返回值均为全局级别的运营数据
        当project_key为指定值时，本类的方法返回值为指定项目下的运营数据
        @param service_id: 服务id
        @param scope: 时间范围
        @param project_key: 项目唯一标示
        """
        self.project_queryset = Q()
        self.service_id = service_id
        self.scope = scope
        if project_key:
            self.project_queryset = Q(project_key=project_key)

    def get_ticket_count(self):
        """获取单据总数"""
        return Ticket.get_count(self.service_id, self.scope, self.project_queryset)

    def get_service_count(self):
        """"获取服务总数"""
        return Service.get_count(self.scope, self.project_queryset)

    def get_biz_count(self):
        """获取业务总数"""
        return Ticket.get_biz_count(self.service_id, self.scope, self.project_queryset)

    def get_ticket_user_count(self):
        """获取用户总数"""
        return Ticket.get_ticket_user_count(self.service_id, self.scope, self.project_queryset)

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

import logging

from django.conf import settings
from django.core.cache import cache

from itsm.component.constants import PROCESS_COUNT, APPROVAL_STATE
from itsm.component.utils.bunch import bunchify
from itsm.meta.services.notice_filter import notice_filter_service
from itsm.ticket.models import Ticket, Status, SignTask
from pipeline.component_framework.component import Component
from .itsm_sign import ItsmSignService
from .tasks import auto_approve, auto_approve_by_approved_user

logger = logging.getLogger("celery")


class ItsmApprovalService(ItsmSignService):
    __need_schedule__ = True
    __multi_callback_enabled__ = True

    def execute(self, data, parent_data):
        """进入审批节点的准备"""

        if super(ItsmSignService, self).execute(data, parent_data):
            return True

        logger.info(
            "itsm_sign execute: data={}, parent_data={}".format(
                data.inputs, parent_data.inputs
            )
        )
        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id
        ticket = Ticket.objects.get(id=ticket_id)

        variables, finish_condition, code_key = ticket.do_before_enter_sign_state(
            state_id, by_flow=self.by_flow
        )
        is_multi = ticket.flow.get_state(state_id)["is_multi"]
        user_count = str(self.get_user_count(ticket_id, state_id)) if is_multi else "1"

        service_approval_blacklist = (
            notice_filter_service.get_service_approval_blacklist()
        )
        if str(ticket.service_id) not in service_approval_blacklist:
            # 如果service_id不在service_approval_blacklist中，则创建moa单据
            ticket.create_moa_ticket(state_id)
        else:
            # 否则，记录日志
            logger.info(
                f"Bypass create_moa_ticket due to service id {ticket.service_id} is in service_approval_blacklist"
            )

        # 如果是普通的审批节点，则自动生成条件
        if not is_multi:
            finish_condition = self.get_finish_condition(user_count)

        # Set outputs to data
        data.set_outputs("variables", variables)
        data.set_outputs("finish_condition", finish_condition)
        data.set_outputs("code_key", code_key)
        node_status = Status.objects.get(ticket_id=ticket.id, state_id=state_id)

        if self.is_skip_approve(ticket, state_id, node_status):
            node_status.processors_type = "PERSON"
            node_status.processors = "system"
            node_status.save()
            msg = "检测到当前处理人为空，系统自动过单"
            callback_data = {
                "fields": ticket.get_approve_fields(state_id, msg),
                "ticket_id": ticket_id,
                "source": "SYS",
                "operator": "system",
                "state_id": state_id,
            }
            logger.info(
                "检测到当前单据处理人为空，系统即将准备自动过单, ticket_id={}, state_id={}, callback_data={}".format(
                    ticket.id, state_id, callback_data
                )
            )
            activity_id = ticket.activity_for_state(state_id)
            auto_approve.apply_async(
                (node_status.id, "system", activity_id, callback_data),
                countdown=settings.AUTO_APPROVE_TIME,
            )  # AUTO_APPROVE_TIME秒之后自动回调
            return True

        # 获取当前节点的可以审批的审批人
        fast_approval_notify_receivers = node_status.get_processor_in_sign_state()
        fast_approval_notify_receivers_list = fast_approval_notify_receivers.split(",")

        # 检测流程和节点级别是否开启了自动过单
        is_flow_auto_approve = self.is_auto_approve(ticket, node_status)
        is_node_auto_approve, intersecting_processors = self.is_approved_auto_approve(
            ticket, state_id, node_status
        )

        # 只有当流程级别的自动过单开启且提单人不在历史审批人交集中时才使用流程级别的自动过单
        # 这里只是给提单人的审批任务进行了自动过单
        if is_flow_auto_approve and (ticket.creator not in intersecting_processors):
            msg = "检测到当前处理人包含提单人，系统自动过单"
            callback_data = {
                "fields": ticket.get_approve_fields(state_id, msg),
                "ticket_id": ticket_id,
                "source": "SYS",
                "operator": ticket.creator,
                "state_id": state_id,
            }
            logger.info(
                "检测到当前单据开启了自动过单，即将准备自动过单, ticket_id={}, state_id={}, callback_data={}".format(
                    ticket.id, state_id, callback_data
                )
            )
            activity_id = ticket.activity_for_state(state_id)
            auto_approve.apply_async(
                (node_status.id, ticket.creator, activity_id, callback_data),
                countdown=settings.AUTO_APPROVE_TIME,
            )  # AUTO_APPROVE_TIME秒之后自动回调

            if ticket.creator in fast_approval_notify_receivers_list:
                fast_approval_notify_receivers_list.remove(ticket.creator)

        # 如果节点级别开启了自动审批通过
        if is_node_auto_approve and intersecting_processors:
            msg = "检测到当前处理人已审批同意过此单据，系统自动过单"
            activity_id = ticket.activity_for_state(state_id)
            # 如果不是多人审批
            if not is_multi:
                #  只取一个processor
                processor = intersecting_processors[0]
                callback_data = {
                    "ticket_id": ticket_id,
                    "fields": ticket.get_approve_fields(state_id, msg),
                    "state_id": state_id,
                    "operator": processor,
                    "source": "SYS",
                }
                logger.info(
                    "检测到当前节点开启了已审批同意用户自动同意，即将准备自动过单，非多人审批场景, ticket_id={}, state_id={}, callback_data={}".format(
                        ticket.id, state_id, callback_data
                    )
                )
                auto_approve_by_approved_user.apply_async(
                    (node_status.id, processor, activity_id, callback_data),
                    countdown=settings.AUTO_APPROVE_TIME,  # AUTO_APPROVE_TIME秒之后自动回调
                )
                if processor in fast_approval_notify_receivers_list:
                    fast_approval_notify_receivers_list.remove(processor)
            # 如果是多人审批
            else:
                logger.info(
                    "多人审批场景，ticket_id={}, state_id={}, intersecting_processors={}".format(
                        ticket.id, state_id, intersecting_processors
                    )
                )
                for processor in intersecting_processors:
                    callback_data = {
                        "ticket_id": ticket_id,
                        "fields": ticket.get_approve_fields(state_id, msg),
                        "state_id": state_id,
                        "operator": processor,
                        "source": "SYS",
                    }
                    logger.info(
                        "检测到当前节点开启了已审批同意用户自动同意，即将准备自动过单，多人审批场景, ticket_id={}, state_id={}, callback_data={}".format(
                            ticket.id, state_id, callback_data
                        )
                    )
                    auto_approve_by_approved_user.apply_async(
                        (node_status.id, processor, activity_id, callback_data),
                        countdown=settings.AUTO_APPROVE_TIME,  # AUTO_APPROVE_TIME秒之后自动回调
                    )
                    if processor in fast_approval_notify_receivers_list:
                        fast_approval_notify_receivers_list.remove(processor)

        ticket.notify_fast_approval(
            state_id, ",".join(fast_approval_notify_receivers_list)
        )
        logger.info(
            f"notify_fast_approval: ticket_id: {ticket_id}, state_id: {state_id}, "
            f"processors: {','.join(fast_approval_notify_receivers_list)}"
        )
        return True

    def is_skip_approve(self, ticket, state_id, node_status):
        processors = node_status.get_processors()
        state = ticket.state(state_id)
        if state.get("is_allow_skip", False) and len(processors) == 0:
            return True
        return False

    def is_auto_approve(self, ticket, node_status):
        sign_processors = node_status.get_processor_in_sign_state()
        sign_processors_list = sign_processors.split(",")
        if ticket.flow.is_auto_approve and ticket.creator in sign_processors_list:
            return True
        return False

    def is_approved_auto_approve(self, ticket, state_id, node_status):
        state = bunchify(ticket.state(state_id))
        if state.get("extras") and state.extras.get(
            "enable_auto_approve_if_previously_approved"
        ):
            # 获取当前节点审批人
            sign_processors = node_status.get_processor_in_sign_state()
            sign_processors_list = sign_processors.split(",")

            # 获取之前审批通过的审批人
            approval_status = Status.objects.filter(
                ticket_id=ticket.id, type=APPROVAL_STATE
            )
            signed_tasks = SignTask.objects.filter(
                status_id__in=list(approval_status.values_list("id", flat=True)),
                is_passed=True,
            )
            approved_processors = list(signed_tasks.values_list("processor", flat=True))

            # 取出他们的交集
            intersecting_processors = list(
                set(sign_processors_list).intersection(set(approved_processors))
            )
            return True, intersecting_processors
        else:
            return False, []

    @staticmethod
    def get_finish_condition(user_count):
        finish_condition = {
            "key": PROCESS_COUNT,
            "condition": ">=",
            "value": user_count,
        }
        return finish_condition

    @staticmethod
    def get_user_count(ticket_id, state_id):
        node_status = Status.objects.get(ticket_id=ticket_id, state_id=state_id)
        user_list = node_status.get_user_list()
        return len(user_list)

    @staticmethod
    def do_before_exit(ticket, state_id, operator):
        ticket.do_before_exit_sign_state(state_id)
        ticket.close_moa_ticket(state_id, operator)

    def final_execute(self, node_status, operator):
        super(ItsmApprovalService, self).final_execute(node_status, operator)
        cache.delete(
            "approval_status_{}_{}_{}".format(
                operator, node_status.ticket_id, node_status.state_id
            )
        )

    def outputs_format(self):
        return []


class ItsmApprovalComponent(Component):
    name = "审批节点原子"
    code = "itsm_approval_node"
    bound_service = ItsmApprovalService

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

import logging
from itsm.ticket.models import Ticket
from pipeline.component_framework.component import Component

from .itsm_base_service import ItsmBaseService

logger = logging.getLogger("celery")


class ItsmService(ItsmBaseService):
    __need_schedule__ = True
    __multi_callback_enabled__ = False

    def execute(self, data, parent_data):
        if super(ItsmService, self).execute(data, parent_data):
            return True

        logger.info("itsm_approve execute: data={}, parent_data={}".format(data.inputs, parent_data.inputs))

        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id

        # 节点信息准备
        ticket = Ticket._objects.get(id=ticket_id)
        ticket.do_before_enter_state(state_id, by_flow=self.by_flow)

        return True

    def schedule(self, data, parent_data, callback_data=None):
        """
            注意：只能手动回调一次
            True/None -> 下一个节点
            False-> 失败在当前节点
        """

        logger.info(
            "schedule: data={}, parent_data={}, callback_data={}".format(data.inputs, parent_data.inputs, callback_data)
        )

        # 扩展多种操作的事情
        ticket_id = callback_data["ticket_id"]
        state_id = callback_data["state_id"]
        operator = callback_data["operator"]
        fields = callback_data["fields"]
        source = callback_data["source"]

        ticket = Ticket.objects.get(id=ticket_id)

        ticket.do_in_state(state_id, fields, operator, source)

        # 输出字段变量和基础模型变量到pipeline
        logger.info("\n-------  itsm_approve add table fields to pipeline data  ----------\n")
        for field in ticket.get_output_fields(state_id):
            logger.info('set_output: "params_{}" = {}'.format(field["key"], field["value"]))
            data.set_outputs("params_%s" % field["key"], field["value"])

        ticket.do_before_exit_state(state_id, operator)

        return True

    def outputs_format(self):
        return []


class ItsmComponent(Component):
    name = "审批原子"
    code = "itsm_approve"
    bound_service = ItsmService

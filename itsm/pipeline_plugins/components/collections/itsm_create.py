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

from .itsm_approve import ItsmService

logger = logging.getLogger("celery")


class TicketCreateService(ItsmService):
    __need_schedule__ = True

    def execute(self, data, parent_data):
        logger.info("itsm_create execute: data=%s, parent_data=%s" % (data.inputs, parent_data.inputs))
        if parent_data.outputs.get("is_first_execute", True) is True:
            if parent_data.inputs.get("is_cloning", False) is True:
                parent_data.set_outputs("is_cloning", True)
                super(TicketCreateService, self).execute(data, parent_data)
            else:
                state_id = data.inputs.state_id
                ticket_id = parent_data.inputs.ticket_id
                current_ticket = Ticket._objects.get(id=ticket_id)
                current_ticket.node_status.filter(state_id=state_id).update(
                    by_flow=current_ticket.first_transition.get("id", "")
                )
                self.set_outputs(data, current_ticket, state_id)

            return True
        return super(TicketCreateService, self).execute(data, parent_data)

    def schedule(self, data, parent_data, callback_data=None):
        logger.info("itsm_create schedule: data=%s, parent_data=%s" % (data.inputs, parent_data.inputs))
        if parent_data.outputs.get("is_first_execute", True) is False:
            return super(TicketCreateService, self).schedule(data, parent_data, callback_data)

        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id

        # 输出字段变量和基础模型变量到pipeline
        logger.info("\n-------  itsm_auto add table fields to pipeline data  ----------\n")
        ticket = Ticket.objects.get(id=ticket_id)
        for field in ticket.get_output_fields(state_id):
            logger.info('set_output: "params_{}" = {}'.format(field["key"], field["value"]))
            data.set_outputs("params_%s" % field["key"], field["value"])
        parent_data.set_outputs("is_first_execute", False)

        return True

    def need_schedule(self, pipeline_data=None):
        """
        编写特殊逻辑：克隆的时候跳过调度，直至恢复
        """
        if pipeline_data is not None and pipeline_data.outputs.get("is_first_execute", True) is True:
            pipeline_data.set_outputs("is_first_execute", False)
            return False
        return super(TicketCreateService, self).need_schedule(pipeline_data)

    def outputs_format(self):
        return []


class ItsmComponent(Component):
    name = "提单原子"
    code = "itsm_create"
    bound_service = TicketCreateService

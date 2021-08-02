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
from django_bulk_update.helper import bulk_update

from itsm.ticket.models import Ticket, TicketGlobalVariable
from pipeline.core.flow.activity import Service

logger = logging.getLogger('celery')


class ItsmBaseService(Service):
    __need_schedule__ = True

    def execute(self, data, parent_data):
        logger.info('ItsmBaseService execute: data={}, parent_data={}'.format(data.inputs, parent_data.inputs))
        is_cloning = parent_data.outputs.get("is_cloning", False)
        if not is_cloning:
            return False

        # 克隆status
        # state_id是flow的节点ID, 母子流程的state_id都是相同的(来源同一个工单流程版本)
        state_id = data.inputs.state_id
        parent_ticket_id = parent_data.inputs.parent_ticket_id
        ticket_id = parent_data.inputs.ticket_id

        parent_ticket = Ticket.objects.get(id=parent_ticket_id)
        current_ticket = Ticket.objects.get(id=ticket_id)

        current_status = parent_ticket.status(state_id=state_id)

        # 若被copy的节点正在执行, 表示克隆流程已经和母流程进度一致, 所以立即解除clone模式
        if current_status.status in current_status.RUNNING_STATUS:
            parent_data.set_outputs("is_cloning", False)
            return False

        # 输出变量
        fields_kv = {item["key"]: item["value"] for item in current_status.fields}

        if int(current_ticket.first_state_id) != int(state_id):
            self.update_status_and_fields(current_status, current_ticket, parent_ticket_id, state_id, fields_kv)

        self.set_outputs(data, current_ticket, state_id, fields_kv)
        return True

    @staticmethod
    def update_status_and_fields(current_status, current_ticket, parent_ticket_id, state_id,
                                 fields_kv=None):
        """子单复制母单的节点和字段"""
        # 代码规范兼容
        if fields_kv is None:
            fields_kv = {}
        ticket_id = current_ticket.id
        current_status.id = None
        current_status.ticket_id = current_ticket.id
        current_status.save()
        current_ticket.node_status.add(current_status)

        state_fields = current_ticket.fields.filter(key__in=fields_kv.keys())
        for field in state_fields:
            field._value = fields_kv[field.key]

        global_variables = TicketGlobalVariable.objects.filter(ticket_id=parent_ticket_id, state_id=state_id)
        TicketGlobalVariable.objects.filter(ticket_id=ticket_id, state_id=state_id).delete()
        for variable in global_variables:
            variable.id = None
            variable.ticket_id = ticket_id
            variable.save()
        bulk_update(state_fields, update_fields=["_value"])

    def need_schedule(self, pipeline_data=None):
        """
        编写特殊逻辑：克隆的时候跳过调度，直至恢复
        """

        if pipeline_data:
            is_cloning = pipeline_data.outputs.get("is_cloning", False)
            if is_cloning:
                return False

        return getattr(self, self.schedule_determine_attr, False)

    def outputs_format(self):
        return []

    def set_outputs(self, data, ticket, state_id, fields_kv=None):
        # 默认的输出字段变量和基础模型变量到pipeline
        if fields_kv is None:
            fields_kv = {}
        logger.info('\n-------  ItsmBaseService add table fields to pipeline data  ----------\n')
        for field in ticket.get_output_fields(state_id):
            value = field['value'] if fields_kv.get(field['key']) is None else fields_kv.get(field['key'])
            logger.info('set_output: "params_{}" = {}'.format(field['key'], value))
            data.set_outputs("params_%s" % field['key'], value)

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

from itsm.component.constants import (
    DISTRIBUTING,
    FINISHED,
    RECEIVING,
    REJECT_SELECT_KEY,
    RUNNING,
    SUSPEND,
)
from itsm.component.utils.bk_bunch import bunchify
from itsm.ticket.models import Status, Ticket
from itsm.workflow.models import TRANSITION_OPERATE
from pipeline.component_framework.component import Component

from .itsm_approve import ItsmService


class ItsmMigrateService(ItsmService):
    __need_schedule__ = True
    __schedule_finish__ = False

    def execute(self, data, parent_data):
        print('itsm_migrate execute: data=%s, parent_data=%s' % (data.inputs, parent_data.inputs))

        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id

        if Status._objects.filter(state_id=state_id, ticket_id=ticket_id).exists():
            parent_data.set_outputs("is_migrate", False)
            return super(ItsmMigrateService, self).execute(data, parent_data)

        ticket = Ticket.objects.get(id=ticket_id)

        # 当前节点是提单节点
        if ticket.current_state_id == str(state_id):
            parent_data.set_outputs("is_migrate", False)
        else:
            parent_data.set_outputs("is_migrate", True)
        state = bunchify(ticket.state(state_id))
        # fetch state's final process log
        log = ticket.logs.filter(from_state_id=state_id).last()
        # add node_status
        if parent_data.outputs.get('is_migrate', False) is True:
            status = FINISHED
        elif parent_data.inputs.get('old_ticket_status') in [RUNNING, RECEIVING, DISTRIBUTING]:
            status = RUNNING
        elif parent_data.inputs.get('old_ticket_status') == SUSPEND:
            status = SUSPEND
        else:
            status = RUNNING
        defaults = {
            "bk_biz_id": ticket.bk_biz_id,
            "name": state.name,
            "action_type": TRANSITION_OPERATE,
            "distribute_type": 'PROCESS',
            "processors": log.processors,
            "processors_type": log.processors_type,
            "status": status,
            "can_deliver": state.can_deliver,
            "delivers": state.delivers,
            "delivers_type": state.delFivers_type,
            "assignors": state.assignors,
            "assignors_type": state.assignors_type,
            "can_terminate": state.is_terminable,
        }

        # print state_id, defaults
        status, created = Status._objects.get_or_create(
            defaults=defaults, **{"state_id": state_id, "ticket_id": ticket_id}
        )
        ticket.node_status.add(status)
        # 菱形/打回变量值的设置
        for var in state.variables['outputs']:
            if 'default' in var:
                data.set_outputs("params_%s" % var['key'], var['default'])
            elif REJECT_SELECT_KEY in var['key']:
                data.set_outputs("params_%s" % var['key'], 'NO')
        # update log
        ticket.logs.filter(from_state_id=state_id).update(status=status.id)
        data.set_outputs('ticket_first_state_id', ticket.first_state_id)
        return True

    def schedule(self, data, parent_data, callback_data=None):
        print('itsm_migrate schedule: data=%s, parent_data=%s' % (data.inputs, parent_data.inputs))

        if parent_data.outputs.get('is_migrate', False) is True:
            return True
        return super(ItsmMigrateService, self).schedule(data, parent_data, callback_data)

    def outputs_format(self):
        return []


class ItsmMigrateComponent(Component):
    name = '审批迁移原子'
    code = 'itsm_migrate'
    bound_service = ItsmMigrateService

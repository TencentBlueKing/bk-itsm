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

from itsm.component.constants import NODE_APPROVE_RESULT
from itsm.ticket.models import Ticket, Status, TicketGlobalVariable, SignTask
from pipeline.component_framework.component import Component

from .itsm_base_service import ItsmBaseService

logger = logging.getLogger("celery")


class ItsmSignService(ItsmBaseService):
    __need_schedule__ = True
    __multi_callback_enabled__ = True

    def execute(self, data, parent_data):
        """进入会签节点的准备"""

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

        # Set outputs to data
        data.set_outputs("variables", variables)
        data.set_outputs("finish_condition", finish_condition)
        data.set_outputs("code_key", code_key)

        return True

    @staticmethod
    def update_node_variables(ticket_id, variables, key_value):
        for variable in variables:
            key = variable["key"]

            TicketGlobalVariable.objects.filter(ticket_id=ticket_id, key=key).update(
                value=key_value.get(key, "")
            )

    def schedule(self, data, parent_data, callback_data=None):
        """
        会签任务回调处理
        """
        try:
            logger.info(
                "schedule: data={}, parent_data={}, callback_data={}, data.outputs={}".format(
                    data.inputs, parent_data.inputs, callback_data, data.outputs
                )
            )

            ticket_id = callback_data["ticket_id"]
            state_id = callback_data["state_id"]
            operator = callback_data["operator"]
            fields = callback_data["fields"]
            source = callback_data["source"]

            variables = data.outputs.get("variables")
            finish_condition = data.outputs.get("finish_condition")
            code_key = data.outputs.get("code_key")
            ticket = Ticket.objects.get(id=ticket_id)
            node_status = Status.objects.get(ticket_id=ticket_id, state_id=state_id)
            try:
                ticket.do_in_sign_state(node_status, fields, operator, source)
                ticket.update_ticket_fields(fields=fields)
                # Determine if current node is finished
                key_value = self.get_key_value(node_status, ticket, code_key)
                if self.task_is_finished(
                    node_status, finish_condition, key_value, code_key
                ):
                    # When node finished set output to data
                    logger.info(
                        "\n-------  itsm_sign add table fields to pipeline data  ----------\n"
                    )
                    self.update_node_variables(ticket_id, variables, key_value)
                    for field in ticket.get_output_fields(state_id):
                        logger.info(
                            'set_output: "params_{}" = {}'.format(
                                field["key"], field["value"]
                            )
                        )
                        data.set_outputs("params_%s" % field["key"], field["value"])

                    self.do_before_exit(ticket, state_id, operator)
                    self.finish_schedule()
            finally:
                self.final_execute(node_status, operator)
                ticket.set_current_processors()
        except Exception as err:
            logger.error("ItsmSignService schedule err, reason is {}".format(err))
            raise err

        return True

    @staticmethod
    def get_key_value(node_status, ticket, code_key):
        if node_status.state["type"] == "SIGN":
            key_value = node_status.get_sign_key_value(ticket, code_key)
            return key_value

        approver_key_value = node_status.get_appover_key_value(code_key)
        is_multi = node_status.state["is_multi"]
        if not is_multi:
            key_value = {}
            reject_count = node_status.sign_reject_count()
            if reject_count > 0:
                key_value[code_key[NODE_APPROVE_RESULT]] = "false"
            key_value.update(approver_key_value)
            return key_value

        key_value = node_status.get_sign_key_value(ticket, code_key)
        reject_count = node_status.sign_reject_count()
        if NODE_APPROVE_RESULT in code_key:
            if reject_count > 0:
                key_value[code_key[NODE_APPROVE_RESULT]] = "false"
            else:
                key_value[code_key[NODE_APPROVE_RESULT]] = "true"
        key_value.update(approver_key_value)
        return key_value

    @staticmethod
    def task_is_finished(node_status, finish_condition, key_value, code_key):
        if node_status.state["type"] == "SIGN":
            is_finished = node_status.sign_is_finished(finish_condition, key_value)
            return is_finished

        is_multi = node_status.state["is_multi"]
        if not is_multi:
            if key_value.get(code_key[NODE_APPROVE_RESULT]) == "false":
                return True
            process_count = node_status.sign_process_count()
            is_finished = (
                True if process_count >= int(finish_condition["value"]) else False
            )
            if is_finished:
                key_value[code_key[NODE_APPROVE_RESULT]] = "true"
            return is_finished

        is_finished = node_status.sign_is_finished(finish_condition, key_value)
        return is_finished

    @staticmethod
    def do_before_exit(ticket, state_id, operator):
        ticket.do_before_exit_sign_state(state_id)

    def final_execute(self, node_status, operator):
        SignTask.objects.filter(status_id=node_status.id, processor=operator).update(
            status="FINISHED"
        )

    def outputs_format(self):
        return []


class ItsmSignComponent(Component):
    name = "会签原子"
    code = "itsm_sign"
    bound_service = ItsmSignService

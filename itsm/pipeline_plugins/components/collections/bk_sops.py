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
from itsm.component.constants import SYSTEM_OPERATE, TRANSITION_OPERATE, NODE_FAILED
from itsm.component.esb.esbclient import client_backend
from itsm.ticket.serializers import StatusSerializer
from itsm.ticket.models import Ticket, TicketGlobalVariable
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import StaticIntervalGenerator

from .itsm_base_service import ItsmBaseService

logger = logging.getLogger("celery")


class BkOpsService(ItsmBaseService):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(3)

    def prepare_task_params(self, state, ticket, sops_info):
        values = ticket.get_output_fields(return_format="dict")
        if sops_info["bk_biz_id"]["value_type"] == "variable":
            bk_biz_id = values.get(sops_info["bk_biz_id"]["value"], 0)
        else:
            bk_biz_id = sops_info["bk_biz_id"]["value"]

        constants = sops_info["constants"]
        for constant in constants:
            if constant["value_type"] == "variable":
                constant["value"] = values.get(constant["value"], "")
        constants = {constant["key"]: constant["value"] for constant in constants}

        exclude_task_nodes_id = sops_info.get("exclude_task_nodes_id", [])
        template_source = sops_info.get("template_source", "common")

        params = {
            "bk_biz_id": bk_biz_id,
            "template_id": str(sops_info["template_id"]),
            "flow_type": "common",
            "template_source": template_source,
            "name": "ITSM-" + state["name"],
            "constants": constants,
            "exclude_task_nodes_id": exclude_task_nodes_id,
            # return raw response data
            "__raw": True,
        }

        return params

    def update_info(self, current_node, sops_result, **kwargs):
        """更新任务上下文"""

        sops_result.value = kwargs.get("result", "")
        sops_result.save()

        current_node.contexts.update(**kwargs)
        current_node.save()

    def do_exit_plugins(self, result, **kwargs):
        if not result:
            current_node = kwargs.get("current_node")
            sops_result = kwargs.get("sops_result")
            error_message = kwargs.get("error")
            processors = kwargs.get("processors")
            error_message_template = kwargs.get("error_message_template")
            ticket = kwargs.get("ticket")
            state_id = kwargs.get("state_id")
            self.update_info(
                current_node, sops_result, error_message=error_message, result=result
            )
            current_node.set_failed_status(
                operator=processors,
                message=error_message_template,
                detail_message=error_message,
            )
            ticket.node_status.filter(state_id=state_id).update(
                action_type=TRANSITION_OPERATE
            )
            # 发送通知
            ticket.notify(
                state_id=state_id,
                receivers=processors,
                message=error_message_template,
                action=NODE_FAILED,
                retry=False,
            )

    def execute(self, data, parent_data):
        if super(BkOpsService, self).execute(data, parent_data):
            return True

        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.do_before_enter_state(state_id, by_flow=self.by_flow)
        processors = ticket.current_processors[1:-1]
        data.set_outputs("params_sops_result_%s" % state_id, False)
        current_node = ticket.node_status.get(state_id=state_id)

        error_message_template = "标准运维任务【{name}】执行失败，失败信息 {detail_message}"

        # 创建全局变量
        sops_result, created = TicketGlobalVariable.objects.get_or_create(
            key="sops_result_" + str(state_id),
            name="sops_result_" + str(state_id),
            state_id=state_id,
            ticket_id=ticket_id,
            value="",
        )

        # first step create_task
        state = ticket.state(state_id)
        sops_info = (
            current_node.query_params
            if current_node.query_params
            else state["extras"]["sops_info"]
        )
        task_params = self.prepare_task_params(state, ticket, sops_info)
        api_info = [
            {
                "key": "api_info",
                "name": "api信息",
                "value": StatusSerializer.build_sops_info(sops_info, task_params),
                "show_result": True,
            }
        ]
        current_node.create_action_log(
            "system",
            "开始执行标准运维任务【{name}】",
            source=SYSTEM_OPERATE,
            action_type=SYSTEM_OPERATE,
            fields=api_info,
        )
        self.update_info(current_node, sops_result, task_params=task_params)

        try:
            create_result = client_backend.sops.create_task(task_params)
        except Exception as error:
            logger.info(
                "create task error，error  info %s , task params %s",
                str(error),
                task_params,
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=str(error),
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        if not create_result.get("result", False):
            detail_message = create_result.get("message") or "unknown"
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=detail_message,
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        sops_task_id = create_result.get("data", {}).get("task_id")
        task_url = create_result.get("data", {}).get("task_url")

        # second_step execute
        try:
            start_result = client_backend.sops.start_task(
                {
                    "__raw": True,
                    "task_id": sops_task_id,
                    "bk_biz_id": task_params["bk_biz_id"],
                }
            )
            self.update_info(current_node, sops_result, task_url=task_url)
        except Exception as error:
            error_message = (
                "start task error，error  info %s , task id %s",
                str(error),
                sops_task_id,
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        if not start_result.get("result", False):
            message = start_result.get("message", "未知错误")
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=message,
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        data.set_outputs("sops_task_id", sops_task_id)
        data.set_outputs("bk_biz_id", task_params["bk_biz_id"])
        data.set_outputs("api_info", api_info)

        return True

    def schedule(self, data, parent_data, callback_data=None):

        sops_task_id = data.outputs.get("sops_task_id", None)
        bk_biz_id = data.outputs.get("bk_biz_id", None)
        api_info = data.outputs.get("api_info", None)
        state_id = data.inputs.state_id
        ticket = Ticket.objects.get(id=parent_data.inputs.ticket_id)
        current_node = ticket.node_status.get(state_id=state_id)
        processors = ticket.current_processors[1:-1]

        sops_result, created = TicketGlobalVariable.objects.get_or_create(
            key="sops_result_" + str(state_id),
            name="sops_result_" + str(state_id),
            state_id=state_id,
            ticket_id=ticket.id,
            value="",
        )

        if not sops_task_id:
            error_message = "invalid callback_data, sops_task_id is null"
            data.outputs.ex_data = error_message
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message,
                ticket=ticket,
                state_id=state_id,
            )
            self.finish_schedule()
            return False

        try:
            task_status_params = {
                "__raw": True,
                "task_id": sops_task_id,
                "bk_biz_id": bk_biz_id,
            }
            task_result = client_backend.sops.get_task_status(task_status_params)
        except Exception as error:
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=str(error),
                processors=processors,
                error_message_template=str(error),
                ticket=ticket,
                state_id=state_id,
            )
            self.finish_schedule()
            return False
        if task_result.get("result", False) is False:
            error_message = task_result.get("message", "")
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message,
                ticket=ticket,
                state_id=state_id,
            )
            self.finish_schedule()
            return False

        task_info = task_result.get("data", {})

        current_status = task_info.get("state")
        if current_status in ["CREATED", "RUNNING", "SUSPENDED"]:
            # 还在执行过程中，继续轮询
            return True
        if current_status in ["FAILED", "REVOKED"]:
            data.set_outputs("params_sops_result_%s" % state_id, False)
            error_message = self.get_detail_message(
                task_status_params, task_info, current_node
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message,
                ticket=ticket,
                state_id=state_id,
            )
            self.finish_schedule()
            return False

        if current_status in ["FINISHED"]:
            data.set_outputs("params_sops_result_%s" % state_id, True)
            self.finish_schedule()
            self.update_info(current_node, sops_result, result=True)
            current_node.set_status(status=current_status)
            current_node.create_action_log(
                "system",
                "标准运维任务【%s】执行成功" % current_node.name,
                source=SYSTEM_OPERATE,
                action_type=SYSTEM_OPERATE,
                fields=api_info,
            )

            for field in ticket.get_output_fields(state_id):
                data.set_outputs("params_%s" % field["key"], field["value"])

            ticket.do_before_exit_state(state_id)

            return True

    @staticmethod
    def get_detail_message(task_params, task_info, task_node):
        failed_children = [
            child
            for child in task_info.get("children", {}).values()
            if child["state"] == "FAILED"
        ]
        error_messages = []
        for child in failed_children:
            task_params.update({"__raw": True, "node_id": child["id"]})
            result = client_backend.sops.get_task_node_detail(task_params)
            error_messages.append(
                u"{}:{}".format(
                    child["name"], result.get("data", {}).get("ex_data") or u"未知错误"
                )
            )
        return "\n".join(error_messages)

    def outputs_format(self):
        return []


class BkOpsComponent(Component):
    name = "标准运维"
    code = "bk_sops"
    bound_service = BkOpsService

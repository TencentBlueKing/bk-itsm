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
import json
import logging

import jmespath
from django.conf import settings

from itsm.component.constants import (
    SYSTEM_OPERATE,
    FINISHED,
    TRANSITION_OPERATE,
    NODE_FAILED,
)
from itsm.component.apigw import client as apigw_client
from itsm.ticket.models import Ticket, TicketGlobalVariable
from itsm.ticket.serializers import StatusSerializer
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import StaticIntervalGenerator

from .itsm_base_service import ItsmBaseService

logger = logging.getLogger("celery")


class BkDevOpsService(ItsmBaseService):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(3)

    def prepare_build_params(self, devops_info, ticket):
        """
        构建流水线参数
        @param devops_info: 蓝盾节点参数 Type: dict
        {
            "username": "user",
            "project_id": {
                "value": "test",
                "name": "测试",
                "key": "project_id"
            },
            "pipeline_id": {
                "value": "p-216fafa1b9f44f2b95ed6bxxxxxxxxxx",
                "name": "代码检查",
                "key": "pipeline_id"
            },
            "constants": [{
                "value": "test",
                "name": "bkapp_code",
                "key": "bkapp_code"
                "type: "variable" or "const" 分别代表变量与常量
            }]
        }
        @return params: 流水线参数 Type: dict
        {
            "username": "user",
            "project_id": "test",
            "pipeline_id": "p-216fafa1b9f44f2b95ed6bxxxxxxxxxx",
            # 下面是流水线所需参数
            "bkapp_code": "test",
            "key2": "value2",
            "key3": "value3",
        }
        """
        # 1.从表单数据中拿出key-value

        fields = ticket.fields.values_list("key", "_value")
        variables = TicketGlobalVariable.objects.filter(
            ticket_id=ticket.id
        ).values_list("key", "value")
        values = dict(list(fields) + list(variables))

        constants = {}
        # 支持引用变量
        if devops_info["constants"]:
            for constant in devops_info["constants"]:
                key = constant["key"]
                if constant.get("type", "const") == "variable":
                    constants[key] = values.get(constant["value"], "")
                else:
                    constants[key] = constant["value"]

        # 2.构建蓝盾流水线api所需参数
        params = {
            "username": devops_info["username"],
            "project_id": devops_info["project_id"]["value"],
            "pipeline_id": devops_info["pipeline_id"]["value"],
        }
        params.update(constants)
        return params

    def update_info(self, current_node, devops_result, **kwargs):
        """
        更新任务上下文
        @param current_node: 当前节点状态 Type: object
        @param devops_result: 节点全局变量 Type: object
        @param kwargs: 流水线构建参数 Type: dict
        """

        devops_result.value = kwargs.get("result", "")
        devops_result.save()

        current_node.contexts.update(**kwargs)
        current_node.save()

    def do_exit_plugins(self, result, **kwargs):
        if not result:
            current_node = kwargs.get("current_node")
            devops_result = kwargs.get("devops_result")
            error_message = kwargs.get("error")
            processors = kwargs.get("processors")
            error_message_template = kwargs.get("error_message_template")
            ticket = kwargs.get("ticket")
            state_id = kwargs.get("state_id")
            self.update_info(
                current_node, devops_result, error_message=error_message, result=result
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

    def update_variables(self, resp, ticket_id, state_id, variables):
        resp = resp["variables"]
        for variable in variables:
            value = jmespath.search(variable["ref_path"], resp)
            if isinstance(value, bool):
                value = json.dumps(value)
            if TicketGlobalVariable.objects.filter(
                ticket_id=ticket_id, key=variable["key"]
            ).exists():
                TicketGlobalVariable.objects.filter(
                    ticket_id=ticket_id, key=variable["key"]
                ).update(value=value)
            else:
                TicketGlobalVariable.objects.create(
                    name=variable.get("name", ""),
                    ticket_id=ticket_id,
                    key=variable["key"],
                    value=value,
                    state_id=state_id,
                )
            variable["value"] = value
        return variables

    def execute(self, data, parent_data):
        """
        执行流水线构建
        @param data: Type: object
        @param parent_data: Type: object
        @return: True为流程中，False为流程暂停
        """
        if super(BkDevOpsService, self).execute(data, parent_data):
            return True

        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.do_before_enter_state(state_id, by_flow=self.by_flow)
        processors = ticket.current_processors[1:-1]

        data.set_outputs("params_devops_result_{}".format(state_id), False)
        current_node = ticket.node_status.get(state_id=state_id)

        error_message_template = "蓝盾流水线【{name}】启动失败，失败信息 {detail_message}"

        # 1.创建全局变量
        devops_result, created = TicketGlobalVariable.objects.get_or_create(
            key="devops_result_{}".format(state_id),
            name="devops_result_{}".format(state_id),
            state_id=state_id,
            ticket_id=ticket_id,
            value="",
        )

        # 2.获取蓝盾节点参数
        state = ticket.state(state_id)
        try:
            devops_info = (
                current_node.query_params
                if current_node.query_params
                else state["extras"].get("devops_info")
            )

        except KeyError as error:
            logger.info(
                "get devops_info error from State instance，error info: {}, state id: {}".format(
                    error, state_id
                )
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                devops_result=devops_result,
                error=error,
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        # 3.构建流水线启动参数
        build_params = self.prepare_build_params(devops_info, ticket)

        # 4.构建 api_info
        api_info = [
            {
                "key": "api_info",
                "name": "api信息",
                "value": StatusSerializer.build_devops_info(devops_info, build_params),
                "show_result": True,
            }
        ]
        current_node.create_action_log(
            "system",
            "开始启动蓝盾流水线【{name}】",
            source=SYSTEM_OPERATE,
            action_type=SYSTEM_OPERATE,
            fields=api_info,
        )
        self.update_info(current_node, devops_result, build_params=build_params)

        # 5.获取项目id和流水线id
        try:
            devops_username = build_params.get("username")
            devops_project_id = build_params.get("project_id")
            devops_pipeline_id = build_params.get("pipeline_id")
        except Exception as error:
            logger.info(
                "check params error，error info: {}, build params: {}".format(
                    error, build_params
                )
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                devops_result=devops_result,
                error=str(error),
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        # 6.执行流水线构建
        try:
            build_result = apigw_client.devops.pipeline_build_start(build_params)
            devops_build_id = build_result.get("id")
            build_url = "{}/{}/{}/detail/{}".format(
                str(settings.DEVOPS_CLIENT_URL).rstrip(),
                devops_project_id,
                devops_pipeline_id,
                devops_build_id,
            )
            self.update_info(current_node, devops_result, build_url=build_url)

        except Exception as error:
            logger.info(
                "build pipeline error，error info: {}, build params: {}".format(
                    error, build_params
                )
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                devops_result=devops_result,
                error=str(error),
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        # 7.设置outputs
        data.set_outputs("devops_username", devops_username)
        data.set_outputs("devops_project_id", devops_project_id)
        data.set_outputs("devops_pipeline_id", devops_pipeline_id)
        data.set_outputs("devops_build_id", devops_build_id)
        data.set_outputs("api_info", api_info)

        return True

    def schedule(self, data, parent_data, callback_data=None):
        """
        轮询流水线执行状态
        @param data: Type: object
        @param parent_data: Type: object
        @param callback_data: Type: object
        @return: True为流程中，False为流程暂停
        """

        # 1.拿到outputs中的username，项目id，流水线id，构建id
        devops_username = data.outputs.get("devops_username", None)
        devops_project_id = data.outputs.get("devops_project_id", None)
        devops_pipeline_id = data.outputs.get("devops_pipeline_id", None)
        devops_build_id = data.outputs.get("devops_build_id", None)
        api_info = data.outputs.get("api_info", None)
        state_id = data.inputs.state_id
        ticket = Ticket.objects.get(id=parent_data.inputs.ticket_id)
        current_node = ticket.node_status.get(state_id=state_id)
        processors = ticket.current_processors[1:-1]

        # 2.创建全局变量
        devops_result, created = TicketGlobalVariable.objects.get_or_create(
            key="devops_result_{}".format(state_id),
            name="devops_result_{}".format(state_id),
            state_id=state_id,
            ticket_id=ticket.id,
            value="",
        )

        # 3.构建查询状态所需参数
        if not devops_build_id:
            error_message = "invalid callback_data, devops_build_id is null"
            data.outputs.ex_data = error_message
            logger.info(
                "get devops_build_id error，error info: {}, data outputs: {}".format(
                    error_message, data.outputs
                )
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                devops_result=devops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message,
                ticket=ticket,
                state_id=state_id,
            )
            self.finish_schedule()
            return False

        build_status_params = {
            "username": devops_username,
            "project_id": devops_project_id,
            "pipeline_id": devops_pipeline_id,
            "build_id": devops_build_id,
        }

        # 4.执行查询流水线执行状态
        try:
            status_info = apigw_client.devops.pipeline_build_status(build_status_params)
            current_status = status_info.get("status")
        except Exception as error:
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                devops_result=devops_result,
                error=str(error),
                processors=processors,
                error_message_template=str(error),
                ticket=ticket,
                state_id=state_id,
            )
            self.finish_schedule()
            return False

        # 5.判断流水线执行状态
        if current_status in ["QUEUE", "QUEUE_CACHE", "RUNNING"]:
            # 在中间状态，继续轮询
            return True

        if current_status == "CANCELED":
            # 流水线取消，结束轮询，获取异常信息
            data.set_outputs("params_devops_result_{}".format(state_id), False)
            error_message = "蓝盾流水线【{}】构建已取消".format(current_node.name)
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                devops_result=devops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message,
                ticket=ticket,
                state_id=state_id,
            )
            # 结束轮询
            self.finish_schedule()
            return False

        if current_status == "QUEUE_TIMEOUT":
            # 队列超时，结束轮询，获取异常信息
            data.set_outputs("params_devops_result_{}".format(state_id), False)
            error_message = "蓝盾流水线【{}】构建排队超时".format(current_node.name)
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                devops_result=devops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message,
                ticket=ticket,
                state_id=state_id,
            )
            # 结束轮询
            self.finish_schedule()
            return False

        if current_status in ["FAILED", "TERMINATE"]:
            # 在异常状态，结束轮询，获取异常信息
            data.set_outputs("params_devops_result_{}".format(state_id), False)
            error_message_info = "蓝盾流水线【{}】执行失败".format(current_node.name)
            error_message_list = status_info.get("errorInfoList", [])
            if error_message_list:
                error_message_detail = ",".join(
                    [item.get("errorMsg", "unknow") for item in error_message_list]
                )
            else:
                error_message_detail = "status: {}".format(current_status)
            error_message = "{}, error message: {}".format(
                error_message_info, error_message_detail
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                devops_result=devops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message,
                ticket=ticket,
                state_id=state_id,
            )
            # 结束轮询
            self.finish_schedule()
            return False

        if current_status in ["SUCCEED", "STAGE_SUCCESS"]:
            # 在成功状态，结束轮询
            data.set_outputs("params_devops_result_{}".format(state_id), True)

            # 处理全局变量
            state = ticket.flow.get_state(state_id)
            variables = state["variables"].get("outputs", [])
            # 更新全局变量
            variable_output = self.update_variables(
                status_info, ticket.id, state_id, variables
            )
            self.update_info(
                current_node, devops_result, result=True, variables=variable_output
            )
            current_node.set_status(status=FINISHED)
            self.finish_schedule()
            current_node.create_action_log(
                "system",
                "蓝盾流水线【{}】执行成功".format(current_node.name),
                source=SYSTEM_OPERATE,
                action_type=SYSTEM_OPERATE,
                fields=api_info,
            )

            for field in ticket.get_output_fields(state_id):
                data.set_outputs("params_{}".format(field["key"]), field["value"])

            ticket.do_before_exit_state(state_id)
            return True


class BkDevOpsComponent(Component):
    name = "蓝盾"
    code = "bk_devops"
    bound_service = BkDevOpsService

# -*- coding: utf-8 -*-
import copy
import json
import logging

import jmespath

from itsm.pipeline_plugins.components.collections.webhook import ParamsBuilder
from itsm.plugin_service.plugin_client import PluginServiceApiClient
from pipeline.component_framework.component import Component
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    TRANSITION_OPERATE,
    NODE_FAILED,
    SYSTEM_OPERATE,
    FINISHED,
)
from itsm.pipeline_plugins.components.collections.itsm_base_service import (
    ItsmBaseService,
)
from itsm.ticket.models import Ticket, TicketGlobalVariable
from pipeline.core.flow.activity import StaticIntervalGenerator

logger = logging.getLogger("celery")


class BkPluginService(ItsmBaseService):
    """
    {
            "method": "method",
            "url": "",
            "query_params": [{key:"", value:""}],
            "auth": "",
            "headers": {},
            "body": {
                "type": "row, json",
                "raw_type": "json, "
                "value": ""
            },
            "timeout": "",
            "success_exp": "",
        }

    variables: {
        "outputs":[
                name: "阿哈哈哈"
                ref_path: "resp.result"
                type: "STRING"
            ]
        }
    """

    __need_schedule__ = True
    interval = StaticIntervalGenerator(3)

    POLL = 2
    CALLBACK = 3
    SUCCESS = 4
    FAILED = 5

    def update_info(self, current_node, **kwargs):
        """
        更新任务上下文
        @param current_node: 当前节点状态 Type: object
        @param devops_result: 节点全局变量 Type: object
        @param kwargs: 流水线构建参数 Type: dict
        """

        current_node.contexts.update(**kwargs)
        current_node.save()

    def build_params(self, extras, ticket):
        """
        整体渲染 extras 所有的变量
        """
        variables = ticket.get_output_fields(return_format="dict", need_display=True)
        extras_copy = copy.deepcopy(extras)
        data = ParamsBuilder(extras=extras_copy, variables=variables).jinja_render(
            extras_copy
        )
        return data

    def update_variables(self, resp, ticket_id, state_id, variables):
        resp = {"resp": resp}
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

    def do_exit_plugins(
        self,
        ticket,
        state_id,
        current_node,
        error_message,
        error_message_template,
        processors,
    ):
        processors = processors
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
        """

        bk_plugin_info: {
            "plugin_code": "code",
            "version": "",
            "inputs":{}
        }


        """
        if super(BkPluginService, self).execute(data, parent_data):
            return True
        logger.info(
            "AutoStateService execute: data={}, parent_data={}".format(
                data.inputs, parent_data.inputs
            )
        )

        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.do_before_enter_state(state_id, by_flow=self.by_flow)

        state = ticket.flow.get_state(state_id)
        variables = state["variables"].get("outputs", [])
        error_message_template = "蓝鲸插件调用失败【{name}】执行失败，失败信息 {detail_message}"

        processors = ticket.current_processors[1:-1]
        current_node = ticket.node_status.get(state_id=state_id)

        try:
            bk_plugin_info = (
                current_node.query_params
                if current_node.query_params
                else state["extras"].get("bk_plugin_info")
            )
        except Exception as e:
            err_message = "bk_plugin_info info节点解析失败, error={}".format(e)
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        try:
            extras = self.build_params(bk_plugin_info, ticket)
            self.update_info(current_node, build_params=copy.deepcopy(extras))
        except Exception as e:
            err_message = "bk_plugin_info 解析失败, error={}".format(e)
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        plugin_code = extras.pop("plugin_code")
        version = extras.pop("version")

        client = PluginServiceApiClient(plugin_code=plugin_code)

        try:
            extras["context"]["executor"] = ticket.creator
            result, resp = client.invoke(version=version, data=extras)
        except Exception as e:
            err_message = "bk_plugin_info 请求失败, error={}".format(e)
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        if not result:
            err_message = "bk_plugin_info 请求失败，返回值非 true， message = {}".format(
                resp.get("message")
            )
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        state = resp.get("state")
        data.set_outputs("is_schedule", False)
        if state in [self.POLL, self.CALLBACK]:
            # 定时任务额外处理
            data.set_outputs("is_schedule", True)
            data.set_outputs("trace_id", resp.get("trace_id"))
            data.set_outputs("plugin_code", plugin_code)
            data.set_outputs("version", version)
            # 退出
        elif state == self.SUCCESS:
            current_node.create_action_log(
                "system",
                "蓝鲸插件任务【%s】执行成功" % current_node.name,
                source=SYSTEM_OPERATE,
                action_type=SYSTEM_OPERATE,
                fields=[],
            )
            # 成功，全局变量渲染，根据路径，渲染outputs
            variable_output = self.update_variables(
                resp, ticket_id, state_id, variables
            )
            # 设置状态
            self.update_info(current_node, variables=variable_output)
            current_node.set_status(status=FINISHED)

        elif state == self.FAILED:
            # 失败, 退出
            err_message = "bk_plugin_info 执行失败，state == 5， message = {}".format(
                resp.get("err")
            )
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        for field in ticket.get_output_fields(state_id):
            data.set_outputs("params_%s" % field["key"], field["value"])

        return True

    def schedule(self, data, parent_data, callback_data=None):

        error_message_template = "蓝鲸插件调用失败【{name}】执行失败，失败信息 {detail_message}"

        ticket = Ticket.objects.get(id=parent_data.inputs.ticket_id)
        state_id = data.inputs.state_id
        current_node = ticket.node_status.get(state_id=state_id)

        if not data.outputs.get("is_schedule"):
            current_node.set_status(status=FINISHED)
            ticket.do_before_exit_state(state_id)
            self.finish_schedule()
            return True

        ticket_id = parent_data.inputs.ticket_id
        processors = ticket.current_processors[1:-1]
        state = ticket.flow.get_state(state_id)
        variables = state["variables"].get("outputs", [])

        plugin_code = data.outputs.get("plugin_code")
        trace_id = data.outputs.get("trace_id")

        try:
            client = PluginServiceApiClient(plugin_code=plugin_code)
            result, resp = client.get_schedule(trace_id=trace_id)
        except Exception:
            err_message = "轮询服务调用异常"
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            self.finish_schedule()
            return False

        if not result:
            err_message = "轮询服务调用异常 ， result = False， message = {}".format(
                resp.get("message")
            )
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            self.finish_schedule()
            return False

        state = resp.get("state")

        if state in [self.POLL, self.CALLBACK]:
            return True
        elif state == self.FAILED:
            err_message = "蓝鲸插件节点 执行失败，state == 5， message = {}".format(
                resp.get("message")
            )
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            self.finish_schedule()
            return False
        elif state == self.SUCCESS:
            # 创建任务
            current_node.create_action_log(
                "system",
                "蓝鲸插件任务【%s】执行成功" % current_node.name,
                source=SYSTEM_OPERATE,
                action_type=SYSTEM_OPERATE,
                fields=[],
            )
            self.update_variables(resp, ticket_id, state_id, variables)
            self.finish_schedule()

            for field in ticket.get_output_fields(state_id):
                data.set_outputs("params_%s" % field["key"], field["value"])

            ticket.do_before_exit_state(state_id)

            return True

        return True

    def outputs_format(self):
        return []


class BkPluginComponent(Component):
    name = _("蓝鲸插件 集成节点")
    code = "itsm_bk_plugin"
    bound_service = BkPluginService

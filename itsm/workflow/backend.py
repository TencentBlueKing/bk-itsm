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


# pipeline适配类
#     建立Workflow和Pipeline的关系

import contextlib
import copy
import logging
import os
import time

import six
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    COVERAGE_STATE,
    END_STATE,
    NORMAL_STATE,
    REJECT_OPERATE,
    ROUTER_P_STATE,
    ROUTER_STATE,
    SIGN_STATE,
    START_STATE,
    SUPPORTED_TYPE,
    TASK_SOPS_STATE,
    TASK_STATE,
    VIRTUAL_STATE,
    TICKET_GLOBAL_VARIABLES,
    APPROVAL_STATE,
    TASK_DEVOPS_STATE,
    WEBHOOK_STATE,
    BK_PLUGIN_STATE,
)
from itsm.component.exceptions import WorkFlowInvalidError
from itsm.component.utils.basic import merge_dict_list
from itsm.component.utils.bk_bunch import Bunch, bunchify, unbunchify
from itsm.component.utils.conversion import format_exp_value, get_exp_template
from itsm.workflow.models import WorkflowVersion
from pipeline.builder import Data
from pipeline.builder.flow import ServiceActivity, Var
from pipeline.core.constants import PE
from pipeline.parser import PipelineParser
from pipeline.parser.utils import replace_all_id
from pipeline.service import task_service
from pipeline.utils.uniqid import line_uniqid, node_uniqid

logger = logging.getLogger("app")


class PipelineWrapper(object):
    """适配器内持有一个workflow和pipeline
    主要封装pipeline操作方法
    """

    def __init__(self, flow, ticket_id=None, for_migrate=False):
        if isinstance(flow, WorkflowVersion):
            self.flow = flow
        elif isinstance(flow, Bunch):
            self.flow = flow
        else:
            self.flow = WorkflowVersion.objects.get(pk=flow)

        self.pipeline = None
        self.data = {"inputs": {}, "outputs": {}}
        self.ticket_id = ticket_id
        self.for_migrate = for_migrate
        (
            self.states,
            self.transitions,
            self.states_map,
            self.transitions_map,
        ) = self.get_workflow_data()

    @contextlib.contextmanager
    def build_tree_exception_handler(self, state):
        try:
            yield
        except Exception as error:
            # 记录代码底层报错
            logger.exception(error)
            raise WorkFlowInvalidError([state["id"]], _("当前节点画布连线不合理, 请重新确认"))

    def _unpack_state(self, states, state_id):
        """状态提取"""

        state = states[state_id]
        incomings = state["incoming"]
        outgoings = state["outgoing"]

        return state, incomings, outgoings

    def build_component_for_itsm(self, state):
        """构造itsm组件"""
        if state["type"] == TASK_STATE:
            act = ServiceActivity("itsm_auto")
            act.component.inputs.need_poll = Var(
                type=Var.PLAIN, value=str(state.get("need_poll", False))
            )
            act.component.inputs.poll_time = Var(
                type=Var.PLAIN, value=str(state.get("poll_time", 3))
            )
            act.component.inputs.poll_interval = Var(
                type=Var.PLAIN, value=str(state.get("poll_interval", 1))
            )
        elif state["type"] == TASK_SOPS_STATE:
            act = ServiceActivity("bk_sops")
        # 开始节点state['type'] == NORMAL_STATE and state['is_builtin']
        elif state["type"] == NORMAL_STATE and state["is_builtin"]:
            act = ServiceActivity("itsm_create")
        elif state["type"] == VIRTUAL_STATE:
            act = ServiceActivity("itsm_migrate")
        elif state["type"] == SIGN_STATE:
            act = ServiceActivity("itsm_sign")
        elif state["type"] == TASK_DEVOPS_STATE:
            act = ServiceActivity("bk_devops")
        elif state["type"] == WEBHOOK_STATE:
            act = ServiceActivity("itsm_webhook")
        elif state["type"] == BK_PLUGIN_STATE:
            act = ServiceActivity("itsm_bk_plugin")
        elif state["type"] == APPROVAL_STATE:
            act = ServiceActivity("itsm_approval_node")
        else:
            act = ServiceActivity("itsm_approve")

        act.component.inputs.state_id = Var(type=Var.PLAIN, value=str(state["id"]))

        # 节点输出变量输出到pipeline->data
        state_variables = bunchify(state["variables"])
        self.data["inputs"].update(
            {
                "${params_%s}"
                % var.key: {
                    "type": "splice",
                    "source_act": "%s" % state["unique_id"],
                    "source_key": "params_%s" % var.key,
                    "value": "",
                }
                for var in state_variables.outputs
            }
        )

        return act.component_dict()

    def append_exclusive_gateway(self, states, state_id):
        """创建分支网关节点
        # 入度：>= 1，出度：>=1
        # A--x--|--->B-->D
        #       |-->C-->E
        """

        state, incomings, outgoings = self._unpack_state(states, state_id)
        flow_to = {}

        # 构造分支网关节点的出口线（拷贝A的出口线作为网关的出口线）
        gateway_id = node_uniqid()
        gateway_outgoings = {
            t["unique_id"]: {
                "is_default": False,
                "source": gateway_id,
                "id": t["unique_id"],
                "target": states[str(t["to_state"])]["unique_id"],
            }
            for t in outgoings
        }
        flow_to.update(gateway_outgoings)

        # 创建一条从当前节点连接到网关节点的连线（当前节点出口线）
        gateway_incoming_id = line_uniqid()

        # 增加一个分支网关
        gateway = {
            gateway_id: {
                "outgoing": list(gateway_outgoings.keys()),
                "incoming": [gateway_incoming_id],
                "name": "",
                "type": PE.ExclusiveGateway,
                # ConvergeMatchError: 非法网关，请检查其分支是否符合规则
                # 'type': PE.ConditionalParallelGateway,
                "conditions": self.build_conditions_for_gateway(outgoings),
                "id": gateway_id,
            }
        }

        return gateway, flow_to, gateway_id, gateway_incoming_id

    def build_activity(
        self, states, state_id, exclusive_gateway_id=None, gateway_incoming_id=None
    ):
        """创建普通节点
        入度：>=1 ，出度：1
        """

        state, incomings, outgoings = self._unpack_state(states, state_id)

        # 从当前节点连接到下一节点的唯一出口线
        outgoing = outgoings[0]
        outgoing_id = outgoing["unique_id"]
        target_id = states[str(outgoing["to_state"])]["unique_id"]
        if gateway_incoming_id and exclusive_gateway_id:
            outgoing_id = gateway_incoming_id
            target_id = exclusive_gateway_id

        # 从当前节点连接到下一节点或后面插入的分支网关节点（exclusive_gateway_id）
        flow_to = {
            outgoing_id: {
                "is_default": False,
                "source": state["unique_id"],
                "id": outgoing_id,
                "target": target_id,
            }
        }

        activity = {
            state["unique_id"]: {
                "id": state["unique_id"],
                "type": PE.ServiceActivity,
                "name": state["name"],
                "optional": False,
                "error_ignorable": False,
                "outgoing": outgoing_id,
                "incoming": [t["unique_id"] for t in incomings],
                "component": self.build_component_for_itsm(state),
                "loop": {},
            }
        }

        return activity, flow_to

    def build_converge_gateway(
        self, states, state_id, exclusive_gateway_id=None, gateway_incoming_id=None
    ):
        """创建汇聚网关节点
        入度：>=1，出度：1
        # B-->D-
        # C-->E-|->A->F

        ITSM: 入度：>=1，出度：>=1（添加分支网关）
        """

        state, incomings, outgoings = self._unpack_state(states, state_id)
        outgoing = outgoings[0]
        outgoing_id = outgoing["unique_id"]
        target_id = states[str(outgoing["to_state"])]["unique_id"]
        if gateway_incoming_id and exclusive_gateway_id:
            outgoing_id = gateway_incoming_id
            target_id = exclusive_gateway_id

        # 当前汇聚网关节点->下一节点或后面插入的分支网关节点（exclusive_gateway_id）
        flow_to = {
            outgoing_id: {
                "is_default": False,
                "source": state["unique_id"],
                "id": outgoing_id,
                "target": target_id,
            }
        }

        gateway = {
            state["unique_id"]: {
                "incoming": [t["unique_id"] for t in incomings],
                "outgoing": outgoing_id,
                "name": "",
                "type": PE.ConvergeGateway,
                "id": state["unique_id"],
            }
        }

        # 设置汇聚网关
        return gateway, flow_to

    def build_parallel_gateway(self, states, state_id):
        """创建并行网关节点
        入度：>=1，出度：>=1
        # X-in--->A-->out--->B
        # Y-in->|   |->out->C
        """

        state, incomings, outgoings = self._unpack_state(states, state_id)

        # 构造分支网关节点的出口线
        gateway_outgoings = {
            t["unique_id"]: {
                "is_default": False,
                "source": state["unique_id"],
                "id": t["unique_id"],
                "target": states[str(t["to_state"])]["unique_id"],
            }
            for t in outgoings
        }

        gateway = {
            state["unique_id"]: {
                "outgoing": list(gateway_outgoings.keys()),
                "incoming": [t["unique_id"] for t in incomings],
                "name": state["name"],
                "type": PE.ConditionalParallelGateway,
                "conditions": self.build_conditions_for_gateway(outgoings),
                "id": state["unique_id"],
            }
        }

        # 设置并行网关
        return gateway, gateway_outgoings

    def build_end_event(self, states, state_id):
        """创建结束节点
        入度：>=1，出度：0
        """

        state, incomings, _ = self._unpack_state(states, state_id)

        end_event = {
            "incoming": [t["unique_id"] for t in incomings],
            "outgoing": "",
            "type": PE.EmptyEndEvent,
            "id": state["unique_id"],
            "name": "结束",
        }

        return end_event, None

    def build_start_event(self, states, state_id):
        """创建开始节点
        入度：0，出度：1
        """

        state, _, outgoings = self._unpack_state(states, state_id)
        outgoing = outgoings[0]

        start_event = {
            "incoming": "",
            "outgoing": outgoing["unique_id"],
            "type": PE.EmptyStartEvent,
            "id": state["unique_id"],
            "name": "开始",
        }

        flow_to = {
            outgoing["unique_id"]: {
                "is_default": False,
                "source": state["unique_id"],
                "id": outgoing["unique_id"],
                "target": states[str(outgoing["to_state"])]["unique_id"],
            }
        }

        return start_event, flow_to

    def build_conditions_for_gateway(self, outgoings):
        """构造网关条件表达式"""

        conditions = {}
        for o in outgoings:
            condition = bunchify(o["condition"])

            expressions = []
            for expression in condition.expressions:

                inner_expressions = []
                for exp in expression.expressions:

                    if exp.key == "G_INT_1":
                        evaluation = "1==1"
                    else:
                        if exp.type not in SUPPORTED_TYPE:
                            raise NotImplementedError(_("不支持的数据类型 %s") % exp.type)
                        template = get_exp_template(exp.type)
                        value = format_exp_value(exp.type, exp.value)
                        evaluation = template.format(
                            key="${params_%s}" % exp.key,
                            condition=exp.condition,
                            value=value,
                        )

                    inner_expressions.append(evaluation)
                expression_type = " {} ".format(expression.type)
                expressions.append(expression_type.join(inner_expressions))

            conditions.update(
                {
                    o["unique_id"]: {
                        "evaluate": condition.type.join(
                            [" ({}) ".format(e) for e in expressions]
                        )
                    }
                }
            )

        return conditions

    def get_workflow_data(self):
        """
        获取流程版本内的节点和连线，并稍加调整
        """

        from itsm.ticket.models import TicketEventLog

        states = copy.deepcopy(
            self.flow.states
            if isinstance(self.flow, WorkflowVersion)
            else unbunchify(self.flow.states)
        )
        transitions = copy.deepcopy(
            self.flow.transitions
            if isinstance(self.flow, WorkflowVersion)
            else unbunchify(self.flow.transitions)
        )
        states_map = {}
        transitions_map = {}

        # 调整state的数据结构，补充：incoming、outgoing、fields信息
        for state_id, state in six.iteritems(states):
            state_uniq_id = node_uniqid()

            # fill state's unique_id/incoming/outgoing
            state.update(
                {
                    "unique_id": state_uniq_id,
                    "incoming": [],
                    "outgoing": [],
                    "fields": [],
                }
            )

            # force change finished state's type for migrate
            if (
                self.for_migrate
                and self.ticket_id
                and TicketEventLog.objects.filter(
                    ticket_id=self.ticket_id,
                    from_state_id=state_id,
                )
                .exclude(type=REJECT_OPERATE)
                .exists()
            ):
                # 忽略被打回的节点的执行日志
                state.update(type=VIRTUAL_STATE)

            # state_id -> unique_id
            states_map[state_id] = state_uniq_id

        # fill state's incoming and outgoing
        for transition_id, transition in six.iteritems(transitions):
            transition.update({"unique_id": line_uniqid()})
            states[str(transition["to_state"])]["incoming"].append(transition)
            states[str(transition["from_state"])]["outgoing"].append(transition)
            transitions_map[transition["unique_id"]] = transition_id

        return states, transitions, states_map, transitions_map

    def get_table_fields(self):
        table_fields = []
        for field in list(self.flow.fields.values()):
            if field.get("source") != "TABLE":
                continue
            table_fields.append(field)
        return table_fields

    def build_tree(self, ticket_id, user_data=None, use_cache=False, **kwargs):
        """组装pipeline数据结构
        START       -> StartEvent
        END         -> EndEvent
        ROUTER-P    -> ParallelGateway
        ROUTER      -> ExclusiveGateway  (NORMAL + outgoings > 1)
        COVERAGE    -> ConvergeGateway
        备注：构造连线信息时，只需要不断更新节点的出口线到flows中即可
        若同时更新入口线和出口线，会导致网关插入后，新线被旧线覆盖的情况
        A--->x--->B
             |--[1]->C （插入x网关后，将A的连接关系直接转移到x上）
          |-[1]->C（更新C的入口线时，相同id[1]对应的线条会被覆盖）

        参数：
            use_cache: 设置是否使用缓存的pipeline_tree
        """

        # 取缓存并替换ID
        if (
            isinstance(self.flow, WorkflowVersion)
            and self.flow.pipeline_data
            and use_cache
        ):
            pipeline_data = self.get_cached_pipeline_data(ticket_id, user_data)
            if pipeline_data:
                return pipeline_data

        # 从Workflow中提取：event/activities/gateways/flows/data
        (
            start_event,
            end_event,
            activities,
            gateways,
            flows,
            exclusive_gateway_source_state,
        ) = ({}, {}, {}, {}, {}, {})

        # 构造pipeline_data
        data_input = {"${ticket_id}": {"type": PE.plain, "value": ticket_id}}
        data_input.update(
            {
                "${%s}" % key: {"type": PE.plain, "value": value}
                for key, value in kwargs.items()
            }
        )

        # source_act = ",".join([state['unique_id'] for state in list(self.states.values())])
        state_unique_ids = [s["unique_id"] for s in self.states.values()]
        for field in self.get_table_fields() + TICKET_GLOBAL_VARIABLES:
            param_key = "params_%s" % field["key"]
            source_key = "${%s}" % param_key
            source_act = [
                {"source_act": suid, "source_key": param_key}
                for suid in state_unique_ids
            ]

            data_input.update(
                {source_key: {"type": "splice", "source_act": source_act, "value": ""}}
            )

        self.data = {"inputs": data_input, "outputs": []}

        # 用户数据覆盖到pipeline_data
        if isinstance(user_data, Data):
            self.data.update(user_data.to_dict())

        # 流程模型转换
        for state_id, state in self.states.items():

            with self.build_tree_exception_handler(state):
                if state["type"] == START_STATE:
                    # START：开始事件
                    start_event, flow_to = self.build_start_event(self.states, state_id)
                    flows.update(flow_to)
                elif state["type"] == END_STATE:
                    # END: 结束事件
                    end_event, _ = self.build_end_event(self.states, state_id)
                elif state["type"] == ROUTER_P_STATE:
                    # ROUTER-P: 并行网关
                    gateway, flow_to = self.build_parallel_gateway(
                        self.states, state_id
                    )
                    # 更新连线
                    flows.update(flow_to)
                    # 更新并行网关
                    gateways.update(gateway)
                elif state["type"] == COVERAGE_STATE:
                    # COVERAGE: 汇聚网关
                    outgoings = state["outgoing"]
                    exclusive_gateway_id, gateway_incoming_id = None, None

                    # outgoings>1时，添加分支网关
                    if len(outgoings) > 1:
                        (
                            gateway,
                            flow_to,
                            exclusive_gateway_id,
                            gateway_incoming_id,
                        ) = self.append_exclusive_gateway(self.states, state_id)
                        # 更新普通节点及分支网关的出口线
                        flows.update(flow_to)
                        # 更新分支网关及汇聚网关
                        gateways.update(gateway)
                        # 更新分支网关的来源节点
                        exclusive_gateway_source_state.update(
                            **{state_id: list(gateway.keys())[0]}
                        )

                    # 连接汇聚网关和下一节点或插入的网关节点
                    coverage_gateway, flow_to = self.build_converge_gateway(
                        self.states, state_id, exclusive_gateway_id, gateway_incoming_id
                    )

                    # 更新连线和汇聚网关
                    flows.update(flow_to)
                    gateways.update(coverage_gateway)

                # add virtual state of: VIRTUAL_STATE for old flow ticket migrate
                elif state["type"] in [
                    NORMAL_STATE,
                    ROUTER_STATE,
                    TASK_STATE,
                    TASK_SOPS_STATE,
                    SIGN_STATE,
                    VIRTUAL_STATE,
                    APPROVAL_STATE,
                    TASK_DEVOPS_STATE,
                    WEBHOOK_STATE,
                    BK_PLUGIN_STATE,
                ]:
                    # NORMAL（普通节点和分支网关节点）
                    outgoings = state["outgoing"]
                    exclusive_gateway_id, gateway_incoming_id = None, None
                    # outgoings>1时，添加分支网关
                    if len(outgoings) > 1:
                        (
                            gateway,
                            flow_to,
                            exclusive_gateway_id,
                            gateway_incoming_id,
                        ) = self.append_exclusive_gateway(self.states, state_id)
                        # 更新普通节点及分支网关的出口线
                        flows.update(flow_to)
                        # 更新分支网关及普通节点
                        gateways.update(gateway)
                        # 更新分支网关的来源节点
                        exclusive_gateway_source_state.update(
                            **{state_id: list(gateway.keys())[0]}
                        )

                    # 连接普通节点和下一节点或插入的网关节点
                    activity, flow_to = self.build_activity(
                        self.states, state_id, exclusive_gateway_id, gateway_incoming_id
                    )
                    # 更新连线和普通节点
                    flows.update(flow_to)
                    activities.update(activity)

        return {
            "pipeline_tree": {
                PE.activities: activities,
                PE.gateways: gateways,
                PE.flows: flows,
                PE.data: self.data,
                PE.start_event: start_event,
                PE.end_event: end_event,
                PE.id: ticket_id,
            },
            "states_map": self.states_map,
            "transitions_map": self.transitions_map,
            "exclusive_gateway_source_state": exclusive_gateway_source_state,
        }

    def update_cached_pipeline_data(self, pipeline_data):
        """更新pipeline_data"""

        # 保存pipeline_tree到pipeline中
        # 为何要更新？？？
        self.flow.pipeline_data.update(pipeline_data)

        # 这里会同时保存从states的变化
        self.flow.save()

    def get_cached_pipeline_data(self, ticket_id, user_data=None):
        """从缓存中获取pipeline_data"""
        if not self.flow.pipeline_data.get("pipeline_tree"):
            # 不存在pipeline_data的时候，直接返回
            return None

        pipeline_tree = self.flow.pipeline_data["pipeline_tree"]
        _states_map = self.flow.pipeline_data["states_map"]

        # 替换旧的unique_id并得到新的映射关系
        new_replace_map = merge_dict_list(list(replace_all_id(pipeline_tree).values()))

        # 更新state_id映射到替换后的unique_id
        states_map = {
            state_id: new_replace_map[old_unique_id]
            for state_id, old_unique_id in six.iteritems(_states_map)
        }

        # 更新pipeline_data
        pipeline_tree["data"]["inputs"].update(
            {"ticket_id": {"type": PE.plain, "value": ticket_id}}
        )

        # 用户数据覆盖到pipeline_data
        if isinstance(user_data, Data):
            pipeline_tree["data"].update(user_data.to_dict())

        # update pipline_tree's id
        pipeline_tree.update(id=ticket_id)

        return {"pipeline_tree": pipeline_tree, "states_map": states_map}

    def create_pipeline(
        self,
        ticket_id,
        root_pipeline_data=None,
        need_start=False,
        use_cache=False,
        **kwargs
    ):
        """
        创建并返回pipeline对象
        :param ticket_id: 绑定ticket_id到pipeline中作为pipeline的id
        :param need_start: 选择性启动pipeline
        :param root_pipeline_data pipeline的结构数据
        :param use_cache 是否启用缓存
        :return: Pipeline Instance
        """

        pipeline_data = self.build_tree(ticket_id, use_cache=use_cache, **kwargs)

        # 解析并获得pipeline，传入全局上下文：root_pipeline_data
        if root_pipeline_data is None:
            root_pipeline_data = copy.deepcopy(kwargs)
            root_pipeline_data["ticket_id"] = ticket_id
        self.pipeline = PipelineParser(
            pipeline_data["pipeline_tree"], cycle_tolerate=True
        ).parse(
            root_pipeline_data=root_pipeline_data
        )  # parent_data

        # 更新pipeline_data
        if isinstance(self.flow, WorkflowVersion):
            self.update_cached_pipeline_data(pipeline_data)

        if need_start:
            t = time.time()
            self.start_pipeline()
            print("start_pipeline elapsed time: %s" % (time.time() - t))

        return pipeline_data

    def start_pipeline(self, check_workers=False):
        """
        启动pipeline
        :return: ActionResult{result/message/extra}

        # 任务激增时会耗尽worker，而_worker_check的检查会误认为：can not find celery workers，
        # 并因此放弃了启动pipeline的逻辑，导致部分单据漏掉，故这里去掉了worker的检查
        """

        action_result = task_service.run_pipeline(
            self.pipeline, check_workers=check_workers
        )
        if not action_result.result:
            logger.info("start pipeline error: %s" % action_result.message)

    def stop_pipeline(self):
        """终止pipeline
        :return: ActionResult{result/message/extra}
        """

        return task_service.revoke_pipeline(self.pipeline.id)

    @staticmethod
    def draw_pipeline(
        data,
        name="pipeline",
        dest=None,
        layout="LR",
        width=20,
        height=16,
        save=False,
        view=False,
    ):
        """
        绘制pipeline
        :param data: pipeline_tree
        :param width: 画布宽
        :param height: 画布高
        :param name: 流程名称
        :param layout: 布局：LR/UD
        """

        from graphviz import Digraph

        f = Digraph(name=name, filename="%s.gv" % name, format="png")

        # 左右布局
        f.attr(rankdir=layout, size="{},{}".format(width, height))

        # 节点类型->形状
        shapes = {
            "EmptyStartEvent": "circle",  # 'circle
            "EmptyEndEvent": "doublecircle",
            "ServiceActivity": "box",
            "ParallelGateway": "Mcircle",
            "ConvergeGateway": "Msquare",
            "ExclusiveGateway": "diamond",
        }

        # 节点（状态）信息
        start_event = data.get("start_event")
        end_event = data.get("end_event")
        activities = data.get("activities")
        flows = data.get("flows")
        gateways = data.get("gateways")

        # 添加节点：开始结束
        f.attr("node", shape=shapes["EmptyStartEvent"])
        f.node(name=start_event["id"], label="start")
        f.attr("node", shape=shapes["EmptyEndEvent"])
        f.node(name=end_event["id"], label="end")

        # 添加节点：Activity
        for nop, node in six.iteritems(activities):
            shape = shapes.get(node["type"])
            f.attr("node", shape=shape)
            f.node(name=str(node["id"]), label=node["name"])

        # 添加节点：Gateway
        for nop, node in six.iteritems(gateways):
            shape = shapes.get(node["type"])
            f.attr("node", shape=shape)
            f.node(name=str(node["id"]), label=node["name"])

        # 添加连线
        for nop, edge in six.iteritems(flows):
            from_node_id, to_node_id, label = edge["source"], edge["target"], "1==1"
            f.edge(from_node_id, to_node_id, label)

        if view:
            # 看效果
            f.view()

        # 保存为source
        f.save()

        # 不需要保存
        if not save:
            return

        # 保存为图片到dest或者当前目录下
        if dest is None:
            dest = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(dest, name), "wb") as output_file:
            output_file.write(f.pipe(format="png"))


class WorkflowPipelineWrapper(PipelineWrapper):
    def __init__(self, workflow):
        self.flow = workflow.tag_data()
        #     TODO 以下部分可以参照流程部署的方式来获取
        self.states = {
            str(state["id"]): state for state in list(self.flow.states.values())
        }
        self.transitions = {
            str(transition["id"]): transition
            for transition in list(self.flow.transitions.values())
        }

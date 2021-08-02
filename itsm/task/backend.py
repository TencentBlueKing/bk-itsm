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
#     建立Task和Pipeline的关系

import copy
import functools
from collections import OrderedDict, defaultdict

from django.db import transaction

from itsm.component.constants import TASK_PI_PREFIX, SOPS_TASK, NEW, QUEUE, DEVOPS_TASK
from itsm.task.models import Task
from itsm.task.serializers import TaskSerializer
from pipeline.builder import ServiceActivity, Var
from pipeline.core.constants import PE
from pipeline.parser import PipelineParser
from pipeline.service import task_service
from pipeline.utils.uniqid import node_uniqid, line_uniqid, uniqid


class TaskPipelineWrapper(object):
    def __init__(self, ticket_id, task_id):
        self.ticket_id = ticket_id
        self.task_id = task_id
        self.tasks = {}
        self.activities = {}
        self.data = {"inputs": {}, "outputs": {}}
        self.flows = {}
        self.gateways = {}
        self.start_event = None
        self.end_event = None
        self.pipeline = None
        self.set_tasks()

    def set_tasks(self):
        task_objs = Task.objects.filter(ticket_id=self.ticket_id, id=self.task_id)
        tasks = {i["id"]: i for i in TaskSerializer(instance=task_objs, many=True).data}
        # 调整task的数据结构，补充：unique_id、incoming、outgoing
        for task_id, task in tasks.items():
            task_unique_id = node_uniqid()
            # fill task's unique_id
            task.update({"unique_id": task_unique_id})

        self.tasks = tasks

    def get_task(self, task_id):
        return self.tasks.get(task_id, {})

    def get_tasks(self, task_ids):
        return OrderedDict({task_id: self.tasks[task_id] for task_id in task_ids if task_id in self.tasks})

    def get_task_flow(self):
        """
        :return: 示例: [[1], [2, 3], [4]]
        任务一、任务二、任务三、任务四对应任务ID分别为1、2、3、4
        等待`任务一`执行完成, `任务二、三`并行执行完成后, 最后执行`任务四`
        """
        order_task_mapping = defaultdict(list)
        for task_id, task in self.tasks.items():
            order_task_mapping[task["order"]].append(task_id)

        def custom_cmp(a, b):
            if int(a[0]) < int(b[0]):
                return -1
            else:
                return 1

        # 按照key(order)从小到大排序
        order_task_mapping_items = list(order_task_mapping.items())
        order_task_mapping_items.sort(key=functools.cmp_to_key(custom_cmp))
        return OrderedDict(order_task_mapping_items).values()

    def build_tree(self):
        """组装pipeline数据结构"""
        outgoing = self.build_start_event()
        outgoing = self.build_activity(self.task_id, [outgoing])
        self.build_end_event([outgoing])

        return {
            PE.id: "%s%s" % (TASK_PI_PREFIX, uniqid()[len(TASK_PI_PREFIX) :]),  # pipeline_id有长度限制
            PE.activities: self.activities,
            PE.gateways: self.gateways,
            PE.flows: self.flows,
            PE.data: self.data,
            PE.start_event: self.start_event,
            PE.end_event: self.end_event,
        }

    def build_leaf(self, task_flow, incoming):
        if len(task_flow) == 1:
            outgoing = self.build_activity(task_flow[0], [incoming])
        else:
            outgoing = self.build_scope(task_flow, [incoming])

        return outgoing

    def build_start_event(self):
        """创建开始节点"""
        start_event_id = node_uniqid()
        start_event_outgoing_flow = self.build_outgoing_flow(start_event_id)

        self.start_event = {
            PE.id: start_event_id,
            PE.name: "开始",
            PE.type: PE.EmptyStartEvent,
            PE.incoming: "",
            PE.outgoing: start_event_outgoing_flow["id"],
        }
        return self.start_event["outgoing"]

    def build_end_event(self, incoming):
        """创建结束节点"""
        self.end_event = {
            PE.id: node_uniqid(),
            PE.name: "结束",
            PE.type: PE.EmptyEndEvent,
            PE.incoming: incoming,
            PE.outgoing: "",
        }

        # 更新结束节点的入度线条的target
        self.set_flow_target(self.end_event["id"], *incoming)

    def build_scope(self, task_ids, incoming):
        """组装区域数据结构"""
        tasks = self.get_tasks(task_ids)
        converge_gateway_id, parallel_gateway_outgoings = self.build_conditional_parallel_gateway(tasks, incoming)
        # 将任务和入度线条进行一一对应
        index = 0
        converge_gateway_incoming = []
        for task_id, task in tasks.items():
            activity_outgoing = self.build_activity(task_id, [parallel_gateway_outgoings[index]])
            converge_gateway_incoming.append(activity_outgoing)
            index += 1

        converge_gateway_outgoing = self.build_converge_gateway(converge_gateway_id, converge_gateway_incoming)
        return converge_gateway_outgoing

    @staticmethod
    def build_component_for_task(task):
        """组装任务组件"""
        # 标准运维任务
        if task["component_type"] == SOPS_TASK:
            act = ServiceActivity("sops_task")
        # 蓝盾任务
        elif task["component_type"] == DEVOPS_TASK:
            act = ServiceActivity("devops_task")
        # 普通任务
        else:
            act = ServiceActivity("normal_task")

        act.component.inputs.task_id = Var(type=Var.PLAIN, value=str(task["id"]))
        return act.component_dict()

    def build_activity(self, task_id, incoming):
        """创建普通节点
        :param task_id: 任务ID
        :param incoming: 节点入度ID
        """
        task = self.get_task(task_id)
        # 节点出度线条信息
        activity_outgoing_flow = self.build_outgoing_flow(task["unique_id"])

        # 节点信息
        activity = {
            PE.id: task["unique_id"],
            PE.name: task["name"],
            PE.type: PE.ServiceActivity,
            PE.incoming: incoming,
            PE.outgoing: activity_outgoing_flow["id"],
            PE.component: self.build_component_for_task(task),
            PE.optional: False,
            PE.error_ignorable: False,
            "loop": {},
        }
        self.activities.update(**{activity["id"]: activity})
        # 更新节点的入度线条的target
        self.set_flow_target(activity["id"], *incoming)
        return activity["outgoing"]

    def build_conditional_parallel_gateway(self, tasks, incoming):
        """创建条件并行网关"""
        parallel_gateway_id = node_uniqid()
        converge_gateway_id = node_uniqid()

        # 创建条件并行网关的出度线条
        parallel_gateway_outgoings = []
        for _ in tasks.items():
            flow = self.build_outgoing_flow(parallel_gateway_id)
            parallel_gateway_outgoings.append(flow["id"])

        parallel_gateway = {
            PE.id: parallel_gateway_id,
            PE.name: "",
            PE.type: PE.ConditionalParallelGateway,
            PE.incoming: incoming,
            PE.outgoing: parallel_gateway_outgoings,
            PE.conditions: {outgoing: {"evaluate": " (1==1) "} for outgoing in parallel_gateway_outgoings},
            PE.converge_gateway_id: converge_gateway_id,
        }
        self.gateways.update(**{parallel_gateway["id"]: parallel_gateway})

        # 更新条件并行网关的入度线条的target
        self.set_flow_target(parallel_gateway["id"], *incoming)
        return converge_gateway_id, parallel_gateway["outgoing"]

    def build_outgoing_flow(self, source, target=""):
        """创建出度线条"""
        flow = {"id": line_uniqid(), "source": source, "target": target, "is_default": False}
        self.flows.update(**{flow["id"]: flow})
        return flow

    def set_flow_target(self, target, *flow_ids):
        """批量更新线条的target"""
        for flow_id in flow_ids:
            self.flows.get(flow_id, {}).update(target=target)

    def build_converge_gateway(self, converge_gateway_id, incoming):
        """创建汇聚网关"""
        # 汇聚网关出度线条信息
        converge_gateway_outgoing_flow = self.build_outgoing_flow(converge_gateway_id)

        converge_gateway = {
            PE.id: converge_gateway_id,
            PE.name: "",
            PE.type: PE.ConvergeGateway,
            PE.incoming: incoming,
            PE.outgoing: converge_gateway_outgoing_flow["id"],
        }
        self.gateways.update(**{converge_gateway["id"]: converge_gateway})

        # 更新条件并行网关的入度线条的target
        self.set_flow_target(converge_gateway["id"], *incoming)
        return converge_gateway["outgoing"]

    def create_pipeline(self, root_pipeline_data=None, **kwargs):
        """
        创建并返回pipeline对象
        :param ticket_id: 绑定ticket_id到pipeline中作为pipeline的id
        :param need_start: 选择性启动pipeline
        :param root_pipeline_data pipeline的结构数据
        :return: Pipeline Instance
        """

        pipeline_tree = self.build_tree()
        if not pipeline_tree:
            return

        # 解析并获得pipeline，传入全局上下文：root_pipeline_data
        if root_pipeline_data is None:
            root_pipeline_data = copy.deepcopy(kwargs)
            root_pipeline_data["ticket_id"] = self.ticket_id

        self.pipeline = PipelineParser(pipeline_tree, cycle_tolerate=False).parse(root_pipeline_data=root_pipeline_data)

        with transaction.atomic():
            Task.objects.filter(ticket_id=self.ticket_id, id=self.task_id).update(
                pipeline_data=pipeline_tree, activity_id=self.tasks[self.task_id]["unique_id"]
            )

        return pipeline_tree

    def start_pipeline(self, pipeline_data, check_workers=False):
        """
        启动pipeline
        :return: ActionResult{result/message/extra}
        """
        task_status = Task.objects.get(ticket_id=self.ticket_id, id=self.task_id).status
        if task_status not in [NEW, QUEUE]:
            return
        parser = PipelineParser(pipeline_tree=pipeline_data)
        pipeline = parser.parse(root_pipeline_data={"ticket_id": self.ticket_id})
        return task_service.run_pipeline(pipeline, check_workers=check_workers)

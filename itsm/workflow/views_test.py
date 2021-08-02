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

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.helper.utils import build_field_kwargs
from itsm.ticket.models import Ticket
from itsm.workflow.backend import PipelineWrapper
from itsm.workflow.models import State, Transition, Workflow, WorkflowVersion
from itsm.workflow.serializers import WorkflowSerializer
from pipeline import builder
from pipeline.builder import (
    ConditionalParallelGateway,
    ConvergeGateway,
    Data,
    EmptyEndEvent,
    EmptyStartEvent,
    ExclusiveGateway,
    NodeOutput,
    ParallelGateway,
    ServiceActivity,
    Var,
)
from pipeline.engine import api as pipeline_api
from pipeline.parser import PipelineParser
from pipeline.service import task_service


class TestViewSet(viewsets.ViewSet):
    """测试视图集合"""

    @action(detail=False, methods=['get'])
    def test_upgrade_workflow(self, request):

        flow_id = request.query_params.get('flow_id', None)
        new_flow = Workflow.objects.upgrade_workflow(flow_id)
        serializer = WorkflowSerializer(new_flow, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def test_upgrade_version(self, request):
        version_id = request.query_params.get('version_id', None)
        kwargs = build_field_kwargs()
        WorkflowVersion.objects.upgrade_version(version_id, for_migrate=True, **kwargs)

        return Response()

    @action(detail=False, methods=['get'])
    def test_draw_workflow_version(self, request):

        version_id = request.query_params.get('version_id')
        flow_version = WorkflowVersion.objects.get(id=version_id)
        Workflow.objects.draw_workflow(flow_version, 'miya', view=True, save=True)

        return Response()

    @action(detail=False, methods=['get'])
    def test_proceed(self, request):
        """简单流程构造测试 - ticket
        开始-》提单-》准备材料-》验收材料-》结束

        入口参数：
            1. 用户提交的表单数据
            2. 节点id
        """
        ticket_id = request.query_params.get('ticket_id')
        state_id = request.query_params.get('state_id')
        fields = request.data.get('fields')
        operator = request.user.username

        ticket = Ticket.objects.get(id=ticket_id)
        activity_id = ticket.activity_for_state(state_id)
        pipeline_api.activity_callback(
            activity_id,
            {"ticket_id": ticket_id, "state_id": state_id, "data": fields, "operator": operator}
        )
        return Response(task_service.get_state(activity_id))

    @action(detail=False, methods=['get'])
    def test_build_simple_workflow(self, request):
        """简单流程构造测试 - workflow
        开始-》提单-》准备材料-》验收材料-》结束
        """

        workflow = Workflow.objects.create(name="简单流程", is_enabled=True, flow_type='request')

        # 默认会创建States：开始/结束/提单，其他states为：
        states = {
            # name    type
            "审核": ("审核", 'NORMAL'),
            "准备材料": ("准备材料", 'NORMAL'),
            "验收材料": ("验收材料", 'NORMAL'),
        }

        name_to_state = {
            "开始": workflow.start_state,
            "提单": workflow.first_state,
            "结束": workflow.end_state,
        }

        # 创建其他states
        for state_name, state_data in states.items():
            state = State.objects.create(workflow=workflow, name=state_name, type=state_data[1])
            name_to_state[state_name] = state

        transitions = [
            ("开始", "提单", True),
            ("提单", "审核", True),
            ("审核", "准备材料", True),
            ("准备材料", "验收材料", True),
            ("验收材料", "结束", True),
        ]

        # 先清理，然后重新创建连线及条件
        workflow.transitions.all().delete()
        for transition in transitions:
            # 条件解析
            if transition[2] is True:
                # 1 == 1
                name, opt, value = "G_INT_1", "equal", 1
            else:
                name, opt, value = transition[2].split()

            obj, created = Transition.objects.get_or_create(
                defaults={
                    'condition': {
                        "expressions": [
                            {"type": "and",
                             "expressions": [{"name": name, "condition": opt, "value": value}]}
                        ],
                        "type": "and",
                    }
                },
                workflow=workflow,
                from_state=name_to_state[transition[0]],
                to_state=name_to_state[transition[1]],
            )

            print(obj, created)

        flow_version = workflow.create_version()
        Workflow.objects.draw_workflow(flow_version, 'miya', view=True, save=True)

        return Response({'id': flow_version.id, })

    @action(detail=False, methods=['get'])
    def test_convert_workflow(self, request):
        """复杂流程转换构造测试 - workflow"""

        version_id = request.query_params.get('id')

        try:
            flow = WorkflowVersion.objects.get(pk=version_id)
            Workflow.objects.draw_workflow(flow, flow.name, view=True, save=True)
        except Exception as e:
            return Response('Server 500: %s' % e)

        # 转化为pipeline
        pipeline_wrapper = PipelineWrapper(flow)
        pipeline_data = pipeline_wrapper.create_pipeline(1, need_start=False)

        PipelineWrapper.draw_pipeline(pipeline_data['pipeline_tree'], view=True, save=True)

        return Response(pipeline_data)

    @action(detail=False, methods=['get'])
    def test_run_simple1(self, request):
        """流程构造测试"""

        start = EmptyStartEvent()
        act_1 = ServiceActivity(component_code='pipe_example_component', name='act_1')
        eg = ExclusiveGateway(conditions={0: '${act_1_output} < 0', 1: '${act_1_output} >= 0'},
                              name='act_2 or act_3')
        act_2 = ServiceActivity(component_code='pipe_example_component', name='act_2')
        act_3 = ServiceActivity(component_code='pipe_example_component', name='act_3')
        end = EmptyEndEvent()

        start.extend(act_1).extend(eg).connect(act_2, act_3).to(eg).converge(end)

        act_1.component.inputs.input_a = Var(type=Var.SPLICE, value='${input_a}')

        pipeline_data = Data()
        pipeline_data.inputs['${input_a}'] = Var(type=Var.PLAIN, value=0)
        pipeline_data.inputs['${act_1_output}'] = NodeOutput(type=Var.SPLICE, source_act=act_1.id,
                                                             source_key='input_a')

        tree = builder.build_tree(start, data=pipeline_data)
        parser = PipelineParser(pipeline_tree=tree)
        pipeline = parser.parse(root_pipeline_data=pipeline_data.to_dict())

        print(json.dumps(tree, indent=2))

        task_service.run_pipeline(pipeline)

        print(json.dumps(task_service.get_state(pipeline.id), indent=2))
        return Response(tree)

    @action(detail=False, methods=['get'])
    def test_run_simple2(self, request):
        """流程构造测试"""

        start = EmptyStartEvent()
        act_1 = ServiceActivity(component_code='pipe_example_component', name='act_1')
        cpg = ConditionalParallelGateway(
            conditions={0: '${act_1_output} < 0', 1: '${act_1_output} >= 0',
                        2: '${act_1_output} >= 0'},
            name='[act_2] or [act_3 and act_4]',
        )
        act_2 = ServiceActivity(component_code='pipe_example_component', name='act_2')
        act_3 = ServiceActivity(component_code='pipe_example_component', name='act_3')
        act_4 = ServiceActivity(component_code='pipe_example_component', name='act_4')
        cg = ConvergeGateway()
        end = EmptyEndEvent()

        start.extend(act_1).extend(cpg).connect(act_2, act_3, act_4).to(cpg).converge(cg).extend(
            end)

        act_1.component.inputs.input_a = Var(type=Var.SPLICE, value='${input_a}')

        pipeline_data = Data()
        pipeline_data.inputs['${input_a}'] = Var(type=Var.PLAIN, value=0)
        pipeline_data.inputs['${act_1_output}'] = NodeOutput(type=Var.SPLICE, source_act=act_1.id,
                                                             source_key='input_a')

        tree = builder.build_tree(start, data=pipeline_data)
        parser = PipelineParser(pipeline_tree=tree)
        pipeline = parser.parse()

        task_service.run_pipeline(pipeline)
        print(json.dumps(task_service.get_state(pipeline.id), indent=2))
        return Response(tree)

    @action(detail=False, methods=['get'])
    def test_build_workflow(self, request):
        """复杂流程构造测试 - workflow"""

        workflow = Workflow.objects.create(name="xx制作流程", is_enabled=True, flow_type='request')

        # 默认会创建States：开始/结束/提单，其他states为：
        states = {
            # name    type
            "审核": ("审核", 'NORMAL'),
            "准备材料": ("准备材料", 'NORMAL'),
            "验收材料": ("验收材料", 'NORMAL'),
            "准备机器": ("准备机器", 'NORMAL'),
            "验收机器": ("验收机器", 'NORMAL'),
            "生产调试": ("生产调试", 'NORMAL'),
            "验收": ("验收", 'NORMAL'),
            # u"验收材料网关": (u"验收材料网关", 'ROUTER'),
            # u"验收机器网关": (u"验收机器网关", 'ROUTER'),
            # u"验收产品网关": (u"验收产品网关", 'ROUTER'),
            # u"审核网关": (u"审核网关", 'ROUTER'),
            "审核后并行网关": ("审核后并行网关", 'ROUTER-P'),
            "并行后汇聚网关": ("并行后汇聚网关", 'COVERAGE'),
        }

        name_to_state = {
            "开始": workflow.start_state,
            "提单": workflow.first_state,
            "结束": workflow.end_state,
        }

        nodes = [
            {'data': {'id': '开始'}},
            {'data': {'id': '提单'}},
            {'data': {'id': '结束'}},
        ]

        # 创建其他states
        for state_name, state_data in states.items():
            state = State.objects.create(workflow=workflow, name=state_name, type=state_data[1])

            name_to_state[state_name] = state

            nodes.append({'data': {'id': state_name}})

        edges = []
        transitions = [
            ("开始", "提单", True),
            ("提单", "审核", True),
            ("审核", "审核后并行网关", 'f_a equal "通过"'),
            ("审核", "结束", 'f_a unequal "通过"'),
            ("审核后并行网关", "准备材料", True),
            ("审核后并行网关", "准备机器", True),
            ("准备材料", "验收材料", True),
            ("准备机器", "验收机器", True),
            ("验收机器", "准备机器", 'f_a unequal "通过"'),
            ("验收机器", "并行后汇聚网关", 'f_a equal "通过"'),
            ("验收材料", "准备材料", 'f_a unequal "通过"'),
            ("验收材料", "并行后汇聚网关", 'f_a equal "通过"'),
            ("并行后汇聚网关", "生产调试", True),
            ("生产调试", "验收", True),
            ("验收", "生产调试", 'f_a unequal "通过"'),
            ("验收", "结束", 'f_a equal "通过"'),
        ]

        # 先清理，然后重新创建连线及条件
        workflow.transitions.all().delete()
        for transition in transitions:
            # 条件解析
            if transition[2] is True:
                # 1 == 1
                name, opt, value = "G_INT_1", "equal", 1
            else:
                name, opt, value = transition[2].split()

            obj, created = Transition.objects.get_or_create(
                defaults={
                    'condition': {
                        "expressions": [
                            {"type": "and",
                             "expressions": [{"name": name, "condition": opt, "value": value}]}
                        ],
                        "type": "and",
                    }
                },
                workflow=workflow,
                from_state=name_to_state[transition[0]],
                to_state=name_to_state[transition[1]],
            )

            edges.append({'data': {'source': transition[0], 'target': transition[1]}})

            print(obj, created)

        flow_version = workflow.create_version()
        Workflow.objects.draw_workflow(flow_version, 'miya', view=True, save=True)

        return Response({'id': flow_version.id, 'edges': edges, 'nodes': nodes})

    @action(detail=False, methods=['get'])
    def test_build_pipeline(self, request):
        """复杂流程构造测试 - pipeline"""

        start = EmptyStartEvent(name='start')
        end = EmptyEndEvent(name='end')

        tidan = ServiceActivity(component_code='pipe_example_component', name='tidan')
        shenhe = ServiceActivity(component_code='pipe_example_component', name='shenhe')
        eg_shenhe = ExclusiveGateway(conditions={0: '1==1', 1: '1==0'}, name='shenhe_ok?')

        prepare_cailiao = ServiceActivity(component_code='pipe_example_component',
                                          name='prepare_cailiao')
        prepare_jiqi = ServiceActivity(component_code='pipe_example_component', name='prepare_jiqi')

        check_cailiao = ServiceActivity(component_code='pipe_example_component',
                                        name='check_cailiao')
        eg_check_cailiao = ExclusiveGateway(conditions={0: '1==1', 1: '1==0'},
                                            name='shenhe_cailiao?')

        check_jiqi = ServiceActivity(component_code='pipe_example_component', name='check_jiqi')
        eg_check_jiqi = ExclusiveGateway(conditions={0: '1==1', 1: '1==0'}, name='shenhe_jiqi?')

        cg_cailiao_jiqi = ConvergeGateway(name='product_ready')
        pg_cailiao_jiqi = ParallelGateway(name='prepare')

        product = ServiceActivity(component_code='pipe_example_component', name='product')
        test = ServiceActivity(component_code='pipe_example_component', name='test')
        eg_test = ExclusiveGateway(conditions={0: '1==1', 1: '1==0'}, name='test_ok?')

        # 连线测试extend/to/connect
        start.extend(tidan).extend(shenhe).extend(eg_shenhe).extend(pg_cailiao_jiqi).to(
            eg_shenhe).extend(end)

        prepare_cailiao.extend(check_cailiao).extend(eg_check_cailiao)
        prepare_jiqi.extend(check_jiqi).extend(eg_check_jiqi)

        # 网关分支可以用connect，无环的网关间才能直接coverage
        eg_check_cailiao.connect(prepare_cailiao, cg_cailiao_jiqi)
        eg_check_jiqi.connect(prepare_jiqi, cg_cailiao_jiqi)
        pg_cailiao_jiqi.connect(prepare_cailiao, prepare_jiqi)

        cg_cailiao_jiqi.extend(product).extend(test).extend(eg_test)
        eg_test.connect(product, end)

        pipeline_data = Data()
        tree = builder.build_tree(start, data=pipeline_data)
        parser = PipelineParser(pipeline_tree=tree, cycle_tolerate=True)
        parser.parse()

        PipelineWrapper.draw_pipeline(tree, view=True, save=True)

        return Response(tree)

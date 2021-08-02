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

#     简单的工单流绘制：
#     说明：依赖[graphviz](https://graphviz.gitlab.io/download/)
#     http://graphviz.readthedocs.io/en/stable/examples.html
#     fsm.py - http://www.graphviz.org/content/fsm


import os

from graphviz import Digraph
from itsm.workflow.tests.pipeline_data import PIPELINE_DATA


# from itsm.workflow.pipeline import PipelineWrapper


def draw_pipeline(data, name='pipeline', dest=None, layout='LR', width=20, height=16, save=False, view=False):
    """
    绘制pipeline
    :param data: pipeline_tree
    :param width: 画布宽
    :param height: 画布高
    :param name: 流程名称
    :param layout: 布局：LR/UD
    """

    f = Digraph(name=name, filename='%s.gv' % name, format='png')

    # 左右布局
    f.attr(rankdir=layout, size='%s,%s' % (width, height))

    # 节点类型->形状
    shapes = {
        'EmptyStartEvent': 'circle',  # 'circle
        'EmptyEndEvent': 'doublecircle',
        'ServiceActivity': 'box',
        'ParallelGateway': 'Mcircle',
        'ConvergeGateway': 'Msquare',
        'ExclusiveGateway': 'diamond',
    }

    # 节点（状态）信息
    start_event = data.get('start_event')
    end_event = data.get('end_event')
    activies = data.get('activities')
    flows = data.get('flows')
    gateways = data.get('gateways')

    # 添加节点：开始结束
    f.attr('node', shape=shapes['EmptyStartEvent'])
    f.node(name=start_event['id'], label='start')
    f.attr('node', shape=shapes['EmptyEndEvent'])
    f.node(name=end_event['id'], label='end')

    # 添加节点：Activity
    for _, node in activies.items():
        shape = shapes.get(node['type'])
        f.attr('node', shape=shape)
        f.node(name=str(node['id']), label=node['name'])

    # 添加节点：Gateway
    for _, node in gateways.items():
        shape = shapes.get(node['type'])
        f.attr('node', shape=shape)
        f.node(name=str(node['id']), label=node['name'])

    # 添加连线
    for _, edge in flows.items():
        from_node_id, to_node_id, label = edge['source'], edge['target'], '1==1'
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

    with open(os.path.join(dest, name), 'wb') as output_file:
        output_file.write(f.pipe(format='png'))


if __name__ == '__main__':
    """
    工作流测试数据
    """

    draw_pipeline(data=PIPELINE_DATA, view=True, save=True)

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


from collections import OrderedDict

from graphviz import Digraph


def flow_example():

    f = Digraph('simple_ticket_flow', filename='fsm.gv', format='png')

    # 左右布局
    f.attr(rankdir='LR', size='8,3')
    # 上下布局
    # f.attr(rankdir='UD', size='8,3')

    # 节点类型->形状
    shapes = {
        'START': 'ellipse',  # 'circle
        'END': 'ellipse',
        'NORMAL': 'box',  # 'ellipse'
        'ROUTER': 'diamond',
    }

    # 节点（状态）信息
    nodes = OrderedDict(
        {
            1: {'id': 1, 'name': '开始', 'type': 'START'},
            2: {'id': 2, 'name': '提单', 'type': 'NORMAL'},
            3: {'id': 3, 'name': '审核', 'type': 'NORMAL'},
            4: {'id': 4, 'name': '实施', 'type': 'NORMAL'},
            5: {'id': 5, 'name': '验证', 'type': 'ROUTER'},
            6: {'id': 6, 'name': '结束', 'type': 'END'},
        }
    )

    # 节点连接信息
    edges = [
        (1, 2, ''),
        (2, 3, '提交'),
        (3, 4, '通过'),
        (4, 5, ''),
        (5, 4, '不通过'),
        (5, 6, '通过'),
        (3, 6, '不通过'),
    ]

    # 添加节点
    for _, node in nodes.items():
        shape = shapes.get(node['type'])
        f.attr('node', shape=shape)
        f.node(name=str(node['id']), label=node['name'])

    # 添加连线
    # f.edges(edges)
    # f.clear()
    for edge in edges:
        from_node_id, to_node_id, label = edge
        f.edge(str(from_node_id), str(to_node_id), label)

    # 看效果
    f.view()
    # 保存为source
    f.save()
    # 保存为图片
    with open('test.png', 'wb') as output_file:
        output_file.write(f.pipe(format='png'))


if __name__ == '__main__':
    flow_example()

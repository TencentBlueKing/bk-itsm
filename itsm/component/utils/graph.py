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


def dfs_paths(graph, start, goal, skip_circle=True):
    """
    深度优先搜索，找到图graph中start->goal中的所有路径
    return all possible paths between a start and goal vertex.
    list(dfs_paths(graph, 'A', 'F'))
    :param graph:   {'A': set(['B', 'C']),
                     'B': set(['A', 'D', 'E']),
                     'C': set(['A', 'F']),
                     'D': set(['B']),
                     'E': set(['B', 'F']),
                     'F': set(['C', 'E'])}
    :param start: 'A'
    :param goal: 'F'
    :param skip_circle: True，是否忽略环
    :return: [['A', 'C', 'F'], ['A', 'B', 'E', 'F']]

    算法思路：选定一个出发点进行遍历，如果有未被访问的邻接点，则继续前进，若不能继续前进，则回退一步，
    若回退一步仍不能前进，则一直回退到可以前进的位置。重复该过程，直到所有与选定点连通的顶点都被遍历

    算法实现：采用栈的方式来实现，
        1、先将起点（和历史路径）入栈，然后标记起点为顶点；
        2、出栈一个顶点和历史路径；
        3、选取任一邻接点，若邻接点为目标点，则命中一条路径，否则将该邻接点入栈（顶点和路径）；
        4、若当前顶点无可前进的邻接点，则出栈最近一次压入的邻接点
        5、重复上面的操作，直至栈空为止
        得到的迭代器结果即为从起始顶点到目标顶点的路径列表的迭代器

    https://eddmann.com/posts/depth-first-search-and-breadth-first-search-in-python/
    https://xiaozhuanlan.com/topic/8623547109
    """
    stack = [(start, [start])]
    while stack:
        (vertex, path) = stack.pop()
        # print vertex, path

        # detect circle path
        if not skip_circle:
            intersection = set(path) & graph[vertex]
            if start in intersection:
                yield path + [goal]

        for next in graph[vertex] - set(path):
            if next == goal:
                yield path + [next]
            else:
                stack.append((next, path + [next]))

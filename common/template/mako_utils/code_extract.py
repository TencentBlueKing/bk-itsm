# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2025 Tencent. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import abc

from mako import parsetree
from mako.ast import PythonFragment

from .exceptions import ForbiddenMakoTemplateException


class MakoNodeCodeExtractor:
    @abc.abstractmethod
    def extract(self, node):
        """
        处理 Mako Lexer 分割出来的节点，返回需要做 AST 安全检查的 Python 代码。

        返回值：
        - None：该节点无需检查
        - str：单个 Python 代码片段
        - list[str]：多个独立 Python 代码片段（例如 Expression 的主表达式 + 各 filter）
        """
        raise NotImplementedError()


class StrictMakoNodeCodeExtractor(MakoNodeCodeExtractor):
    def extract(self, node):
        if isinstance(node, parsetree.Code) or isinstance(node, parsetree.Expression):
            return node.text
        elif isinstance(node, parsetree.ControlLine):
            if node.isend:
                return None
            return PythonFragment(node.text).code
        elif isinstance(node, parsetree.Text):
            return None
        else:
            raise ForbiddenMakoTemplateException("不支持[{}]节点".format(node.__class__.__name__))

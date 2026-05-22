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

# Mako 安全工具


import ast

from mako import parsetree

from common.template.mako_utils.code_extract import MakoNodeCodeExtractor
from common.template.mako_utils.exceptions import ForbiddenMakoTemplateException


FORBIDDEN_TEMPLATE_METHODS = {"format", "format_map"}


class SingleLineNodeVisitor(ast.NodeVisitor):
    """
    遍历语法树节点，遇到魔术方法使用或 import 时，抛出异常
    """

    def __init__(self, *args, **kwargs):
        super(SingleLineNodeVisitor, self).__init__(*args, **kwargs)

    @staticmethod
    def _get_subscript_key(node):
        slice_node = node.slice
        if isinstance(slice_node, ast.Index):
            slice_node = slice_node.value

        if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
            return slice_node.value

        if hasattr(ast, "Str") and isinstance(slice_node, ast.Str):
            return slice_node.s

        return None

    def visit_Attribute(self, node):
        if node.attr.startswith("__"):
            raise ForbiddenMakoTemplateException("can not access private attribute")
        if node.attr in FORBIDDEN_TEMPLATE_METHODS:
            raise ForbiddenMakoTemplateException("can not call forbidden method")
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id.startswith("__"):
            raise ForbiddenMakoTemplateException("can not access private method")
        self.generic_visit(node)

    def visit_Subscript(self, node):
        subscript_key = self._get_subscript_key(node)
        if isinstance(subscript_key, str) and subscript_key.startswith("__"):
            raise ForbiddenMakoTemplateException("can not access private key")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_TEMPLATE_METHODS:
            raise ForbiddenMakoTemplateException("can not call forbidden method")
        self.generic_visit(node)

    def visit_Import(self, node):
        raise ForbiddenMakoTemplateException("can not use import statement")

    def visit_ImportFrom(self, node):
        self.visit_Import(node)


# mako 内置 filter 白名单（'n' 表示不转义，非 Python 表达式，无需 AST 校验）
MAKO_BUILTIN_FILTER_WHITELIST = {"n"}


class SingleLinCodeExtractor(MakoNodeCodeExtractor):
    """
    抽取需要做 AST 安全检查的 Python 代码片段。

    返回值契约：
    - list[str]：一个或多个独立的 Python 代码片段，调用方需逐条解析校验
    - None：无需检查
    异常：遇到不支持的节点直接抛 ForbiddenMakoTemplateException
    """

    def extract(self, node):
        if isinstance(node, parsetree.Code):
            return [node.text]
        if isinstance(node, parsetree.Expression):
            codes = [node.text]
            # ${expr | filter} 中 filter 同样会作为 Python 代码参与渲染，
            # 必须与主表达式一并送入 AST 黑名单校验，避免绕过。
            for arg in node.escapes_code.args:
                if arg in MAKO_BUILTIN_FILTER_WHITELIST:
                    continue
                codes.append(arg)
            return codes
        if isinstance(node, parsetree.Text):
            return None
        raise ForbiddenMakoTemplateException("Unsupported node: [{}]".format(node.__class__.__name__))

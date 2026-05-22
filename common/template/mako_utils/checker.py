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


import ast
from typing import List

from mako import parsetree
from mako.exceptions import MakoException
from mako.lexer import Lexer

from .code_extract import MakoNodeCodeExtractor
from .exceptions import ForbiddenMakoTemplateException


def parse_template_nodes(
    nodes: List[parsetree.Node],
    node_visitor: ast.NodeVisitor,
    code_extractor: MakoNodeCodeExtractor,
):
    """
    解析 mako 模板节点，逐节点抽取 Python 代码片段并做 AST 安全检查。

    code_extractor.extract 契约：
    - 返回 None：跳过
    - 返回 str 或 list[str]：每个片段都需独立 ast.parse 后送入 visitor
    """
    for node in nodes:
        code = code_extractor.extract(node)
        if code is None:
            continue

        code_snippets = [code] if isinstance(code, str) else list(code)
        for snippet in code_snippets:
            ast_node = ast.parse(snippet, "<unknown>", "exec")
            node_visitor.visit(ast_node)

        if hasattr(node, "nodes"):
            parse_template_nodes(node.nodes, node_visitor, code_extractor)


def check_mako_template_safety(text: str, node_visitor: ast.NodeVisitor, code_extractor: MakoNodeCodeExtractor) -> bool:
    """
    检查mako模板是否安全，若不安全直接抛出异常，安全则返回True
    :param text: mako模板内容
    :param node_visitor: 节点访问器，用于遍历AST节点
    """
    try:
        lexer_template = Lexer(text).parse()
    except MakoException as mako_error:
        raise ForbiddenMakoTemplateException("非mako模板，解析失败, {err_msg}".format(err_msg=mako_error.__class__.__name__))
    parse_template_nodes(lexer_template.nodes, node_visitor, code_extractor)
    return True

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

# Mako 安全工具


import ast
import re

from mako import parsetree

from common.template.mako_utils.code_extract import MakoNodeCodeExtractor
from common.template.mako_utils.exceptions import ForbiddenMakoTemplateException

FORBIDDEN_TEMPLATE_METHODS = {"format", "format_map"}
SAFE_FILTERS = {"n", "h", "x", "u", "trim", "entity", "unicode", "str"}
SAFE_DECODE_FILTER_PATTERN = re.compile(r"^decode\.[A-Za-z0-9][A-Za-z0-9_.-]*$")


class SingleLineNodeVisitor(ast.NodeVisitor):
    """
    遍历语法树节点，遇到魔术方法使用或 import 时，抛出异常
    """

    def __init__(self, *args, **kwargs):
        super(SingleLineNodeVisitor, self).__init__(*args, **kwargs)

    @staticmethod
    def _unwrap_slice(node):
        """兼容 Python<3.9 的 ast.Index 包装"""
        slice_node = node.slice
        if hasattr(ast, "Index") and isinstance(slice_node, ast.Index):
            slice_node = slice_node.value
        return slice_node

    @staticmethod
    def _check_subscript_slice(slice_node):
        """
        白名单式校验下标表达式：
        - 常量字符串：拒绝以 "_" 开头的（含 dunder 与单下划线私有命名）
        - 数字 / 布尔 / None 常量、切片、纯变量名、元组（多维下标）：放行
        - 其他（BinOp / Call / JoinedStr / IfExp / Subscript / Attribute / Lambda 等动态拼接）：一律拒绝
        """
        # 1) 常量字符串 / 数字 / 布尔 / None
        if isinstance(slice_node, ast.Constant):
            value = slice_node.value
            if isinstance(value, str):
                if value.startswith("_"):
                    raise ForbiddenMakoTemplateException(
                        "can not access private key: [{}]".format(value)
                    )
                return
            if isinstance(value, (int, float, bool)) or value is None:
                return
            raise ForbiddenMakoTemplateException(
                "unsupported subscript constant type: [{}]".format(type(value).__name__)
            )

        # 2) py<3.8 字符串/数字节点（向后兼容）
        if hasattr(ast, "Str") and isinstance(slice_node, ast.Str):
            if slice_node.s.startswith("_"):
                raise ForbiddenMakoTemplateException(
                    "can not access private key: [{}]".format(slice_node.s)
                )
            return
        if hasattr(ast, "Num") and isinstance(slice_node, ast.Num):
            return

        # 3) 切片 obj[a:b:c]
        if isinstance(slice_node, ast.Slice):
            return

        # 4) 纯变量名 obj[var]：放行（变量值由上下文决定，结合 visit_Name 的私有名拦截可形成纵深防御）
        if isinstance(slice_node, ast.Name):
            return

        # 5) 多维下标 obj[a, b]：递归校验每一维
        if isinstance(slice_node, ast.Tuple):
            for elt in slice_node.elts:
                SingleLineNodeVisitor._check_subscript_slice(elt)
            return

        # 6) 其他一切动态表达式（BinOp/Call/JoinedStr/IfExp/Subscript/Attribute/Lambda/...）
        raise ForbiddenMakoTemplateException(
            "dynamic subscript is forbidden: [{}]".format(type(slice_node).__name__)
        )

    def visit_Attribute(self, node):
        # 与 visit_Subscript 中字符串常量阈值保持一致：禁止访问任何下划线起始的私有属性
        # 防御 Django ORM 内省链：obj._meta / obj._state / Model._default_manager 等
        if node.attr.startswith("_"):
            raise ForbiddenMakoTemplateException(
                "can not access private attribute: [{}]".format(node.attr)
            )
        if node.attr in FORBIDDEN_TEMPLATE_METHODS:
            raise ForbiddenMakoTemplateException("can not call forbidden method")
        self.generic_visit(node)

    def visit_Name(self, node):
        # 收紧到单下划线，与 visit_Attribute / visit_Subscript 一致，禁止读取私有变量名
        if node.id.startswith("_"):
            raise ForbiddenMakoTemplateException(
                "can not access private name: [{}]".format(node.id)
            )
        self.generic_visit(node)

    def visit_Subscript(self, node):
        slice_node = self._unwrap_slice(node)
        self._check_subscript_slice(slice_node)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_TEMPLATE_METHODS:
            raise ForbiddenMakoTemplateException("can not call forbidden method")
        self.generic_visit(node)

    def visit_Import(self, node):
        raise ForbiddenMakoTemplateException("can not use import statement")

    def visit_ImportFrom(self, node):
        self.visit_Import(node)


def validate_filter_args(filter_args):
    for filter_arg in filter_args:
        normalized_filter = filter_arg.strip()
        if normalized_filter in SAFE_FILTERS:
            continue
        decode_filter_parts = normalized_filter.split(".")
        if (
            SAFE_DECODE_FILTER_PATTERN.match(normalized_filter)
            and "__" not in normalized_filter
            and not any(part.startswith("_") for part in decode_filter_parts[1:])
        ):
            continue
        raise ForbiddenMakoTemplateException("unsupported filter expression: [{}]".format(normalized_filter))


class SingleLinCodeExtractor(MakoNodeCodeExtractor):
    def extract(self, node):
        if isinstance(node, parsetree.Code) or isinstance(node, parsetree.Expression):
            return node.text
        elif isinstance(node, parsetree.Text):
            return None
        else:
            raise ForbiddenMakoTemplateException("Unsupported node: [{}]".format(node.__class__.__name__))

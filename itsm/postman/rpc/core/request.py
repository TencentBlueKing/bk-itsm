# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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

import ast
import json
import re

from common.log import logger
from common.template.template import Template
from common.utils import sanitize_user_content
from itsm.postman.constants import TICKET_CONTEXT_KEY, TRIGGER_SOURCE
from itsm.ticket.models import Ticket, TicketGlobalVariable
from itsm.trigger.models import Trigger

SAFE_RPC_PLACEHOLDER_PATTERN = re.compile(r"\$\{([^{}]+)\}")


class CompRequest(object):
    """
    Request class for Component
    """

    def __init__(self, data, method="RPC"):
        self.data = data
        self.kwargs = {}
        self.query_params = {}
        self.method = method

    @classmethod
    def _get_safe_subscript_key(cls, node):
        slice_node = node.slice
        if hasattr(ast, "Index") and isinstance(slice_node, ast.Index):
            slice_node = slice_node.value

        if isinstance(slice_node, ast.Constant):
            if isinstance(slice_node.value, (str, int)):
                return slice_node.value
        elif hasattr(ast, "Str") and isinstance(slice_node, ast.Str):
            return slice_node.s
        elif hasattr(ast, "Num") and isinstance(slice_node, ast.Num):
            return slice_node.n

        raise ValueError("rpc_api meta only supports constant dict/list indexes")

    @classmethod
    def _resolve_safe_expression(cls, node, params_context):
        if isinstance(node, ast.Name):
            if not node.id.startswith("params_"):
                raise ValueError("rpc_api meta only supports params_* variables")
            if node.id not in params_context:
                raise KeyError(node.id)
            return params_context[node.id]

        if isinstance(node, ast.Subscript):
            parent = cls._resolve_safe_expression(node.value, params_context)
            subscript_key = cls._get_safe_subscript_key(node)
            if isinstance(parent, dict):
                return parent[subscript_key]
            if isinstance(parent, (list, tuple)) and isinstance(subscript_key, int):
                return parent[subscript_key]
            raise ValueError("rpc_api meta index type is invalid")

        raise ValueError("rpc_api meta only supports variable reference expressions")

    @classmethod
    def _resolve_safe_placeholder(cls, expression, params_context):
        try:
            parsed = ast.parse(expression.strip(), mode="eval")
        except SyntaxError as error:
            raise ValueError("rpc_api meta expression is invalid") from error
        return cls._resolve_safe_expression(parsed.body, params_context)

    @classmethod
    def _render_safe_rpc_string(cls, value, params_context):
        matches = list(SAFE_RPC_PLACEHOLDER_PATTERN.finditer(value))
        if not matches:
            return value

        if len(matches) == 1 and matches[0].span() == (0, len(value)):
            return cls._resolve_safe_placeholder(matches[0].group(1), params_context)

        rendered = []
        last_index = 0
        for match in matches:
            rendered.append(value[last_index:match.start()])
            rendered.append(
                str(cls._resolve_safe_placeholder(match.group(1), params_context))
            )
            last_index = match.end()
        rendered.append(value[last_index:])
        return "".join(rendered)

    @classmethod
    def _safe_render_rpc_meta(cls, value, params_context):
        if isinstance(value, dict):
            return {
                key: cls._safe_render_rpc_meta(item, params_context)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [cls._safe_render_rpc_meta(item, params_context) for item in value]
        if isinstance(value, tuple):
            return tuple(
                cls._safe_render_rpc_meta(item, params_context) for item in value
            )
        if isinstance(value, str):
            return cls._render_safe_rpc_string(value, params_context)
        return value

    @classmethod
    def parse_params(cls, params, safe_mode=False):
        params_context = {"params_%s" % key: value for key, value in params.items()}
        rpc_source = params.get("rpc_source")
        # 判断是否包括单据上下文
        if TICKET_CONTEXT_KEY in params:
            ticket_id = params["ticket_id"]
            ticket = Ticket.objects.get(id=ticket_id)

            params_context.update(
                {
                    "params_%s" % field["key"]: field["_value"]
                    for field in ticket.fields.filter(_value__isnull=False)
                    .exclude(_value="")
                    .values("key", "_value")
                }
            )
            params_context.update(
                {
                    "params_%s" % item["key"]: item["value"]
                    for item in TicketGlobalVariable.objects.filter(
                        ticket_id=ticket_id
                    ).values("key", "value")
                }
            )

        template = params.get("meta", {})
        try:
            if safe_mode:
                query_params = cls._safe_render_rpc_meta(template, params_context)
            else:
                query_params = json.loads(
                    Template(json.dumps(template)).render(**params_context)
                )
        except Exception as e:
            logger.warning(
                "Template text=%s, context=%s, error=%s",
                sanitize_user_content(template),
                sanitize_user_content(params),
                e,
            )
            return False, []

        if rpc_source == TRIGGER_SOURCE:
            # 触发器默认增加两个参数
            try:
                trigger = Trigger.objects.get(id=params.get("rpc_source_id"))
            except Trigger.DoesNotExist:
                return False, []
            query_params.update(
                {
                    "trigger_source_id": trigger.source_id,
                    "trigger_source_type": trigger.source_type,
                }
            )
        return True, query_params

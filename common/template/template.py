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

import re
import logging

from typing import Any, List, Set

from mako.template import Template as MakoTemplate
from mako import lexer, codegen
from mako.exceptions import MakoException

from common.template.mako_utils import mako_safety
from common.template.mako_utils.checker import check_mako_template_safety
from common.template.mako_utils.exceptions import ForbiddenMakoTemplateException
from common.template.mako_utils.string import deformat_var_key
from common.template.sandbox import Sandbox, _ForbiddenProxy
from common.utils import sanitize_user_content

logger = logging.getLogger("root")
# find mako template(format is ${xxx}，and ${}# not in xxx, # may raise memory error)
TEMPLATE_PATTERN = re.compile(r"\${[^${}#]+}")
NESTED_INDEX_STR_PATTERN = r'^(\w+)(?:\[(?:"\w+"|\'\w+\'|\d+)\])+$'
INDEX_STR_PATTERN = r'\[("\w+"|\'\w+\'|\d+)\]'

# 渲染数据中需要额外注入屏蔽代理的 Mako runtime 名。
# 注：Mako 运行时会在模板执行命名空间内自动注入 self/local/context 等；这里在 data 中
# 同步覆盖一份 _ForbiddenProxy，作为静态层 AST 白名单之外的纵深防御。若 Mako 运行时
# 优先使用自身注入对象，本层覆盖无副作用；若有遗漏的代码路径读到 data 中的同名键，
# 任何属性访问/调用/格式化都会立即抛 ForbiddenMakoTemplateException。
_RUNTIME_SHIELD_KEYS = ("self", "local", "context", "caller", "next", "parent", "capture")


class Template:
    def __init__(self, data: Any):
        self.data = data

    def get_reference(self, deformat=False) -> Set[str]:
        """
        获取当前数据中模板所引用的所有标志符

        :return: 标志符列表
        :rtype: List[str]
        """

        reference = []
        templates = self.get_templates()
        for tpl in templates:
            reference += self._get_template_reference(tpl)
        reference = set(reference)
        if not deformat:
            reference = {"${%s}" % r for r in reference}

        return reference

    def get_templates(self) -> List[str]:
        """
        获取当前数据中所有的模板片段

        :return: 模板片段列表
        :rtype: List[str]
        """
        templates = []
        data = self.data
        if isinstance(data, str):
            templates += self._get_string_templates(data)
        if isinstance(data, (list, tuple)):
            for item in data:
                templates += Template(item).get_templates()
        if isinstance(data, dict):
            for value in list(data.values()):
                templates += Template(value).get_templates()
        return list(set(templates))

    def render(self, context: dict = None, **kwargs) -> Any:
        """
        渲染当前模板

        :param context: 模板渲染上下文
        :type context: dict
        :return: 模板渲染后的数据
        :rtype: Any
        """
        data = self.data
        if not isinstance(data, str):
            raise Exception(
                "render type error, template[%s] is not a string" % self.data
            )

        context = context or kwargs
        if isinstance(data, str):
            return self._render_string(data, context)

    def _get_string_templates(self, string) -> List[str]:
        return list(set(TEMPLATE_PATTERN.findall(string)))

    def _get_template_reference(self, template: str) -> List[str]:
        lex = lexer.Lexer(template)

        try:
            node = lex.parse()
        except MakoException as e:
            logger.warning("pipeline get template[%s] reference error[%s]", template, e)
            return []

        # Dummy compiler. _Identifiers class requires one
        # but only interested in the reserved_names field
        def compiler():
            return None

        compiler.reserved_names = set()
        identifiers = codegen._Identifiers(compiler, node)

        return list(identifiers.undeclared)

    def _render_string(self, string: str, context: dict) -> str:
        """
        使用特定上下文渲染指定模板

        :param string: 模板
        :type string: str
        :param context: 上下文
        :type context: dict
        :return: 渲染后的模板
        :rtype: str
        """
        if not isinstance(string, str):
            return string
        templates = self._get_string_templates(string)

        # TODO keep render return object, here only process simple situation
        if len(templates) == 1 and templates[0] == string:
            deformat_string = deformat_var_key(string)

            # directly get value from context
            if deformat_string in context:
                return context[deformat_var_key(string)]

        for tpl in templates:
            try:
                check_mako_template_safety(
                    tpl,
                    mako_safety.SingleLineNodeVisitor(),
                    mako_safety.SingleLinCodeExtractor(),
                )
            except ForbiddenMakoTemplateException as e:
                logger.warning(
                    "forbidden template: %s, exception: %s",
                    sanitize_user_content(tpl),
                    e,
                )
                continue
            except Exception:
                logger.exception("%s safety check error.", sanitize_user_content(tpl))
                continue
            resolved = Template._render_template(tpl, context)
            string = string.replace(tpl, str(resolved))
        return string

    @staticmethod
    def _nested_get_value_from_context(context: Any, string: str) -> Any:
        """
        从上下文中获取嵌套数据的值，仅支持 list/tuple/dict，且需保证索引合法，外层需要处理异常
        """
        cur_context = context
        for key in re.findall(INDEX_STR_PATTERN, string):
            if isinstance(cur_context, dict):
                cur_context = cur_context[key.strip("'\"")]
            elif isinstance(cur_context, (list, tuple)):
                cur_context = cur_context[int(key)]
            else:
                raise ValueError("invalid context type: %s", type(cur_context))
        return cur_context

    @staticmethod
    def _render_template(template: str, context: dict) -> Any:
        """
        使用特定上下文渲染指定模板

        :param template: 模板
        :type template: Any
        :param context: 上下文
        :type context: dict
        :raises TypeError: [description]
        :return: [description]
        :rtype: str
        """
        data = {}
        data.update(context)
        data.update(Sandbox().get())
        # 运行时纵深防御：覆盖 Mako Namespace 相关名为屏蔽代理，禁止经由 data 抵达 self.module 等
        for shield_key in _RUNTIME_SHIELD_KEYS:
            data[shield_key] = _ForbiddenProxy(shield_key)

        if not isinstance(template, str):
            raise TypeError(
                "constant resolve error, template[%s] is not a string", template
            )
        try:
            tm = MakoTemplate(template)
        except (MakoException, SyntaxError) as e:
            logger.error(
                "pipeline resolve template[%s] error[%s]",
                sanitize_user_content(template),
                e,
            )
            return template
        try:
            resolved = tm.render_unicode(**data)
        except Exception as e:
            # 严格模式下，沙箱屏蔽词的 _ForbiddenProxy 在 __repr__/__str__ 中也会抛异常，
            # 因此这里禁止直接将 data 字典（含代理对象）传入 logger 格式化，
            # 改为仅记录上下文键名 + 异常类型/消息，避免日志静默丢失，且降低敏感数据外溢风险。
            logger.warning(
                "constant content(%s) is invalid, context_keys=%s, error_type=%s, error=%s",
                sanitize_user_content(template),
                sorted(list(context.keys())) if isinstance(context, dict) else type(context).__name__,
                type(e).__name__,
                sanitize_user_content(str(e)),
            )
            return template
        else:
            return resolved

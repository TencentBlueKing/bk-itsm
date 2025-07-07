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

import copy
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
from common.template.sandbox import Sandbox

logger = logging.getLogger("root")
# find mako template(format is ${xxx}，and ${}# not in xxx, # may raise memory error)
TEMPLATE_PATTERN = re.compile(r"\${[^${}#]+}")
NESTED_INDEX_STR_PATTERN = r'^(\w+)(?:\[(?:"\w+"|\'\w+\'|\d+)\])+$'
INDEX_STR_PATTERN = r'\[("\w+"|\'\w+\'|\d+)\]'


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

    def render(self, context: dict=None, **kwargs) -> Any:
        """
        渲染当前模板

        :param context: 模板渲染上下文
        :type context: dict
        :return: 模板渲染后的数据
        :rtype: Any
        """
        data = self.data
        
        context = context or kwargs
        if isinstance(data, str):
            return self._render_string(data, context)
        if isinstance(data, list):
            ldata = [""] * len(data)
            for index, item in enumerate(data):
                ldata[index] = Template(copy.deepcopy(item)).render(context)
            return ldata
        if isinstance(data, tuple):
            ldata = [""] * len(data)
            for index, item in enumerate(data):
                ldata[index] = Template(copy.deepcopy(item)).render(context)
            return tuple(ldata)
        if isinstance(data, dict):
            for key, value in list(data.items()):
                data[key] = Template(copy.deepcopy(value)).render(context)
            return data
        return data

    def _get_string_templates(self, string) -> List[str]:
        return list(set(TEMPLATE_PATTERN.findall(string)))

    def _get_template_reference(self, template: str) -> List[str]:
        lex = lexer.Lexer(template)

        try:
            node = lex.parse()
        except MakoException as e:
            logger.warning("pipeline get template[{}] reference error[{}]".format(template, e))
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
                logger.warning("forbidden template: {}, exception: {}".format(tpl, e))
                continue
            except Exception:
                logger.exception("{} safety check error.".format(tpl))
                continue
            resolved = Template._render_template(tpl, context)
            string = string.replace(tpl, resolved)
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
                raise ValueError("invalid context type: {}".format(type(cur_context)))
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
        
        if not isinstance(template, str):
            raise TypeError("constant resolve error, template[%s] is not a string" % template)
        try:
            tm = MakoTemplate(template)
        except (MakoException, SyntaxError) as e:
            logger.error("pipeline resolve template[{}] error[{}]".format(template, e))
            return template
        try:
            resolved = tm.render_unicode(**data)
        except Exception as e:
            logger.warning("constant content({}) is invalid, data({}), error: {}".format(template, data, e))
            return template
        else:
            return resolved

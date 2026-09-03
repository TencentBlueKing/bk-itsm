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

from django.conf import settings
from mako.template import Template as MakoTemplate
from mako import lexer, codegen
from mako.exceptions import MakoException

from common.template import sandbox
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
#
# 直接复用 mako_safety.MAKO_RESERVED_NAMESPACES 作为唯一事实源（single source of truth），
# 保证静态层 AST 白名单与运行时屏蔽两层完全对齐，避免后续维护时遗漏。
# 额外加入 "capture"（Mako 内置的 capture() 调用代理，也可作为 SSTI 跳板）。
_RUNTIME_SHIELD_KEYS = tuple(mako_safety.MAKO_RESERVED_NAMESPACES)




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
        if context is None:
            context = kwargs
        elif kwargs:
            context = {**context, **kwargs}
        data = self.data
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
            return {
                key: Template(copy.deepcopy(value)).render(context)
                for key, value in data.items()
            }
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
                return context[deformat_string]

            # nested get value from tuple/list/dict
            match = re.match(NESTED_INDEX_STR_PATTERN, deformat_string)
            if settings.ENABLE_RENDER_OBJ_BY_MAKO_STRING and match and match.group(1) in context:
                try:
                    return self._nested_get_value_from_context(context[match.group(1)], deformat_string)
                except Exception as e:
                    logger.exception("render obj from nested mako string failed: {}".format(e))
                    pass

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
                    sanitize_user_content(str(e)),
                )
                continue
            except Exception:
                logger.exception(
                    "%s safety check error.",
                    sanitize_user_content(tpl),
                )
                continue

            # 根标识符白名单：fail-secure，模式缺失/非法（含 "off"）一律回退 enforce
            whitelist_mode = getattr(settings, "MAKO_TEMPLATE_NAME_WHITELIST_MODE", "enforce")
            if whitelist_mode not in {"warn", "enforce"}:
                logger.warning(
                    "[mako-safety] invalid MAKO_TEMPLATE_NAME_WHITELIST_MODE=%r, fallback to 'enforce'",
                    whitelist_mode,
                )
                whitelist_mode = "enforce"
            try:
                allowed_names = mako_safety.build_allowed_names(context)
                check_mako_template_safety(
                    tpl,
                    mako_safety.WhitelistNameVisitor(allowed_names, mode=whitelist_mode),
                    mako_safety.SingleLinCodeExtractor(),
                )
            except ForbiddenMakoTemplateException as e:
                logger.warning(
                    "forbidden by whitelist: %s, exception: %s",
                    sanitize_user_content(tpl),
                    sanitize_user_content(str(e)),
                )
                continue
            except Exception:
                logger.exception(
                    "%s whitelist check error.",
                    sanitize_user_content(tpl),
                )
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
        # 注入顺序极其关键：
        #   1) 先放业务 ``context``，允许业务字段进入命名空间；
        #   2) 再用 ``sandbox.get()`` 覆盖，确保 ``eval``/``exec``/``globals``/
        #      ``getattr``/``__import__`` 等屏蔽词永远是 ``_ForbiddenProxy``，
        #      即便业务 context 中存在同名键也无法绕过；
        #   3) 最后差异化覆盖 Mako 保留命名空间名（``self``/``context`` 强制覆盖，
        #      其它如 ``next``/``parent``/``local`` 仅在 data 中不存在同名键时注入，
        #      避免误伤业务字段）。
        if not isinstance(template, str):
            raise TypeError("constant resolve error, template[%s] is not a string" % template)

        try:
            tm = MakoTemplate(template)
        except (MakoException, SyntaxError) as e:
            logger.error("pipeline resolve template[{}] error[{}]".format(template, e))
            return template

        data = {}
        data.update(context)
        data.update(Sandbox().get())

        # 高危核心名：无条件覆盖。SSTI 主入口，绝不让步。
        for shield_key in ("self", "context"):
            data[shield_key] = _ForbiddenProxy(shield_key)
        # 其它 Mako 保留名：仅在不存在同名业务键时注入，避免误伤。
        for shield_key in _RUNTIME_SHIELD_KEYS:
            if shield_key in ("self", "context"):
                continue
            if shield_key not in data:
                data[shield_key] = _ForbiddenProxy(shield_key)

        # Mako 的渲染入口签名为 ``render_unicode(self, *args, **data)``，而模板编译出的
        # ``render_body(context, **pageargs)`` 会把 ``context`` 作为位置参数。若 ``data``
        # 中包含这些保留名，会导致：
        #   - ``self``            -> 与 render_unicode 的 bound-method 首参撞名
        #                              ("got multiple values for argument 'self'")
        #   - ``context``/``UNDEFINED``/``STOP_RENDERING``/``loop`` -> Mako 在
        #     ``Context._set_with_template`` 里检测到保留字后会抛 NameConflictError。
        # 这些名即便注入到 ``data`` 也无法在运行期生效：
        #   * ``self``/``local``：Mako 在 ``_populate_self_namespace`` 中会用真实
        #     TemplateNamespace 覆盖 ``_data``；
        #   * ``context``/``UNDEFINED``/``STOP_RENDERING``：Mako 编译期把它们编译成
        #     直接引用（LOAD_FAST/LOAD_GLOBAL），根本不走 ``context.get()``。
        # 因此这里统一从渲染 kwargs 中剔除，运行期防护由 AST 白名单（enforce 模式）保证，
        # 其余经 ``context.get()`` 解析的屏蔽词（module/cache/util/...）仍保留在 ``data``
        # 中发挥作用。
        for reserved_name in tm.reserved_names | {"self"}:
            data.pop(reserved_name, None)

        try:
            resolved = tm.render_unicode(**data)
        except Exception as e:
            # 注意：``data`` 中含 ``_ForbiddenProxy`` 实例，其 ``__repr__`` 会主动抛
            # ForbiddenMakoTemplateException。如果直接 ``"{}".format(data)`` 整段打印，
            # 异常会从本 except 块二次逃逸，导致这条审计日志彻底丢失。
            # 这里只打印 data 的"键名集合"用于排障，不触达任何 value 的 repr。
            try:
                data_keys = sorted(data.keys())
            except Exception:  # pragma: no cover - defensive
                data_keys = "<unprintable>"
            logger.warning(
                "constant content(%s) is invalid, data_keys=%s, error: %s",
                template, data_keys, e,
            )
            return template
        else:
            return resolved

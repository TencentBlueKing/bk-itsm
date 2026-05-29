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
#
# 契约：
# - 表达式静态检查走 AST 白名单（最小可用），其余 AST 节点一律 ForbiddenMakoTemplateException
# - Call 仅放行两类：
#   1) 字符串方法白名单 SAFE_STR_METHODS
#   2) 受信模块成员调用白名单 SAFE_MODULE_CALL_WHITELIST（与 sandbox.MAKO_SANDBOX_IMPORT_MODULES 对齐）
# - 任意 Call 形态均禁止链式（Call.func.value 为 Call）、禁止解包、禁止参数侧嵌套 Call


import ast
import logging
import re

from django.conf import settings
from mako import parsetree

from common.template.mako_utils.code_extract import MakoNodeCodeExtractor
from common.template.mako_utils.exceptions import ForbiddenMakoTemplateException
from common.template.sandbox import MAKO_SANDBOX_FORBIDDEN_MODULES

logger = logging.getLogger("root")

FORBIDDEN_TEMPLATE_METHODS = {"format", "format_map"}
SAFE_FILTERS = {"n", "h", "x", "u", "trim", "entity", "unicode", "str"}
SAFE_DECODE_FILTER_PATTERN = re.compile(r"^decode\.[A-Za-z0-9][A-Za-z0-9_.-]*$")

# 与 ``MAKO_SANDBOX_SHIELD_WORDS`` 不重叠的"安全内建函数"集合。
# 用于白名单模式下默认放行的根标识符。
# 不包含 ``bytes/bytearray/frozenset/memoryview/object/type/vars/getattr/...``
# 等常出现在 shield 列表中的内建——它们即便能通过 AST 也会在渲染期被屏蔽成 ``None``，
# 留在白名单里只会带来认知噪音。
SAFE_BUILTIN_NAMES = frozenset(
    {
        "True",
        "False",
        "None",
        # 类型构造（不会构造危险对象）
        "bool",
        "int",
        "float",
        "str",
        "list",
        "tuple",
        "dict",
        "set",
        # 数学 / 长度
        "abs",
        "round",
        "pow",
        "sum",
        "min",
        "max",
        "len",
        # 序列
        "range",
        "slice",
        "enumerate",
        "zip",
        "sorted",
        "reversed",
        # 逻辑
        "all",
        "any",
    }
)

# Mako 在渲染期会向模板命名空间注入的保留对象名，用户模板里出现这些名字时
# 极大概率是在尝试触达模板内部对象（``self.module.cache.util.os...`` SSTI 链路）。
# 对它们直接拒绝，可以堵住绝大多数 namespace 链式 RCE 路径。
MAKO_RESERVED_NAMESPACES = frozenset(
    {
        "self",
        "context",
        "local",
        "parent",
        "next",
        "caller",
        "pageargs",
        "UNDEFINED",
        "STOP_RENDERING",
        # ``self.module.cache.util.os...`` 经典 SSTI 链路上的中段标识符。
        # 即便用户绕过 ``self`` 通过其它路径取到这些对象，根标识符层也独立拒绝，
        # 不再单纯依赖 ``self`` 截断。
        "module",
        "cache",
        "util",
    }
)


class SingleLineNodeVisitor(ast.NodeVisitor):
    """
    遍历语法树节点，遇到魔术方法使用或 import 时，抛出异常
    """

    def __init__(self, *args, **kwargs):
        super(SingleLineNodeVisitor, self).__init__(*args, **kwargs)

    @staticmethod
    def _get_subscript_key(node):
        slice_node = node.slice
        if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
            return slice_node.value
        if hasattr(ast, "Str") and isinstance(slice_node, ast.Str):
            return slice_node.s
        return None

    def visit_Attribute(self, node):
        # 一律拦截下划线开头的属性，覆盖：
        #   1) ``__xxx`` / ``__xxx__`` —— Python 魔术方法 / 私有名（经典 SSTI 跳板，
        #      如 ``__class__``、``__mro__``、``__subclasses__``、``__builtins__``）
        #   2) ``_xxx``               —— PEP 8 约定的非公开 API，含 Django ``_meta``/
        #      ``_state``、SQLAlchemy ``_sa_instance_state`` 等 ORM 反射跳板
        # 业务模板按惯例不会暴露下划线开头字段，因此用一条通用规则替代具名黑名单，
        # 实现"未来新增内部属性也不必维护黑名单"的默认安全。
        if node.attr.startswith("_"):
            raise ForbiddenMakoTemplateException(
                "can not access private/sensitive attribute: {}".format(node.attr)
            )
        if node.attr in FORBIDDEN_TEMPLATE_METHODS:
            raise ForbiddenMakoTemplateException("can not call forbidden method")
        self.generic_visit(node)

    def visit_Name(self, node):
        # Name 仅拦截 dunder 前缀：
        # 顶层标识符以单下划线开头是 Python 中常见的合法命名（如循环变量 ``_``），
        # 真正危险的根标识符（``self``/``context``/``os``/``sys``/...）已由
        # ``WhitelistNameVisitor`` + ``MAKO_RESERVED_NAMESPACES`` +
        # ``MAKO_SANDBOX_FORBIDDEN_MODULES`` 三层兜底拦截。
        if node.id.startswith("__"):
            raise ForbiddenMakoTemplateException("can not access private method")
        self.generic_visit(node)

    def visit_Subscript(self, node):
        # 同步覆盖 ``${obj["_meta"]}`` / ``${obj["__class__"]}`` 等通过下标
        # 绕过属性访问的形态，与 visit_Attribute 的拦截范围完全对称，
        # 杜绝"属性拦了但下标没拦"的不对称漏洞。
        subscript_key = self._get_subscript_key(node)
        if isinstance(subscript_key, str) and subscript_key.startswith("_"):
            raise ForbiddenMakoTemplateException(
                "can not access private/sensitive key: {}".format(subscript_key)
            )
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


def _deformat_var_key(key):
    """``${name}`` -> ``name``；其它 key 原样返回。"""
    if isinstance(key, str) and key.startswith("${") and key.endswith("}"):
        return key[2:-1]
    return key


def build_allowed_names(context, *, extra=()):
    """根据当前渲染 context 与全局 ``Settings`` 计算白名单的根标识符集合。

    包含：
      * ``context`` 中的键（``${name}`` 形式自动 deformat）
      * ``Settings.MAKO_SANDBOX_IMPORT_MODULES`` 中每个 alias 的首段
        （例：``os.path`` → ``os``）
      * :data:`SAFE_BUILTIN_NAMES`
      * ``Settings.MAKO_TEMPLATE_NAME_EXTRA_WHITELIST``
      * 调用方传入的 ``extra``
    """

    allowed = set(SAFE_BUILTIN_NAMES)

    for key in context.keys() if context else ():
        allowed.add(_deformat_var_key(key))

    import_modules = getattr(settings, "MAKO_SANDBOX_IMPORT_MODULES", {})
    for alias in import_modules.values():
        if alias:
            allowed.add(alias.split(".", 1)[0])

    extra_whitelist = getattr(settings, "MAKO_TEMPLATE_NAME_EXTRA_WHITELIST", ())
    allowed.update(extra_whitelist)
    allowed.update(extra)

    # 终极兜底：无论 context / settings / extra 如何配置，
    # 危险模块名和 Mako 保留命名空间都必须从白名单中剔除。
    # 这样即使管理员误把 "os" 写入 MAKO_SANDBOX_IMPORT_MODULES 或
    # MAKO_TEMPLATE_NAME_EXTRA_WHITELIST，AST 静态层依然会拒绝，
    # 实现"默认安全（secure by default）"。
    allowed -= MAKO_SANDBOX_FORBIDDEN_MODULES
    allowed -= MAKO_RESERVED_NAMESPACES

    return allowed


class WhitelistNameVisitor(ast.NodeVisitor):
    """根标识符白名单 visitor。

    只允许 Load 语义的 ``Name`` 节点引用 ``allowed_names`` 中的标识符；其余一律按
    ``mode`` 处理：

      * ``warn``：调用 ``on_violation`` / 打 warning 日志，**不抛异常**（灰度模式）。
      * ``enforce``：抛 :exc:`ForbiddenMakoTemplateException`，由
        :func:`bamboo_engine.utils.mako_utils.checker.check_mako_template_safety` 捕获。

    本 visitor 还显式拦截 :data:`MAKO_RESERVED_NAMESPACES` 中的标识符，
    无论是否被传入 ``allowed_names`` 都会被拒，避免误把 ``self/context/...`` 加进
    上下文导致 SSTI 链路被放行。

    支持 ``ListComp / SetComp / DictComp / GeneratorExp / Lambda`` 引入的局部
    绑定——这些临时变量会被压入作用域栈，在子树访问完后自动弹出。
    """

    def __init__(self, allowed_names, mode="enforce", on_violation=None):
        if mode not in {"warn", "enforce"}:
            raise ValueError("invalid whitelist mode: {}".format(mode))
        self.allowed_names = set(allowed_names)
        self.mode = mode
        self.on_violation = on_violation
        self.scope_stack = []

    def _name_allowed(self, name):
        if name in MAKO_RESERVED_NAMESPACES:
            return False
        if name in self.allowed_names:
            return True
        for scope in self.scope_stack:
            if name in scope:
                return True
        return False

    def _violate(self, name, reason):
        msg = "name not in whitelist: {} ({})".format(name, reason)
        if self.on_violation is not None:
            try:
                self.on_violation(name, reason)
            except Exception:  # pragma: no cover - defensive
                logger.exception("on_violation callback raised")
        if self.mode == "enforce":
            raise ForbiddenMakoTemplateException(msg)
        logger.warning("[mako_whitelist] %s", msg)

    @staticmethod
    def _collect_targets(target, into):
        if isinstance(target, ast.Name):
            into.add(target.id)
        elif isinstance(target, ast.Starred):
            WhitelistNameVisitor._collect_targets(target.value, into)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                WhitelistNameVisitor._collect_targets(elt, into)

    def visit_Name(self, node):
        # Store / Del 上下文是赋值/删除目标，由 _enter_* 显式处理，跳过命名检查
        if not isinstance(node.ctx, ast.Load):
            return
        if node.id in MAKO_RESERVED_NAMESPACES:
            self._violate(node.id, "mako reserved namespace")
            return
        if not self._name_allowed(node.id):
            self._violate(node.id, "not in whitelist")

    def _enter_comprehension(self, node):
        local = set()
        for gen in node.generators:
            self._collect_targets(gen.target, local)
        self.scope_stack.append(local)
        try:
            self.generic_visit(node)
        finally:
            self.scope_stack.pop()

    def visit_ListComp(self, node):
        self._enter_comprehension(node)

    def visit_SetComp(self, node):
        self._enter_comprehension(node)

    def visit_DictComp(self, node):
        self._enter_comprehension(node)

    def visit_GeneratorExp(self, node):
        self._enter_comprehension(node)

    def visit_Lambda(self, node):
        local = set()
        args = node.args
        local.update(arg.arg for arg in args.args)
        local.update(arg.arg for arg in args.kwonlyargs)
        local.update(arg.arg for arg in getattr(args, "posonlyargs", ()) or ())
        if args.vararg:
            local.add(args.vararg.arg)
        if args.kwarg:
            local.add(args.kwarg.arg)
        self.scope_stack.append(local)
        try:
            self.generic_visit(node)
        finally:
            self.scope_stack.pop()

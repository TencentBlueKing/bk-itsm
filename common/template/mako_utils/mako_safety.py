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

# 字符串方法白名单：仅放行无副作用、返回 str/bool/int/list[str] 的内置 str 方法。
# 显式不含 format/format_map（统一沿用 FORBIDDEN_TEMPLATE_METHODS）、encode（产 bytes）、
# translate/maketrans（dict 参数易滥用）以及任何 _ 前缀方法。
SAFE_STR_METHODS = {
    "upper", "lower", "swapcase", "title", "capitalize", "casefold",
    "strip", "lstrip", "rstrip",
    "startswith", "endswith",
    "isdigit", "isalpha", "isalnum", "isspace", "isascii",
    "islower", "isupper", "istitle",
    "replace", "split", "rsplit", "splitlines", "join",
    "zfill", "center", "ljust", "rjust",
    "removeprefix", "removesuffix",
    "count", "find", "rfind", "index", "rindex",
}

# dict 写方法白名单：放行带副作用的 dict 写入，但仍受参数侧/链根/私有属性等所有现有约束保护。
SAFE_DICT_MUTATION_METHODS = {"update", "setdefault"}

# 受信模块成员调用白名单：与 common.template.sandbox.MAKO_SANDBOX_IMPORT_MODULES 对齐。
# 顶层 key 为模板上下文中可见的模块根名；value 为允许出现在属性链/链尾方法名中的 token 集合。
# 链路上每一段 attr 均需命中对应集合，否则拒。
SAFE_MODULE_CALL_WHITELIST = {
    "datetime": {
        # 类型/类
        "datetime", "date", "time", "timedelta", "timezone",
        # 类方法/工厂
        "now", "utcnow", "today", "fromtimestamp", "utcfromtimestamp",
        "fromisoformat", "fromordinal", "combine",
        # 实例方法/属性
        "strftime", "isoformat", "timetuple",
        "replace", "astimezone",
        "year", "month", "day", "hour", "minute", "second", "microsecond",
        "weekday", "isoweekday",
    },
    "time": {
        "time", "monotonic", "perf_counter", "process_time",
        "strftime", "strptime", "gmtime", "localtime", "mktime", "asctime", "ctime",
        "sleep",
    },
}

# 与 ``MAKO_SANDBOX_SHIELD_WORDS`` 不重叠的安全内建根名集合（白名单模式默认放行）。
SAFE_BUILTIN_NAMES = frozenset(
    {
        "True",
        "False",
        "None",
        "bool",
        "int",
        "float",
        "str",
        "list",
        "tuple",
        "dict",
        "set",
        "abs",
        "round",
        "pow",
        "sum",
        "min",
        "max",
        "len",
        "range",
        "slice",
        "enumerate",
        "zip",
        "sorted",
        "reversed",
        "all",
        "any",
    }
)

# Mako 在渲染期注入的保留命名空间名（含 ``self.module.cache.util.os`` SSTI 链路中段标识符）。
# 由原始 FORBIDDEN_ROOT_NAMES（self/local/context/...）与 2.8 侧扩展（module/cache/util/pageargs）并集而来。
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
        "module",
        "cache",
        "util",
        "capture",
    }
)


def _is_pure_value_node(node):
    """判断节点是否为纯取值表达式：常量 / Name / Attribute / Subscript / Tuple / List 嵌套。"""
    if isinstance(node, ast.Constant):
        return True
    if hasattr(ast, "Str") and isinstance(node, ast.Str):
        return True
    if hasattr(ast, "Num") and isinstance(node, ast.Num):
        return True
    if isinstance(node, ast.Name):
        return True
    if isinstance(node, ast.Attribute):
        return _is_pure_value_node(node.value)
    if isinstance(node, ast.Subscript):
        return _is_pure_value_node(node.value)
    if isinstance(node, (ast.Tuple, ast.List)):
        return all(_is_pure_value_node(elt) for elt in node.elts)
    return False


def _attribute_chain_root(node):
    """返回 Attribute/Name 链的根 Name 节点（仅当链全部由 Attribute 组成且根为 Name）；否则 None。"""
    cur = node
    while isinstance(cur, ast.Attribute):
        cur = cur.value
    if isinstance(cur, ast.Name):
        return cur
    return None


def _attribute_chain_attrs(node):
    """收集 Attribute 链上的所有 attr 名（不含根 Name）。"""
    attrs = []
    cur = node
    while isinstance(cur, ast.Attribute):
        attrs.append(cur.attr)
        cur = cur.value
    return attrs


class SingleLineNodeVisitor(ast.NodeVisitor):
    """AST 白名单 visitor。

    放行：Module/Expression/Load、Name、Attribute、Subscript、Constant、Tuple/List、Call(受限)。
    其它节点一律拒绝（BinOp/BoolOp/UnaryOp/Compare/IfExp/Lambda/Comp*/JoinedStr/FormattedValue/
    Yield*/Await/Starred/NamedExpr/Import* 等）。
    """

    @staticmethod
    def _unwrap_slice(node):
        slice_node = node.slice
        if hasattr(ast, "Index") and isinstance(slice_node, ast.Index):
            slice_node = slice_node.value
        return slice_node

    @staticmethod
    def _check_subscript_slice(slice_node):
        """白名单式校验下标：常量(非 _ 前缀字符串)/数字/布尔/None/纯变量名/多维元组放行；其它拒。"""
        if isinstance(slice_node, ast.Constant):
            value = slice_node.value
            if isinstance(value, str):
                if value.startswith("_"):
                    raise ForbiddenMakoTemplateException(f"can not access private key: [{value}]")
                return
            if isinstance(value, (int, float, bool)) or value is None:
                return
            raise ForbiddenMakoTemplateException(
                f"unsupported subscript constant type: [{type(value).__name__}]"
            )
        if hasattr(ast, "Str") and isinstance(slice_node, ast.Str):
            if slice_node.s.startswith("_"):
                raise ForbiddenMakoTemplateException(f"can not access private key: [{slice_node.s}]")
            return
        if hasattr(ast, "Num") and isinstance(slice_node, ast.Num):
            return
        if isinstance(slice_node, ast.Name):
            if slice_node.id.startswith("_") or slice_node.id in MAKO_RESERVED_NAMESPACES:
                raise ForbiddenMakoTemplateException(
                    f"can not use forbidden name as subscript: [{slice_node.id}]"
                )
            return
        if isinstance(slice_node, ast.Tuple):
            for elt in slice_node.elts:
                SingleLineNodeVisitor._check_subscript_slice(elt)
            return
        # Slice / BinOp / Call / JoinedStr / IfExp / Subscript / Attribute / Lambda 等动态形态：一律拒
        raise ForbiddenMakoTemplateException(
            f"dynamic subscript is forbidden: [{type(slice_node).__name__}]"
        )

    def visit_Module(self, node):
        self.generic_visit(node)

    def visit_Expression(self, node):
        self.generic_visit(node)

    def visit_Expr(self, node):
        self.generic_visit(node)

    def visit_Load(self, node):
        return

    def visit_Name(self, node):
        if node.id.startswith("_"):
            raise ForbiddenMakoTemplateException(f"can not access private name: [{node.id}]")
        if node.id in MAKO_RESERVED_NAMESPACES:
            raise ForbiddenMakoTemplateException(f"can not access runtime name: [{node.id}]")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr.startswith("_"):
            raise ForbiddenMakoTemplateException(f"can not access private attribute: [{node.attr}]")
        if node.attr in FORBIDDEN_TEMPLATE_METHODS:
            raise ForbiddenMakoTemplateException("can not call forbidden method")
        # 不允许"调用结果再点属性"形态：Attribute.value=Call，否则绕过链式 Call 检查
        if isinstance(node.value, ast.Call):
            raise ForbiddenMakoTemplateException("attribute access on call result is not allowed")
        # 兜底：链根命中保留命名空间 → 拒（防 self.module.cache.util.os.popen 类链）
        root = _attribute_chain_root(node)
        if root is not None:
            if root.id in MAKO_RESERVED_NAMESPACES:
                raise ForbiddenMakoTemplateException(
                    f"can not access runtime namespace chain: [{root.id}]"
                )
            # 受信模块根：链路上每一段 attr 必须命中对应集合
            if root.id in SAFE_MODULE_CALL_WHITELIST:
                allowed = SAFE_MODULE_CALL_WHITELIST[root.id]
                for attr in _attribute_chain_attrs(node):
                    if attr not in allowed:
                        raise ForbiddenMakoTemplateException(
                            f"module attribute not in whitelist: [{root.id}.{attr}]"
                        )
        self.generic_visit(node)

    def visit_Subscript(self, node):
        slice_node = self._unwrap_slice(node)
        self._check_subscript_slice(slice_node)
        self.generic_visit(node)

    def visit_Constant(self, node):
        return

    def visit_Tuple(self, node):
        self.generic_visit(node)

    def visit_List(self, node):
        self.generic_visit(node)

    def visit_Call(self, node):
        # 形态：Call.func 必须是 Attribute(value=<取值表达式>, attr=<白名单方法>)
        if not isinstance(node.func, ast.Attribute):
            raise ForbiddenMakoTemplateException(
                "only attribute method call is allowed in mako expression"
            )
        # 禁链式 Call
        if isinstance(node.func.value, ast.Call):
            raise ForbiddenMakoTemplateException("chained call is not allowed")
        # 禁解包
        for a in node.args:
            if isinstance(a, ast.Starred):
                raise ForbiddenMakoTemplateException("starred arg is not allowed")
        for kw in node.keywords:
            if kw.arg is None:
                raise ForbiddenMakoTemplateException("**kwargs is not allowed")
            if kw.arg.startswith("_"):
                raise ForbiddenMakoTemplateException(f"can not use private keyword arg: [{kw.arg}]")

        method_attr = node.func.attr
        if method_attr.startswith("_"):
            raise ForbiddenMakoTemplateException(f"can not call private method: [{method_attr}]")
        if method_attr in FORBIDDEN_TEMPLATE_METHODS:
            raise ForbiddenMakoTemplateException("can not call forbidden method")

        # 分支判定：链根命中受信模块 → 走模块成员调用白名单；否则走字符串方法白名单
        root = _attribute_chain_root(node.func)
        if root is not None and root.id in SAFE_MODULE_CALL_WHITELIST:
            allowed = SAFE_MODULE_CALL_WHITELIST[root.id]
            for attr in _attribute_chain_attrs(node.func):
                if attr not in allowed:
                    raise ForbiddenMakoTemplateException(
                        f"module attribute not in whitelist: [{root.id}.{attr}]"
                    )
        else:
            if method_attr not in SAFE_STR_METHODS and method_attr not in SAFE_DICT_MUTATION_METHODS:
                raise ForbiddenMakoTemplateException(
                    f"method not in safe method whitelist: [{method_attr}]"
                )

        # 实参约束：仅纯取值，不允许嵌套 Call/Lambda/BinOp/Compare/IfExp/推导式/Set/Dict 等
        for a in node.args:
            if not _is_pure_value_node(a):
                raise ForbiddenMakoTemplateException(
                    f"unsafe argument node: [{type(a).__name__}]"
                )
        for kw in node.keywords:
            if not _is_pure_value_node(kw.value):
                raise ForbiddenMakoTemplateException(
                    f"unsafe keyword argument node: [{type(kw.value).__name__}]"
                )

        self.generic_visit(node)

    def visit_Import(self, node):
        raise ForbiddenMakoTemplateException("can not use import statement")

    def visit_ImportFrom(self, node):
        self.visit_Import(node)

    def visit_Lambda(self, node):
        raise ForbiddenMakoTemplateException("lambda is not allowed")

    def visit_FunctionDef(self, node):
        raise ForbiddenMakoTemplateException("function definition is not allowed")

    def visit_AsyncFunctionDef(self, node):
        raise ForbiddenMakoTemplateException("async function definition is not allowed")

    def visit_ClassDef(self, node):
        raise ForbiddenMakoTemplateException("class definition is not allowed")

    def visit_GeneratorExp(self, node):
        raise ForbiddenMakoTemplateException("generator expression is not allowed")

    def visit_ListComp(self, node):
        raise ForbiddenMakoTemplateException("list comprehension is not allowed")

    def visit_SetComp(self, node):
        raise ForbiddenMakoTemplateException("set comprehension is not allowed")

    def visit_DictComp(self, node):
        raise ForbiddenMakoTemplateException("dict comprehension is not allowed")

    def visit_JoinedStr(self, node):
        raise ForbiddenMakoTemplateException("f-string is not allowed")

    def visit_FormattedValue(self, node):
        raise ForbiddenMakoTemplateException("f-string is not allowed")

    def visit_Yield(self, node):
        raise ForbiddenMakoTemplateException("yield is not allowed")

    def visit_YieldFrom(self, node):
        raise ForbiddenMakoTemplateException("yield from is not allowed")

    def visit_Await(self, node):
        raise ForbiddenMakoTemplateException("await is not allowed")

    def visit_Starred(self, node):
        raise ForbiddenMakoTemplateException("starred is not allowed")

    def visit_NamedExpr(self, node):
        raise ForbiddenMakoTemplateException("walrus expression is not allowed")

    def visit_BinOp(self, node):
        raise ForbiddenMakoTemplateException("binary operator is not allowed")

    def visit_BoolOp(self, node):
        raise ForbiddenMakoTemplateException("boolean operator is not allowed")

    def visit_UnaryOp(self, node):
        raise ForbiddenMakoTemplateException("unary operator is not allowed")

    def visit_Compare(self, node):
        raise ForbiddenMakoTemplateException("compare is not allowed")

    def visit_IfExp(self, node):
        raise ForbiddenMakoTemplateException("if expression is not allowed")

    def visit_Set(self, node):
        raise ForbiddenMakoTemplateException("set literal is not allowed")

    def visit_Dict(self, node):
        raise ForbiddenMakoTemplateException("dict literal is not allowed")

    def visit_Slice(self, node):
        raise ForbiddenMakoTemplateException("slice expression is not allowed")

    # generic_visit：兜底拒绝所有未知节点类型
    def generic_visit(self, node):
        allowed_types = (
            ast.Module, ast.Expression, ast.Expr, ast.Load,
            ast.Name, ast.Attribute, ast.Subscript, ast.Constant,
            ast.Tuple, ast.List, ast.Call, ast.keyword,
        )
        legacy = []
        for legacy_name in ("Str", "Num", "NameConstant", "Bytes"):
            if hasattr(ast, legacy_name):
                legacy.append(getattr(ast, legacy_name))
        allowed_types = allowed_types + tuple(legacy)
        if not isinstance(node, allowed_types):
            raise ForbiddenMakoTemplateException(
                f"ast node is not in whitelist: [{type(node).__name__}]"
            )
        super().generic_visit(node)


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
        raise ForbiddenMakoTemplateException(f"unsupported filter expression: [{normalized_filter}]")


class SingleLinCodeExtractor(MakoNodeCodeExtractor):
    def extract(self, node):
        if isinstance(node, parsetree.Code) or isinstance(node, parsetree.Expression):
            return node.text
        elif isinstance(node, parsetree.Text):
            return None
        else:
            raise ForbiddenMakoTemplateException(f"Unsupported node: [{node.__class__.__name__}]")


def _deformat_var_key(key):
    """``${name}`` -> ``name``；其它 key 原样返回。"""
    if isinstance(key, str) and key.startswith("${") and key.endswith("}"):
        return key[2:-1]
    return key


def build_allowed_names(context, *, extra=()):
    """根据当前渲染 context 与全局 Settings 计算白名单的根标识符集合。

    包含 context 键、MAKO_SANDBOX_IMPORT_MODULES 别名首段、SAFE_BUILTIN_NAMES、
    MAKO_TEMPLATE_NAME_EXTRA_WHITELIST 与 extra；再强制剔除危险模块名与保留命名空间。
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

    allowed -= MAKO_SANDBOX_FORBIDDEN_MODULES
    allowed -= MAKO_RESERVED_NAMESPACES

    return allowed


class WhitelistNameVisitor(ast.NodeVisitor):
    """根标识符白名单 visitor。

    只允许 Load 语义的 Name 引用 allowed_names 中的标识符；其余按 mode 处理：
    warn 打日志不拦截（灰度），enforce 抛 ForbiddenMakoTemplateException。
    显式拦截 MAKO_RESERVED_NAMESPACES，避免误把 self/context/... 加进上下文导致放行。
    """

    def __init__(self, allowed_names, mode="enforce", on_violation=None):
        if mode not in {"warn", "enforce"}:
            raise ValueError(f"invalid whitelist mode: {mode}")
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
        msg = f"name not in whitelist: {name} ({reason})"
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

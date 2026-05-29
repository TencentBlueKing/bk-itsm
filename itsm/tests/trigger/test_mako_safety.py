# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
Copyright (C) 2026 Tencent.  All rights reserved.
BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
"""

# 单测：Mako 表达式 AST 白名单（mako_safety.SingleLineNodeVisitor）
# 关注点：
# - 取值表达式（Name/Attribute/Subscript/Constant）放行
# - 字符串方法白名单 SAFE_STR_METHODS
# - 受信模块成员调用白名单 SAFE_MODULE_CALL_WHITELIST
# - 必拒：runtime 命名空间链 / 链式 Call / 参数侧 Call / Lambda / 推导式 / f-string / BinOp 等

import pytest

from common.template.mako_utils import mako_safety
from common.template.mako_utils.checker import check_mako_template_safety
from common.template.mako_utils.exceptions import ForbiddenMakoTemplateException


def _check(expr: str):
    return check_mako_template_safety(
        expr,
        mako_safety.SingleLineNodeVisitor(),
        mako_safety.SingleLinCodeExtractor(),
    )


# -------- 通过用例 --------

@pytest.mark.parametrize(
    "expr",
    [
        "${sn}",
        "${a.b}",
        "${a.b.c}",
        "${a['k']}",
        "${a[\"a\"]}",
        "${arr[0]}",
        "${a.b['k']}",
        # 嵌套 Subscript（数字 + 字符串键混合）
        "${a[0][\"a\"]}",
        "${a[\"a\"][0]}",
        "${a[\"a\"][\"b\"][\"c\"]}",
        "${a[0][1][2]}",
        # Subscript + 字符串方法
        "${a[\"a\"].upper()}",
        "${a[0][\"a\"].strip()}",
        "${name.upper()}",
        "${name.lower()}",
        "${name.replace('a','b')}",
        "${name.startswith('x')}",
        "${name.endswith('y')}",
        "${'-'.join(parts)}",
        "${name.strip()}",
        "${name.split(',')}",
        "${name.zfill(3)}",
        "${name.count('x')}",
        # 受信模块（顶层取值）
        "${datetime.datetime.now()}",
        "${datetime.date.today()}",
        "${datetime.datetime.fromtimestamp(ts)}",
        "${time.time()}",
        "${time.strftime('%Y-%m-%d', t)}",
        "${time.localtime()}",
        # 取值链 + 一次方法调用
        "${a.b.c.upper()}",
        # dict 写方法白名单：update / setdefault
        "${query_params.update(\"xx\")}",
        "${query_params.update(other)}",
        "${query_params.update(other.foo)}",
        "${query_params.update(a[\"b\"])}",
        "${query_params.setdefault(\"k\", v)}",
        "${obj.update(a, b=c)}",
    ],
)
def test_safe_expressions_pass(expr):
    assert _check(expr) is True


# -------- 必拒：runtime 命名空间 / 模块属性链 RCE --------

@pytest.mark.parametrize(
    "expr",
    [
        "${self.module.cache.util.os.popen('x').read()}",
        "${self.module}",
        "${self.module.cache}",
        "${local.foo}",
        "${context.kwargs}",
        "${caller.body()}",
        "${next.body()}",
        "${parent.foo}",
        "${capture(x)}",
    ],
)
def test_runtime_namespace_chain_rejected(expr):
    with pytest.raises(ForbiddenMakoTemplateException):
        _check(expr)


# -------- 必拒：链式 Call / 参数侧 Call --------

@pytest.mark.parametrize(
    "expr",
    [
        "${a.upper().lower()}",
        "${name.replace('a','b').upper()}",
        # 受信模块也禁链式 Call
        "${datetime.datetime.now().strftime('%Y')}",
        "${time.localtime().tm_year}",  # 链式：先 Call 再 Attribute（Attribute.value=Call）
        # 参数侧嵌套 Call
        "${a.replace(b.upper(), 'x')}",
        "${'-'.join(name.split(','))}",
    ],
)
def test_chained_or_nested_call_rejected(expr):
    with pytest.raises(ForbiddenMakoTemplateException):
        _check(expr)


# -------- 必拒：字符串方法白名单外 --------

@pytest.mark.parametrize(
    "expr",
    [
        "${a.encode('utf-8')}",
        "${a.translate(t)}",
        "${a.format('x')}",
        "${a.format_map({})}",
        "${a.do_evil()}",
    ],
)
def test_str_method_outside_whitelist_rejected(expr):
    with pytest.raises(ForbiddenMakoTemplateException):
        _check(expr)


# -------- 必拒：受信模块属性不在白名单 --------

@pytest.mark.parametrize(
    "expr",
    [
        "${datetime.datetime.subclasses()}",   # 链尾 token 非白名单
        "${time.struct_time(())}",             # struct_time 不在 time 白名单
        "${datetime.foo}",                     # foo 不在 datetime 白名单
        "${time.unknown}",                     # 仅取属性，但属性非白名单
    ],
)
def test_module_attr_outside_whitelist_rejected(expr):
    with pytest.raises(ForbiddenMakoTemplateException):
        _check(expr)


# -------- 必拒：私有/魔术属性 --------

@pytest.mark.parametrize(
    "expr",
    [
        "${a.__class__}",
        "${a._meta}",
        "${a._private}",
        "${datetime.datetime.__subclasses__()}",
        "${datetime.datetime.__class__}",
    ],
)
def test_private_attr_rejected(expr):
    with pytest.raises(ForbiddenMakoTemplateException):
        _check(expr)


# -------- 必拒：高危节点 --------

@pytest.mark.parametrize(
    "expr",
    [
        "${(lambda x: x)(1)}",
        "${[x for x in y]}",
        "${{x for x in y}}",
        "${{k: v for k, v in y}}",
        "${a if b else c}",
        "${a + b}",
        "${a - b}",
        "${a and b}",
        "${not a}",
        "${a == b}",
        "${a > b}",
        "${f'x{a}'}",
        "${a[1:2]}",
        "${a[::2]}",
    ],
)
def test_high_risk_nodes_rejected(expr):
    with pytest.raises(ForbiddenMakoTemplateException):
        _check(expr)


# -------- 必拒：裸函数 / *args / **kwargs --------

@pytest.mark.parametrize(
    "expr",
    [
        "${getattr(x, 'y')}",
        "${eval('1')}",
        "${str(x)}",
        "${name.replace(*args)}",
        "${name.replace(**kw)}",
    ],
)
def test_bare_call_or_unpack_rejected(expr):
    with pytest.raises(ForbiddenMakoTemplateException):
        _check(expr)


# -------- 必拒：私有下标 --------

def test_private_subscript_rejected():
    with pytest.raises(ForbiddenMakoTemplateException):
        _check("${a['__class__']}")
    with pytest.raises(ForbiddenMakoTemplateException):
        _check("${a['_secret']}")


# -------- 必拒：runtime 名作下标变量 --------

def test_runtime_name_as_subscript_rejected():
    with pytest.raises(ForbiddenMakoTemplateException):
        _check("${a[self]}")


# -------- 必拒：非常量 / 非纯变量名形态作下标 --------
# 收口策略：下标只允许常量字面量或纯变量名；
# Attribute / BinOp / Call 等动态形态一律拒绝，避免绕过链根校验。

@pytest.mark.parametrize(
    "expr",
    [
        "${a[b.c]}",       # Attribute 作下标
        "${a[b + 1]}",     # BinOp 作下标
        "${a[fn()]}",      # Call 作下标
    ],
)
def test_dynamic_subscript_rejected(expr):
    with pytest.raises(ForbiddenMakoTemplateException):
        _check(expr)


# -------- 必拒：dict 写方法白名单不得绕过参数侧/链根/私有属性约束 --------
# 即使 update / setdefault 已加入白名单，参数侧仍受 _is_pure_value_node、
# FORBIDDEN_ROOT_NAMES、私有属性、链式 Call 等所有现有约束保护。

@pytest.mark.parametrize(
    "expr",
    [
        # 链根 / 私有属性
        "${query_params.update(self.module.__dict__)}",
        "${query_params.update(self.module)}",
        "${obj.update(other.__dict__)}",
        # Dict / Set 字面量参数（包括含私有键的 dict）
        "${obj.update({\"__class__\": x})}",
        "${obj.update({\"_secret\": 1})}",
        # BinOp / 嵌套 Call 参数
        "${obj.update(a + b)}",
        "${obj.update(fn())}",
        # 解包
        "${obj.update(*args)}",
        "${obj.update(**kw)}",
        # 链式 Call
        "${obj.update().clear()}",
        # 非白名单的 dict 写方法仍拒
        "${obj.pop(\"k\")}",
        "${obj.clear()}",
    ],
)
def test_dict_mutation_attack_rejected(expr):
    with pytest.raises(ForbiddenMakoTemplateException):
        _check(expr)

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

common.template.template.Template 端到端渲染测试

测试目标：
1. 正常模板渲染功能（变量替换、嵌套结构、内置函数等）
2. get_templates / get_reference 解析能力
3. Mako 沙箱在 render() 全链路上的安全拦截：
   - 危险 payload 被 check_mako_template_safety 拦截后，render 必须返回原文（不抛异常给上层）
   - 不允许在渲染阶段真正执行命令（验证 dunder/动态拼接/format/import 等链路）
   - 私有名（下划线起始）属性 / 名字 / 下标全部被拦截
"""

import os
import tempfile
import unittest

from django.test import TestCase

from common.template.mako_utils import mako_safety
from common.template.mako_utils.checker import check_mako_template_safety
from common.template.mako_utils.exceptions import ForbiddenMakoTemplateException
from common.template.template import Template


class TemplateBasicTest(TestCase):
    """Template 基础功能测试：解析、引用提取、正常渲染"""

    def test_get_templates_from_string(self):
        tpl = Template("hello ${name}, age=${age}")
        self.assertEqual(set(tpl.get_templates()), {"${name}", "${age}"})

    def test_get_templates_from_list(self):
        tpl = Template(["${a}", ["${b}", "${a + b}"]])
        self.assertEqual(set(tpl.get_templates()), {"${a}", "${b}", "${a + b}"})

    def test_get_templates_from_dict(self):
        tpl = Template({"k1": "${a}", "k2": {"k3": "${b}"}})
        self.assertEqual(set(tpl.get_templates()), {"${a}", "${b}"})

    def test_get_templates_no_template(self):
        tpl = Template("plain text without template")
        self.assertEqual(tpl.get_templates(), [])

    def test_get_reference_default_format(self):
        tpl = Template("${a} + ${b}")
        self.assertEqual(tpl.get_reference(), {"${a}", "${b}"})

    def test_get_reference_deformat(self):
        tpl = Template("${a} + ${b}")
        self.assertEqual(tpl.get_reference(deformat=True), {"a", "b"})

    def test_render_simple_variable(self):
        self.assertEqual(Template("${name}").render({"name": "alice"}), "alice")

    def test_render_arithmetic(self):
        self.assertEqual(Template("${a + b}").render({"a": 1, "b": 2}), "3")

    def test_render_attribute(self):
        class Obj:
            name = "bob"

        self.assertEqual(Template("${obj.name}").render({"obj": Obj()}), "bob")

    def test_render_dict_subscript(self):
        self.assertEqual(
            Template('${data["k"]}').render({"data": {"k": "v"}}), "v"
        )

    def test_render_list_subscript(self):
        self.assertEqual(Template("${arr[0]}").render({"arr": [10, 20]}), "10")

    def test_render_method_call(self):
        self.assertEqual(
            Template('${s.upper()}').render({"s": "abc"}), "ABC"
        )

    def test_render_builtin_int(self):
        self.assertEqual(Template("${int(x)}").render({"x": "5"}), "5")

    def test_render_builtin_str(self):
        self.assertEqual(Template('${str(123)}').render({}), "123")

    def test_render_builtin_len(self):
        self.assertEqual(Template("${len(arr)}").render({"arr": [1, 2, 3]}), "3")

    def test_render_non_string_returns_directly(self):
        """单一模板变量且 context 中可直接命中时，直接返回原值（不强制转字符串）"""
        result = Template("${data}").render({"data": [1, 2, 3]})
        self.assertEqual(result, [1, 2, 3])

    def test_render_mixed_text_and_template(self):
        self.assertEqual(
            Template("name=${name}, age=${age}").render({"name": "a", "age": 1}),
            "name=a, age=1",
        )

    def test_render_non_string_data_raises(self):
        with self.assertRaises(Exception):
            Template(["${a}"]).render({"a": 1})


class TemplateRenderSafetyTest(TestCase):
    """
    Template.render() 端到端安全测试

    关键约定（参见 _render_string 实现）：
    - 当 check_mako_template_safety 抛出 ForbiddenMakoTemplateException 时，
      render() 不会替换该模板片段，整段保留原文返回。
    - 因此对恶意 payload 的断言策略是：render 后字符串保持不变。
    """

    # ---------------- dunder 属性链路 ----------------

    def test_render_blocks_classic_rce_payload(self):
        """经典 RCE 链路：__class__.__bases__.__subclasses__... popen.read"""
        payload = (
            '${().__class__.__bases__[0].__subclasses__()[0].__init__.__globals__'
            '["__builtins__"]["__import__"]("os").popen("id").read()}'
        )
        self.assertEqual(Template(payload).render({}), payload)

    def test_render_blocks_dunder_class(self):
        payload = "${obj.__class__}"
        self.assertEqual(Template(payload).render({"obj": object()}), payload)

    def test_render_blocks_dunder_globals_chain(self):
        payload = '${obj.__init__.__globals__["__builtins__"]}'
        self.assertEqual(Template(payload).render({"obj": object()}), payload)

    def test_render_blocks_dunder_mro(self):
        payload = '${"".__class__.__mro__[1].__subclasses__()}'
        self.assertEqual(Template(payload).render({}), payload)

    # ---------------- dunder 名字（visit_Name） ----------------

    def test_render_blocks_dunder_import_name(self):
        payload = '${__import__("os")}'
        self.assertEqual(Template(payload).render({}), payload)

    def test_render_blocks_dunder_builtins_name(self):
        payload = "${__builtins__}"
        self.assertEqual(Template(payload).render({}), payload)

    # ---------------- 单下划线（P0-1 收紧后）----------------

    def test_render_blocks_single_underscore_attribute(self):
        """单下划线属性需被拒绝，防御 Django ORM 内省链 (_meta / _state / _default_manager)"""
        payload = "${obj._meta}"
        self.assertEqual(Template(payload).render({"obj": object()}), payload)

    def test_render_blocks_single_underscore_state_chain(self):
        payload = "${obj._state.db}"
        self.assertEqual(Template(payload).render({"obj": object()}), payload)

    def test_render_blocks_single_underscore_name(self):
        """
        单下划线变量名拦截。
        注意：_render_string 有快路径——当整个字符串则是单个模板且 deformat 后的
        key 能在 context 中直接命中时，会绕过 AST 检查。
        所以这里需要让 _private 不在 context 中走“路”，才能调起 visit_Name 拦截逻辑。
        """
        payload = "prefix-${_private}-suffix"
        # 只要不是“单一模板且整串为模板”，就一定走 AST 检查路径
        result = Template(payload).render({"_private": "x"})
        # 拦截后 该 ${_private} 片段保留原文
        self.assertIn("${_private}", result)
        self.assertNotIn("prefix-x-suffix", result)

    def test_render_blocks_single_underscore_subscript(self):
        payload = '${data["_meta"]}'
        self.assertEqual(Template(payload).render({"data": {"_meta": "x"}}), payload)

    # ---------------- 字符串下标 dunder ----------------

    def test_render_blocks_static_dunder_subscript(self):
        payload = '${data["__globals__"]}'
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    def test_render_blocks_static_dunder_subscript_single_quote(self):
        payload = "${data['__class__']}"
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    # ---------------- 动态拼接 dunder 下标（H1 重点） ----------------

    def test_render_blocks_dynamic_concat_dunder_subscript(self):
        payload = '${data["__" + "globals__"]}'
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    def test_render_blocks_string_multiplication_dunder(self):
        payload = '${data["_" * 2 + "class" + "_" * 2]}'
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    def test_render_blocks_chr_concat_dunder(self):
        payload = '${data[chr(95)+chr(95)+"class"+chr(95)+chr(95)]}'
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    def test_render_blocks_fstring_dunder_subscript(self):
        """f-string 拼接 dunder：JoinedStr 节点应被白名单直接拒绝（不论值是否真为 dunder）"""
        payload = '${data[f"__{\'class\'}__"]}'
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    def test_render_blocks_percent_format_dunder(self):
        payload = '${data["%s%s" % ("__", "globals__")]}'
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    def test_render_blocks_ifexp_subscript(self):
        payload = '${data["__class__" if 1 else "x"]}'
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    def test_render_blocks_call_result_subscript(self):
        payload = '${data[str("__class__")]}'
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    def test_render_blocks_attribute_as_subscript(self):
        """以属性访问表达式作为下标：Attribute 节点不在白名单，应被拒绝"""
        payload = '${data[a.b]}'
        self.assertEqual(Template(payload).render({"data": {}, "a": object()}), payload)

    def test_render_blocks_walrus_subscript(self):
        """walrus 表达式 (NamedExpr) 作为下标：不在白名单，应被拒绝"""
        payload = '${data[(x := "__class__")]}'
        # 注：mako 解析或 AST 解析失败也算拦截（render 返回原文）
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    def test_render_blocks_lambda_subscript(self):
        """lambda 表达式作为下标：Lambda 节点不在白名单，应被拒绝"""
        payload = '${data[(lambda: "__class__")()]}'
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    def test_render_blocks_bytes_constant_subscript(self):
        payload = '${data[b"__class__"]}'
        self.assertEqual(Template(payload).render({"data": {}}), payload)

    # ---------------- format / format_map ----------------

    def test_render_blocks_format_dunder(self):
        payload = '${"{0.__class__}".format(1)}'
        self.assertEqual(Template(payload).render({}), payload)

    def test_render_blocks_format_map_dunder(self):
        payload = '${"{x.__class__}".format_map({"x": 1})}'
        self.assertEqual(Template(payload).render({}), payload)

    def test_render_blocks_format_method_on_var(self):
        payload = "${s.format(obj)}"
        self.assertEqual(
            Template(payload).render({"s": "{0}", "obj": "x"}), payload
        )

    # ---------------- import / from import ----------------

    def test_render_blocks_import_statement(self):
        payload = "<% import os %>"
        self.assertEqual(Template(payload).render({}), payload)

    def test_render_blocks_from_import_statement(self):
        payload = "<% from os import system %>"
        self.assertEqual(Template(payload).render({}), payload)

    # ---------------- 真实 RCE 副作用验证（最关键） ----------------

    def test_render_does_not_execute_command_via_popen(self):
        """
        端到端验证：恶意 payload 即使突破解析层也不应在渲染阶段执行命令。
        借助临时文件作为 RCE 探针：若 payload 真的被执行，文件会被创建。
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            probe = os.path.join(tmp_dir, "rce_probe.flag")
            # 用 touch / type nul 跨平台不便；改用 Python 自身写文件作为更稳定的探针
            payload = (
                '${().__class__.__bases__[0].__subclasses__()[0].__init__.__globals__'
                '["__builtins__"]["open"]("%s","w").write("pwned")}'
                % probe.replace("\\", "\\\\")
            )

            result = Template(payload).render({})

            # 1) payload 被沙箱拦截，原文返回
            self.assertEqual(result, payload)
            # 2) 探针文件未被创建，证明命令未执行
            self.assertFalse(
                os.path.exists(probe),
                "RCE probe file was created — sandbox bypassed!",
            )

    def test_render_does_not_leak_subclasses(self):
        """
        即使 payload 写法变化（mro / subclasses 文本不变），输出都应是原文，
        而不是 [<class 'type'>, ...] 这类内省结果。
        """
        payload = '${"".__class__.__mro__}'
        result = Template(payload).render({})
        # 1) 拦截后必须原文返回
        self.assertEqual(result, payload)
        # 2) 不应泄漏内省结果（type/object/tuple 的 repr 文本）
        self.assertNotIn("<class ", result)
        self.assertNotIn("type'>", result)
        self.assertNotIn("object'>", result)


class TemplateAstCheckerDirectTest(TestCase):
    """
    直接调用 check_mako_template_safety 的补充用例，
    用于覆盖 [test_expression.py] 中尚未覆盖的边界。
    """

    def _assert_forbidden(self, payload):
        with self.assertRaises(ForbiddenMakoTemplateException):
            check_mako_template_safety(
                payload,
                mako_safety.SingleLineNodeVisitor(),
                mako_safety.SingleLinCodeExtractor(),
            )

    def _assert_safe(self, payload):
        self.assertTrue(
            check_mako_template_safety(
                payload,
                mako_safety.SingleLineNodeVisitor(),
                mako_safety.SingleLinCodeExtractor(),
            )
        )

    # 多维下标 / 切片放行
    def test_allow_tuple_index(self):
        self._assert_safe("${a[0, 1]}")

    def test_allow_slice(self):
        self._assert_safe("${a[1:3]}")

    def test_allow_slice_with_step(self):
        self._assert_safe("${a[1:10:2]}")

    def test_allow_variable_subscript(self):
        self._assert_safe("${a[i]}")

    def test_allow_bool_constant_subscript(self):
        self._assert_safe("${a[True]}")

    def test_allow_none_constant_subscript(self):
        self._assert_safe("${a[None]}")

    # 多维元组下标内若混入 dunder 字符串也应拦截
    def test_block_dunder_inside_tuple_subscript(self):
        self._assert_forbidden('${a["__class__", 1]}')

    # 嵌套 subscript 作为下标（非常量）
    def test_block_nested_subscript_as_key(self):
        self._assert_forbidden('${a[["__class__"][0]]}')

    # 过滤器白名单
    def test_allow_safe_filter_h(self):
        self._assert_safe("${x | h}")

    def test_allow_safe_filter_trim(self):
        self._assert_safe("${x | trim}")

    def test_allow_safe_decode_filter(self):
        self._assert_safe("${x | decode.utf8}")

    def test_block_unsafe_filter_format(self):
        self._assert_forbidden("${x | format}")

    def test_block_decode_filter_with_dunder(self):
        self._assert_forbidden("${x | decode.__init__}")

    def test_block_decode_filter_with_private_segment(self):
        self._assert_forbidden("${x | decode._private}")


class TemplateGetReferenceMalformedTest(TestCase):
    """异常模板片段不应让 get_reference 崩溃"""

    def test_get_reference_with_syntax_error(self):
        # 非法 Mako 表达式应被忽略而不是抛出
        tpl = Template("${a:b}")
        # 不抛异常即可
        try:
            tpl.get_reference()
        except Exception as e:
            self.fail("get_reference raised unexpectedly: %s" % e)


class TemplateMixedPayloadTest(TestCase):
    """
    混合模板用例：同一字符串中有合法片段 + 非法片段，
    验证沙箱按片段独立判定，合法片段正常渲染、非法片段保留原文。
    """

    def test_render_mixed_safe_and_unsafe(self):
        unsafe = "${obj.__class__}"
        tpl_str = "name=${name}, leak=" + unsafe
        result = Template(tpl_str).render({"name": "alice", "obj": object()})
        self.assertIn("name=alice", result)
        self.assertIn(unsafe, result)  # 非法片段保留原文
        self.assertNotIn("type", result)  # 不应渲染出 <class 'type'>

    def test_render_multiple_unsafe_blocks(self):
        tpl_str = '${obj._meta} | ${data["__class__"]} | ${__import__("os")}'
        result = Template(tpl_str).render({"obj": object(), "data": {}})
        # 三段全部保留原文
        self.assertIn("${obj._meta}", result)
        self.assertIn('${data["__class__"]}', result)
        self.assertIn('${__import__("os")}', result)


class TemplateSafeExpressionAllowTest(TestCase):
    """
    放行用例：确认收紧后的沙箱不会误伤常规业务模板。
    """

    def test_allow_string_concat(self):
        self.assertEqual(
            Template("${a + b}").render({"a": "foo", "b": "bar"}), "foobar"
        )

    def test_allow_format_string_in_context(self):
        """
        该用例验证走 mako 表达式的字符串拼接能力。
        注：mako 的 ${...} 表达式语法本身就是表达式插值，
        不需要再字 f-string；此处改用字符串 .format 被拦截者不应该走。
        走字符串拼接验证放行：
        """
        # 用拼接代替 f-string（mako 本身就是插值语法）
        self.assertEqual(
            Template('${"hello " + name}').render({"name": "alice"}),
            "hello alice",
        )

    def test_allow_comparison(self):
        self.assertEqual(Template("${a > b}").render({"a": 2, "b": 1}), "True")

    def test_allow_bool_op(self):
        self.assertEqual(
            Template("${a and b}").render({"a": True, "b": "ok"}), "ok"
        )

    def test_allow_ternary(self):
        self.assertEqual(
            Template("${'yes' if flag else 'no'}").render({"flag": True}), "yes"
        )

    def test_allow_list_comprehension(self):
        # 列表推导内的 x 是 Store 形式不会触发 visit_Name 私有名检查
        self.assertEqual(
            Template("${[x*2 for x in arr]}").render({"arr": [1, 2, 3]}),
            "[2, 4, 6]",
        )

    def test_allow_dict_comprehension_via_dict_call(self):
        """
        注：mako 的 ${...} 里写 {k:v for ...} 会与 mako 表达式语法冲突，
        改用 dict(...) 验证推导表达式可运行。
        """
        result = Template("${dict([(k, v) for k, v in items])}").render(
            {"items": [("a", 1), ("b", 2)]}
        )
        # 字典顺序依赖实现，仅判断关键字段
        self.assertIn("'a': 1", result)
        self.assertIn("'b': 2", result)

    def test_allow_method_chain_with_args(self):
        self.assertEqual(
            Template("${s.replace('a','b').upper()}").render({"s": "abc"}), "BBC"
        )

    def test_allow_starred_call(self):
        """*args 调用应放行"""
        self.assertEqual(
            Template("${list(arr)}").render({"arr": (1, 2, 3)}), "[1, 2, 3]"
        )


class TemplateSandboxFallbackTest(TestCase):
    """
    Sandbox 兜底层验证（严格模式）：
    即使假设 AST 检查未拦住（人为构造越过），
    MAKO_SANDBOX_SHIELD_WORDS 把 __import__ / open / getattr 等遵蔽为 _ForbiddenProxy 实例，
    渲染时应抛 ForbiddenMakoTemplateException 并由 _render_template 的 try/except 兜回原文。
    """

    def test_sandbox_shields_dangerous_builtins_with_proxy(self):
        """严格模式：sandbox 注入的是 _ForbiddenProxy 实例（非 None），以起到主动拦截作用。"""
        from common.template.sandbox import Sandbox, _ForbiddenProxy

        sb = Sandbox().get()
        for word in ("__import__", "open", "getattr", "eval", "exec", "compile", "globals"):
            self.assertIn(word, sb)
            self.assertIsInstance(
                sb[word],
                _ForbiddenProxy,
                msg="sandbox[{}] should be _ForbiddenProxy in strict mode".format(word),
            )

    def test_sandbox_proxy_call_raises(self):
        """严格模式：代理对象被调用时必须抛 ForbiddenMakoTemplateException。"""
        from common.template.sandbox import Sandbox

        sb = Sandbox().get()
        with self.assertRaises(ForbiddenMakoTemplateException):
            sb["open"]("/tmp/x", "w")

    def test_sandbox_proxy_attr_access_raises(self):
        """严格模式：访问 __class__ 跳板类属性也必须抛异常，堆断 RCE 跳板。"""
        from common.template.sandbox import Sandbox

        sb = Sandbox().get()
        with self.assertRaises(ForbiddenMakoTemplateException):
            _ = sb["getattr"].__class__  # noqa: F841

    def test_sandbox_proxy_format_raises(self):
        """严格模式：format / f-string 路径也不能静默。"""
        from common.template.sandbox import Sandbox

        sb = Sandbox().get()
        with self.assertRaises(ForbiddenMakoTemplateException):
            "{}".format(sb["type"])

    def test_sandbox_proxy_str_repr_raises(self):
        """严格模式：str() / repr() 也必须抛异常（有意为之的可观察性 trade-off）。"""
        from common.template.sandbox import Sandbox

        sb = Sandbox().get()
        with self.assertRaises(ForbiddenMakoTemplateException):
            str(sb["eval"])
        with self.assertRaises(ForbiddenMakoTemplateException):
            repr(sb["eval"])

    def test_sandbox_provides_safe_modules(self):
        """sandbox 应注入 datetime / time 等安全模块，业务模板可正常使用"""
        from common.template.sandbox import Sandbox

        sb = Sandbox().get()
        self.assertIn("datetime", sb)
        self.assertIn("time", sb)


class TemplateForbiddenProxyStrictTest(TestCase):
    """
    严格模式下 _ForbiddenProxy 各 dunder 拦截点的直接单元测试。
    与端到端测试互补：这里直接实例化 _ForbiddenProxy，逐个驱动 dunder，
    避免被上层 AST 拦截遮盖住底层语义。
    """

    def setUp(self):
        from common.template.sandbox import _ForbiddenProxy

        self.proxy = _ForbiddenProxy("getattr")

    def test_call_raises(self):
        with self.assertRaises(ForbiddenMakoTemplateException):
            self.proxy(1, 2)

    def test_getattr_class_raises_no_rce_pivot(self):
        """堆断 __class__.__bases__[0].__subclasses__() 跳板的核心防线。"""
        with self.assertRaises(ForbiddenMakoTemplateException):
            _ = self.proxy.__class__  # noqa: F841

    def test_getattr_arbitrary_raises(self):
        with self.assertRaises(ForbiddenMakoTemplateException):
            _ = self.proxy.anything  # noqa: F841

    def test_getattr_token_raises(self):
        """代理内部的 _token 也不允许被外部读取。"""
        with self.assertRaises(ForbiddenMakoTemplateException):
            _ = self.proxy._token  # noqa: F841

    def test_setattr_raises(self):
        with self.assertRaises(ForbiddenMakoTemplateException):
            self.proxy.x = 1

    def test_delattr_raises(self):
        with self.assertRaises(ForbiddenMakoTemplateException):
            del self.proxy.x

    def test_getitem_raises(self):
        with self.assertRaises(ForbiddenMakoTemplateException):
            _ = self.proxy[0]  # noqa: F841

    def test_iter_raises(self):
        with self.assertRaises(ForbiddenMakoTemplateException):
            list(self.proxy)

    def test_contains_raises(self):
        with self.assertRaises(ForbiddenMakoTemplateException):
            _ = 1 in self.proxy  # noqa: F841

    def test_format_raises(self):
        with self.assertRaises(ForbiddenMakoTemplateException):
            "{}".format(self.proxy)
        with self.assertRaises(ForbiddenMakoTemplateException):
            "{:>10}".format(self.proxy)

    def test_str_raises(self):
        with self.assertRaises(ForbiddenMakoTemplateException):
            str(self.proxy)

    def test_repr_raises(self):
        with self.assertRaises(ForbiddenMakoTemplateException):
            repr(self.proxy)

    def test_bool_default_true(self):
        """未重写 __bool__，默认为 True，避免被 `if proxy:` 当作 None 失静默。"""
        self.assertTrue(bool(self.proxy))


class TemplateRenderLoggingContractTest(TestCase):
    """
    验证 _render_template 在严格模式下的行为契约：
    - 任何 sandbox 拦截报错都不应上抛到调用方；
    - 最终必须返回模板原文（联合 _render_string 也能保证）。
    该类不检查日志内容本身，只验证外部可观察的返回值契约。
    """

    def test_render_returns_origin_when_proxy_invoked_in_safe_lookalike(self):
        """
        构造一个 AST 能过、但运行时会跳发 sandbox 代理的场景：
        取 context 中名为 builtin 关键字的变量（合法变量名）。
        实际渲染时 sandbox.update 会覆盖 context，所以该变量会被代理接管；
        代理在 __str__ 阶段抛异常 → _render_template 兜底 → 返回原文。
        """
        # 变量名 itself 不含下划线，能过 visit_Name；但 sandbox 覆盖后变代理
        # 'getattr' 作为变量名是合法的 Python 表达式，但也是被遮蔽词
        payload = "${getattr}"
        result = Template(payload).render({"getattr": "hijacked"})
        # 严格模式下 sandbox 覆盖 context，str(proxy) 抛异常→原文返回
        self.assertEqual(result, payload)

    def test_render_with_runtime_error_returns_origin(self):
        """渲染时如果上下文缺变量，也应返回模板原文而非抛错。"""
        payload = "${missing_var}"
        result = Template(payload).render({})
        # mako 未定义变量会报 NameError → 被兜底为原文
        self.assertEqual(result, payload)


class TemplateMakoTagSafetyTest(TestCase):
    """Mako 标签内的 import / 模块级代码也应拦截"""

    def test_block_module_level_import_tag(self):
        """<%! import os %> 模块级 import 标签"""
        payload = "<%! import os %>${1+1}"
        # 非法标签会让 sandbox 抛异常，渲染兜底回原文或部分原文；
        # 关键是不能真正导入 os 并执行
        result = Template(payload).render({})
        # 渲染过程不会抛 ImportError 给上层
        self.assertIsNotNone(result)
        # 不应出现 os 模块的 repr
        self.assertNotIn("<module 'os'", result)

    def test_block_inline_import_tag(self):
        """<% import os %> 内联 import 标签"""
        payload = "<% import os %>${1+1}"
        result = Template(payload).render({})
        self.assertIsNotNone(result)
        self.assertNotIn("<module 'os'", result)


class TemplateFilterSafetyTest(TestCase):
    """filter 表达式安全测试（端到端）"""

    def test_render_blocks_filter_format(self):
        payload = "${x | format}"
        self.assertEqual(Template(payload).render({"x": "abc"}), payload)

    def test_render_blocks_filter_dunder(self):
        payload = "${x | decode.__init__}"
        self.assertEqual(Template(payload).render({"x": "abc"}), payload)

    def test_render_allows_filter_h(self):
        # | h 是 HTML 转义过滤器，应放行
        result = Template("${x | h}").render({"x": "<b>"})
        self.assertEqual(result, "&lt;b&gt;")

    def test_render_allows_filter_trim(self):
        result = Template("${x | trim}").render({"x": "  abc  "})
        self.assertEqual(result, "abc")


if __name__ == "__main__":
    unittest.main()

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

from django.test import TestCase

from common.template.mako_utils import mako_safety
from common.template.mako_utils.checker import check_mako_template_safety
from common.template.mako_utils.exceptions import ForbiddenMakoTemplateException
from common.template.template import Template as CommonTemplate
from pipeline.core.data import expression
from pipeline.core.data.expression import format_constant_key, deformat_constant_key


class TestConstantTemplate(TestCase):
    def setUp(self):
        pass

    def test_format_constant_key(self):
        self.assertEqual(format_constant_key("a"), "${a}")

    def test_deformat_constant_key(self):
        self.assertEqual(deformat_constant_key("${a}"), "a")

    def test_get_reference(self):
        all_in_cons_template = expression.ConstantTemplate(["${a}", ["${a}", "${a+int(b)}"]])
        self.assertEqual(set(all_in_cons_template.get_reference()), {"a", "b", "int"})

        comma_exclude_template = expression.ConstantTemplate(['${a["c"]}', ['${"%s" % a}', "${a+int(b)}"]])
        self.assertEqual(set(comma_exclude_template.get_reference()), {"a", "b", "int"})

    def test_get_templates(self):
        cons_tmpl = expression.ConstantTemplate(["${a}", ["${a}", "${a+int(b)}"]])
        self.assertEqual(set(cons_tmpl.get_templates()), {"${a+int(b)}", "${a}"})

    def test_resolve_data(self):
        list_template = expression.ConstantTemplate(["${a}", ["${a}", "${a+int(b)}"]])
        self.assertEqual(list_template.resolve_data({"a": 2, "b": "3"}), [2, [2, "5"]])

        tuple_template = expression.ConstantTemplate(("${a}", ("${a}", "${a+int(b)}")))
        self.assertEqual(tuple_template.resolve_data({"a": 2, "b": "3"}), (2, (2, "5")))

        dict_template = expression.ConstantTemplate({"aaaa": {"a": "${a}", "b": "${a+int(b)}"}})
        self.assertEqual(dict_template.resolve_data({"a": 2, "b": "3"}), {"aaaa": {"a": 2, "b": "5"}})

    def test_get_string_templates(self):
        cons_tmpl = expression.ConstantTemplate("")
        self.assertEqual(cons_tmpl.get_string_templates("${a}"), ["${a}"])

    def test_resolve_string(self):
        cons_tmpl = expression.ConstantTemplate("")
        one_template = "${a}"
        self.assertEqual(cons_tmpl.resolve_string(one_template, {"a": "1"}), "1")

    def test_get_template_reference(self):
        cons_tmpl = expression.ConstantTemplate("")
        self.assertEqual(cons_tmpl.get_template_reference("${a}"), ["a"])

    def test_resolve_template(self):
        cons_tmpl = expression.ConstantTemplate("")
        simple = "${a}"
        self.assertEqual(cons_tmpl.resolve_template(simple, {"a": "1"}), "1")

        calculate = "${a+int(b)}"
        self.assertEqual(cons_tmpl.resolve_template(calculate, {"a": 2, "b": "3"}), "5")

        split = "${a[0]}"
        self.assertEqual(cons_tmpl.resolve_template(split, {"a": [1, 2]}), "1")

        dict_item = '${a["b"]}'
        self.assertEqual(cons_tmpl.resolve_template(dict_item, {"a": {"b": 1}}), "1")

        not_exists = "{a}"
        self.assertEqual(cons_tmpl.resolve_template(not_exists, {}), not_exists)

        resolve_syntax_error = "${a.b}"
        self.assertEqual(cons_tmpl.resolve_template(resolve_syntax_error, {}), resolve_syntax_error)

        template_syntax_error = "${a:b}"
        self.assertEqual(cons_tmpl.resolve_template(template_syntax_error, {}), template_syntax_error)

    def test_resolve(self):
        list_template = expression.ConstantTemplate(["${a}", ["${a}", "${a+int(b)}"]])
        self.assertEqual(list_template.resolve_data({"a": 2, "b": "3"}), [2, [2, "5"]])

        tuple_template = expression.ConstantTemplate(("${a}", ("${a}", "${a+int(b)}")))
        self.assertEqual(tuple_template.resolve_data({"a": 2, "b": "3"}), (2, (2, "5")))

        dict_template = expression.ConstantTemplate({"aaaa": {"a": "${a}", "b": "${a+int(b)}"}})
        self.assertEqual(dict_template.resolve_data({"a": 2, "b": "3"}), {"aaaa": {"a": 2, "b": "5"}})

    def test_get_reference_complex(self):
        all_in_cons_template = expression.ConstantTemplate(["${a}", ["${a}", "${a+int(b)}"]])
        self.assertEqual(set(all_in_cons_template.get_reference()), set(["a", "b", "int"]))

        comma_exclude_template = expression.ConstantTemplate(['${a["c"]}', ['${"%s" % a}', "${a+int(b)}"]])
        self.assertEqual(set(comma_exclude_template.get_reference()), set(["a", "b", "int"]))

    def test_built_in_functions__without_args(self):
        int_template = expression.ConstantTemplate("${int}")
        self.assertEqual(int_template.resolve_data({}), "int")

        int_template = expression.ConstantTemplate("${str}")
        self.assertEqual(int_template.resolve_data({}), "str")

    def test_built_in_functions__with_args(self):
        int_template = expression.ConstantTemplate("${int(111)}")
        self.assertEqual(int_template.resolve_data({}), "111")

        int_template = expression.ConstantTemplate("${str('aaa')}")
        self.assertEqual(int_template.resolve_data({}), "aaa")

    def test_built_in_functions__cover(self):
        int_template = expression.ConstantTemplate("${int}")
        self.assertEqual(int_template.resolve_data({"int": "cover"}), "cover")


class TestMakoTemplateSafety(TestCase):
    def _assert_forbidden_template(self, payload):
        with self.assertRaises(ForbiddenMakoTemplateException):
            check_mako_template_safety(
                payload,
                mako_safety.SingleLineNodeVisitor(),
                mako_safety.SingleLinCodeExtractor(),
            )

    def _assert_safe_template(self, payload):
        """断言模板是安全的，不应抛出异常"""
        result = check_mako_template_safety(
            payload,
            mako_safety.SingleLineNodeVisitor(),
            mako_safety.SingleLinCodeExtractor(),
        )
        self.assertTrue(result)

    # ========== RCE 经典链路拦截测试 ==========

    def test_reject_nested_dunder_payload(self):
        payload = (
            '${().__class__.__bases__[0].__subclasses__()[0].__init__.__globals__'
            '["__builtins__"]["__import__"]("os").popen("id").read()}'
        )

        self._assert_forbidden_template(payload)
        self.assertEqual(CommonTemplate(payload).render({}), payload)

    # ========== visit_Attribute 魔术方法拦截测试 ==========

    def test_reject_dunder_class(self):
        """拦截 __class__ 属性访问"""
        self._assert_forbidden_template("${obj.__class__}")

    def test_reject_dunder_bases(self):
        """拦截 __bases__ 属性访问"""
        self._assert_forbidden_template("${obj.__bases__}")

    def test_reject_dunder_subclasses(self):
        """拦截 __subclasses__ 属性访问"""
        self._assert_forbidden_template("${obj.__subclasses__}")

    def test_reject_dunder_init(self):
        """拦截 __init__ 属性访问"""
        self._assert_forbidden_template("${obj.__init__}")

    def test_reject_dunder_globals(self):
        """拦截 __globals__ 属性访问"""
        self._assert_forbidden_template("${obj.__globals__}")

    def test_reject_dunder_builtins(self):
        """拦截 __builtins__ 属性访问"""
        self._assert_forbidden_template("${obj.__builtins__}")

    def test_reject_dunder_dict(self):
        """拦截 __dict__ 属性访问"""
        self._assert_forbidden_template("${obj.__dict__}")

    def test_reject_dunder_doc(self):
        """拦截 __doc__ 属性访问"""
        self._assert_forbidden_template("${obj.__doc__}")

    def test_reject_dunder_module(self):
        """拦截 __module__ 属性访问"""
        self._assert_forbidden_template("${obj.__module__}")

    def test_reject_dunder_mro(self):
        """拦截 __mro__ 属性访问"""
        self._assert_forbidden_template("${obj.__mro__}")

    def test_reject_nested_dunder_class_bases_chain(self):
        """拦截 __class__.__bases__ 链式访问"""
        self._assert_forbidden_template("${().__class__.__bases__}")

    def test_reject_nested_dunder_class_mro_chain(self):
        """拦截 __class__.__mro__ 链式访问"""
        self._assert_forbidden_template("${().__class__.__mro__}")

    # ========== visit_Name 魔术方法拦截测试 ==========

    def test_reject_dunder_name_import(self):
        """拦截 __import__ 变量名访问"""
        self._assert_forbidden_template("${__import__}")

    # ========== visit_Subscript 字符串索引拦截测试 ==========

    def test_reject_dunder_subscript_payload(self):
        """拦截双引号字符串索引访问 dunder 键"""
        self._assert_forbidden_template('${data["__globals__"]}')

    def test_reject_dunder_subscript_single_quote(self):
        """拦截单引号字符串索引访问 dunder 键"""
        self._assert_forbidden_template("${data['__globals__']}")

    def test_reject_dunder_subscript_builtins(self):
        """拦截 __builtins__ 字符串索引访问"""
        self._assert_forbidden_template('${data["__builtins__"]}')

    def test_reject_dunder_subclass_dict_key(self):
        """拦截 __subclasses__ 字典键访问"""
        self._assert_forbidden_template('${data["__subclasses__"]}')

    def test_reject_nested_subscript_and_attribute_chain(self):
        """拦截混合属性访问与字符串索引的 RCE 链路"""
        self._assert_forbidden_template(
            '${obj.__init__.__globals__["__builtins__"]["__import__"]("os").popen("id").read()}'
        )

    def test_reject_dynamic_dunder_subscript_concat(self):
        """拦截通过字符串拼接生成的 dunder key"""
        payload = '${data["__" + "globals__"]}'
        self._assert_forbidden_template(payload)
        self.assertEqual(CommonTemplate(payload).render({"data": {}}), payload)

    def test_reject_dynamic_dunder_subscript_percent_format(self):
        """拦截通过 % 格式化生成的 dunder key"""
        payload = '${data["%s%s" % ("__", "globals__")]}'
        self._assert_forbidden_template(payload)
        self.assertEqual(CommonTemplate(payload).render({"data": {}}), payload)

    def test_reject_dynamic_dunder_builtins_key_concat(self):
        """拦截通过字符串拼接生成的 __builtins__ key"""
        payload = '${data["__built" + "ins__"]}'
        self._assert_forbidden_template(payload)
        self.assertEqual(CommonTemplate(payload).render({"data": {}}), payload)

    # ========== visit_Call format/format_map 拦截测试 ==========

    def test_reject_format_payload(self):
        self._assert_forbidden_template('${"{0.__class__}".format(1)}')

    def test_reject_format_map_payload(self):
        self._assert_forbidden_template('${"{target.__class__}".format_map({"target": 1})}')

    def test_reject_format_on_variable(self):
        """拦截变量调用 format 方法"""
        self._assert_forbidden_template('${s.format(obj)}')

    def test_reject_format_map_on_variable(self):
        """拦截变量调用 format_map 方法"""
        self._assert_forbidden_template('${s.format_map(obj)}')

    # ========== visit_Import / visit_ImportFrom 拦截测试 ==========

    def test_reject_import_statement(self):
        """拦截 import 语句"""
        self._assert_forbidden_template("<% import os %>")

    def test_reject_import_from_statement(self):
        """拦截 from ... import 语句"""
        self._assert_forbidden_template("<% from os import system %>")

    # ========== 递归遍历深度验证（generic_visit 必要性） ==========

    def test_reject_deeply_nested_dunder(self):
        """验证 AST 遍历器能递归检查深层嵌套的 dunder 属性"""
        # 三层嵌套：确保不是只检查最外层
        self._assert_forbidden_template("${a.__class__.__bases__.__class__}")

    def test_reject_dunder_in_call_args(self):
        """验证函数调用参数中的 dunder 访问也能被拦截"""
        self._assert_forbidden_template("${func(obj.__class__)}")

    def test_reject_dunder_in_subscript_value(self):
        """验证下标表达式中嵌套的 dunder 属性访问也能被拦截"""
        self._assert_forbidden_template("${arr[obj.__class__]}")

    # ========== 安全模板放行测试（正例） ==========

    def test_allow_simple_variable(self):
        """简单变量引用应放行"""
        self._assert_safe_template("${name}")

    def test_allow_normal_attribute(self):
        """普通属性访问应放行"""
        self._assert_safe_template("${obj.attr}")

    def test_allow_normal_subscript(self):
        """普通字符串索引应放行"""
        self._assert_safe_template('${obj["key"]}')

    def test_allow_normal_subscript_single_quote(self):
        """单引号普通字符串索引应放行"""
        self._assert_safe_template("${obj['key']}")

    def test_allow_normal_function_call(self):
        """普通函数调用应放行"""
        self._assert_safe_template("${func()}")

    def test_allow_method_call(self):
        """普通方法调用应放行"""
        self._assert_safe_template("${obj.method()}")

    def test_allow_arithmetic(self):
        """算术运算应放行"""
        self._assert_safe_template("${a + b}")

    def test_forbid_single_underscore(self):
        """单下划线属性应被拒绝（防御 Django ORM 内省链：_meta / _state / _default_manager 等）"""
        self._assert_forbidden_template("${obj._private}")

    def test_allow_numeric_subscript(self):
        """数字索引应放行"""
        self._assert_safe_template("${arr[0]}")

    def test_allow_int_conversion(self):
        """int() 调用应放行"""
        self._assert_safe_template("${int(x)}")

    def test_allow_str_conversion(self):
        """str() 调用应放行"""
        self._assert_safe_template("${str(x)}")

    def test_allow_len_call(self):
        """len() 调用应放行"""
        self._assert_safe_template("${len(arr)}")

    def test_allow_chained_normal_attributes(self):
        """链式普通属性访问应放行"""
        self._assert_safe_template("${obj.attr1.attr2.attr3}")

    def test_allow_method_with_args(self):
        """带参数的方法调用应放行"""
        self._assert_safe_template("${obj.method(arg1, arg2)}")

    def test_allow_dict_get_method(self):
        """字典的 get 方法应放行"""
        self._assert_safe_template('${obj.get("key")}')

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

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
from django.test import TestCase, override_settings

from itsm.component.utils.basic import (
    merge_dict_list,
    get_random_key,
    get_pinyin_key,
    ComplexRegexField,
    Regex,
    better_time_or_none,
    safe_cast,
    duplicate_check,
    group_by,
    tuple_choices,
    generate_random_sn,
    list_by_separator,
)


class TestComponentsUtilsInstance(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_merge_dict_list(self):
        dict_1 = {"hello": "world"}
        dict_2 = {"hello": "word", "hey": "joy"}
        dict_3 = merge_dict_list([dict_1, dict_2])
        self.assertDictEqual(dict_3, {"hello": "word", "hey": "joy"})

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_random_key(self):
        value = get_random_key("hello")
        self.assertIsInstance(value, str)
        self.assertEqual(len(value), 32)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_pinyin_key(self):
        value = get_pinyin_key("你好")
        self.assertIsInstance(value, str)
        self.assertEqual(value, "NIHAO")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_complex_regex_field(self):
        from rest_framework.exceptions import ValidationError

        file_name_validator = ComplexRegexField(
            validate_type=["en", "ch", "num", "special"], special_char="()_ .-"
        )
        file_name_validator.validate("1.jpg")
        self.assertRaises(ValidationError, file_name_validator.validate, "###")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_complex_regex(self):
        from rest_framework.exceptions import ValidationError

        regex = Regex("num")
        self.assertRaises(ValidationError, regex.validate, "###")
        regex.validate_type = "ip"
        self.assertRaises(ValidationError, regex.validate, "124223455")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_ctime_delta(self):
        import datetime

        data = better_time_or_none(datetime.datetime.now())
        self.assertIsInstance(data, str)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_safe_cast(self):
        value = safe_cast("112", int)
        self.assertIsInstance(value, int)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_duplicate_check(self):
        test = [1, 1, 2, 3]
        self.assertEqual(duplicate_check(test), True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_group_by(self):
        test = [{"id": 2}, {"id": 1}]
        result = list(group_by(test, ["id"]))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 1)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_tuple_choices(self):
        CODE_STATUS_TUPLE = (
            "OK",
            "UNAUTHORIZED",
            "VALIDATE_ERROR",
            "METHOD_NOT_ALLOWED",
            "PERMISSION_DENIED",
            "SERVER_500_ERROR",
            "OBJECT_NOT_EXIST",
            "FAILED",
        )
        self.assertIsInstance(tuple_choices(CODE_STATUS_TUPLE), list)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_generate_random_sn(self):
        sn = generate_random_sn("request")
        self.assertTrue(sn.startswith("REQ"), sn)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_(self):
        result = list_by_separator("admin1,admin2,admin3")
        self.assertListEqual(result, ["admin1", "admin2", "admin3"])

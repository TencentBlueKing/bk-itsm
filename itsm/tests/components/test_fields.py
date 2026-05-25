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

import os
import pickle
import zlib

from django.test import TestCase

from itsm.component.fields import (
    IOField,
    JSON_MAGIC,
    _restricted_pickle_loads,
)


class TestIOFieldSerialization(TestCase):
    """测试 IOField 的安全序列化/反序列化功能"""

    def setUp(self):
        self.field = IOField()

    # ==================== 新格式（JSON）写入/读取测试 ====================

    def test_get_prep_value_uses_json_format(self):
        """验证 get_prep_value 使用 JSON 格式序列化并带有 JSON_MAGIC 前缀"""
        value = {"key": "value", "number": 42}
        result = self.field.get_prep_value(value)

        # 解压后应以 JSON_MAGIC 开头
        decompressed = zlib.decompress(result)
        self.assertTrue(decompressed.startswith(JSON_MAGIC))

    def test_roundtrip_dict(self):
        """验证字典数据的序列化/反序列化往返一致性"""
        value = {"key1": "value1", "key2": [1, 2, 3], "key3": {"nested": True}}
        serialized = self.field.get_prep_value(value)
        deserialized = self.field.to_python(serialized)
        self.assertEqual(deserialized, value)

    def test_roundtrip_list(self):
        """验证列表数据的往返一致性"""
        value = [1, "two", 3.0, None, True, False]
        serialized = self.field.get_prep_value(value)
        deserialized = self.field.to_python(serialized)
        self.assertEqual(deserialized, value)

    def test_roundtrip_string(self):
        """验证字符串数据的往返一致性"""
        value = "hello world 你好世界"
        serialized = self.field.get_prep_value(value)
        deserialized = self.field.to_python(serialized)
        self.assertEqual(deserialized, value)

    def test_roundtrip_integer(self):
        """验证整数数据的往返一致性"""
        value = 12345
        serialized = self.field.get_prep_value(value)
        deserialized = self.field.to_python(serialized)
        self.assertEqual(deserialized, value)

    def test_roundtrip_none(self):
        """验证 None 值的处理"""
        # to_python 对 None 直接返回 None
        result = self.field.to_python(None)
        self.assertIsNone(result)

    def test_roundtrip_nested_structure(self):
        """验证复杂嵌套结构的往返一致性"""
        value = {
            "users": [
                {"name": "张三", "age": 30, "active": True},
                {"name": "李四", "age": 25, "active": False},
            ],
            "total": 2,
            "metadata": None,
        }
        serialized = self.field.get_prep_value(value)
        deserialized = self.field.to_python(serialized)
        self.assertEqual(deserialized, value)

    def test_roundtrip_empty_dict(self):
        """验证空字典的往返一致性"""
        value = {}
        serialized = self.field.get_prep_value(value)
        deserialized = self.field.to_python(serialized)
        self.assertEqual(deserialized, value)

    def test_roundtrip_empty_list(self):
        """验证空列表的往返一致性"""
        value = []
        serialized = self.field.get_prep_value(value)
        deserialized = self.field.to_python(serialized)
        self.assertEqual(deserialized, value)

    # ==================== 历史 pickle 格式兼容性测试 ====================

    def test_legacy_pickle_safe_types_readable(self):
        """验证历史 pickle 格式的安全类型数据可以正常读取"""
        # 模拟旧格式数据：直接 pickle + zlib（无 JSON_MAGIC 前缀）
        legacy_value = {"key1": "value1", "key2": [1, 2, 3]}
        legacy_serialized = zlib.compress(pickle.dumps(legacy_value))

        result = self.field.to_python(legacy_serialized)
        self.assertEqual(result, legacy_value)

    def test_legacy_pickle_integer_readable(self):
        """验证历史 pickle 格式的整数数据可以正常读取"""
        legacy_value = 42
        legacy_serialized = zlib.compress(pickle.dumps(legacy_value))

        result = self.field.to_python(legacy_serialized)
        self.assertEqual(result, legacy_value)

    def test_legacy_pickle_list_readable(self):
        """验证历史 pickle 格式的列表数据可以正常读取"""
        legacy_value = [1, "hello", 3.14, True, None]
        legacy_serialized = zlib.compress(pickle.dumps(legacy_value))

        result = self.field.to_python(legacy_serialized)
        self.assertEqual(result, legacy_value)

    # ==================== 安全性测试：恶意 pickle 拦截 ====================

    def test_malicious_pickle_os_system_blocked(self):
        """验证恶意 pickle payload（os.system）被白名单拦截"""

        class MaliciousPayload:
            def __reduce__(self):
                return (os.system, ("echo hacked",))

        malicious_data = zlib.compress(pickle.dumps(MaliciousPayload()))
        result = self.field.to_python(malicious_data)
        # 恶意数据应被拦截，返回 None
        self.assertIsNone(result)

    def test_malicious_pickle_eval_blocked(self):
        """验证恶意 pickle payload（eval）被白名单拦截"""

        class EvalPayload:
            def __reduce__(self):
                return (eval, ("__import__('os').system('echo hacked')",))

        malicious_data = zlib.compress(pickle.dumps(EvalPayload()))
        result = self.field.to_python(malicious_data)
        self.assertIsNone(result)

    def test_malicious_pickle_subprocess_blocked(self):
        """验证恶意 pickle payload（subprocess）被白名单拦截"""
        import subprocess

        class SubprocessPayload:
            def __reduce__(self):
                return (subprocess.call, (["echo", "hacked"],))

        malicious_data = zlib.compress(pickle.dumps(SubprocessPayload()))
        result = self.field.to_python(malicious_data)
        self.assertIsNone(result)

    # ==================== RestrictedUnpickler 白名单测试 ====================

    def test_restricted_unpickler_allows_basic_types(self):
        """验证 RestrictedUnpickler 允许基础类型"""
        # set 类型需要通过 pickle 的 REDUCE 操作码加载 builtins.set
        data = pickle.dumps({1, 2, 3})
        result = _restricted_pickle_loads(data)
        self.assertEqual(result, {1, 2, 3})

    def test_restricted_unpickler_allows_datetime(self):
        """验证 RestrictedUnpickler 允许 datetime 类型"""
        import datetime

        dt = datetime.datetime(2024, 1, 15, 10, 30, 0)
        data = pickle.dumps(dt)
        result = _restricted_pickle_loads(data)
        self.assertEqual(result, dt)

    def test_restricted_unpickler_blocks_os_module(self):
        """验证 RestrictedUnpickler 阻止 os 模块"""

        class OsPayload:
            def __reduce__(self):
                return (os.system, ("echo test",))

        data = pickle.dumps(OsPayload())
        with self.assertRaises(pickle.UnpicklingError) as ctx:
            _restricted_pickle_loads(data)
        self.assertIn("不允许反序列化类型", str(ctx.exception))

    def test_restricted_unpickler_blocks_arbitrary_class(self):
        """验证 RestrictedUnpickler 阻止任意自定义类（如 codecs.encode）"""
        import codecs

        # 使用一个可 pickle 但不在白名单中的标准库函数
        # pickle 协议会尝试加载 codecs.encode
        class CodecsPayload:
            def __reduce__(self):
                return (codecs.encode, (b"test", "hex_codec"))

        # 手动构造 pickle 数据（使用全局模块级别的可 pickle 对象）
        data = pickle.dumps(CodecsPayload(), protocol=2)
        with self.assertRaises(pickle.UnpicklingError):
            _restricted_pickle_loads(data)

    # ==================== 压缩级别测试 ====================

    def test_custom_compress_level(self):
        """验证自定义压缩级别正常工作"""
        field = IOField(compress_level=1)
        value = {"data": "x" * 1000}
        serialized = field.get_prep_value(value)
        deserialized = field.to_python(serialized)
        self.assertEqual(deserialized, value)

    # ==================== from_db_value 测试 ====================

    def test_from_db_value_delegates_to_to_python(self):
        """验证 from_db_value 正确委托给 to_python"""
        value = {"test": "data"}
        serialized = self.field.get_prep_value(value)
        result = self.field.from_db_value(serialized, None, None)
        self.assertEqual(result, value)

    def test_from_db_value_none(self):
        """验证 from_db_value 对 None 的处理"""
        result = self.field.from_db_value(None, None, None)
        self.assertIsNone(result)

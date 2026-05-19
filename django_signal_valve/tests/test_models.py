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

from django_signal_valve.models import (
    IOField,
    JSON_MAGIC,
    Signal,
    _restricted_pickle_loads,
)


class TestModels(TestCase):

    def tearDown(self):
        Signal.objects.all().delete()

    def test_manager_dump(self):
        """验证 SignalManager.dump 正常存储和读取信号参数"""
        kwargs = {"key1": "value1", "key2": [1, 2, 3], "key3": {"key4": "value4"}}
        Signal.objects.dump(module_path="path", signal_name="name", kwargs=kwargs)
        signal = Signal.objects.all()[0]
        self.assertEqual(signal.module_path, "path")
        self.assertEqual(signal.name, "name")
        self.assertEqual(signal.kwargs, kwargs)


class TestIOFieldSecurity(TestCase):
    """测试 IOField 的安全序列化/反序列化功能"""

    def setUp(self):
        self.field = IOField()

    # ==================== JSON 格式写入/读取测试 ====================

    def test_new_format_uses_json_magic_prefix(self):
        """验证新格式数据带有 JSON_MAGIC 前缀"""
        value = {"signal": "test", "args": [1, 2]}
        serialized = self.field.get_prep_value(value)
        decompressed = zlib.decompress(serialized)
        self.assertTrue(decompressed.startswith(JSON_MAGIC))

    def test_roundtrip_signal_kwargs(self):
        """验证信号参数字典的序列化/反序列化往返一致性"""
        value = {
            "sender": "test_module",
            "instance_id": 123,
            "action": "create",
            "extra": {"nested": True, "list": [1, 2, 3]},
        }
        serialized = self.field.get_prep_value(value)
        deserialized = self.field.to_python(serialized)
        self.assertEqual(deserialized, value)

    def test_roundtrip_none(self):
        """验证 None 值直接返回 None"""
        result = self.field.to_python(None)
        self.assertIsNone(result)

    # ==================== 历史 pickle 兼容性测试 ====================

    def test_legacy_pickle_dict_readable(self):
        """验证历史 pickle 格式的字典数据可以正常读取"""
        legacy_value = {"key1": "value1", "key2": [1, 2, 3]}
        legacy_serialized = zlib.compress(pickle.dumps(legacy_value))
        result = self.field.to_python(legacy_serialized)
        self.assertEqual(result, legacy_value)

    # ==================== 安全性测试 ====================

    def test_malicious_pickle_blocked(self):
        """验证恶意 pickle payload 被白名单拦截"""

        class MaliciousPayload:
            def __reduce__(self):
                return (os.system, ("echo hacked",))

        malicious_data = zlib.compress(pickle.dumps(MaliciousPayload()))
        result = self.field.to_python(malicious_data)
        # 恶意数据应被拦截，返回 None
        self.assertIsNone(result)

    def test_restricted_unpickler_blocks_dangerous_module(self):
        """验证 RestrictedUnpickler 阻止危险模块"""

        class DangerousPayload:
            def __reduce__(self):
                return (os.system, ("id",))

        data = pickle.dumps(DangerousPayload())
        with self.assertRaises(pickle.UnpicklingError) as ctx:
            _restricted_pickle_loads(data)
        self.assertIn("不允许反序列化类型", str(ctx.exception))

    def test_restricted_unpickler_allows_safe_types(self):
        """验证 RestrictedUnpickler 允许安全的基础类型"""
        # frozenset 需要通过 pickle 的 REDUCE 加载 builtins.frozenset
        data = pickle.dumps(frozenset([1, 2, 3]))
        result = _restricted_pickle_loads(data)
        self.assertEqual(result, frozenset([1, 2, 3]))

    # ==================== 集成测试：Signal 模型 ====================

    def test_signal_dump_and_read_with_new_format(self):
        """验证 Signal 模型使用新的安全格式存储和读取"""
        kwargs = {"sender": "app", "data": {"id": 1, "name": "test"}}
        Signal.objects.dump(
            module_path="test.signals",
            signal_name="post_save",
            kwargs=kwargs,
        )
        signal = Signal.objects.first()
        self.assertEqual(signal.kwargs, kwargs)
        self.assertEqual(signal.module_path, "test.signals")
        self.assertEqual(signal.name, "post_save")

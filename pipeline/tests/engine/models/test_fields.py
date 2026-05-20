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

import json
import pickle
import zlib

from django.test import SimpleTestCase

from pipeline.engine.models.fields import IOField, JSON_MAGIC, PICKLE_MAGIC
from pipeline.utils.collections import FancyDict


class RuntimeObject(object):
    def __init__(self, object_id, data=None):
        self.id = object_id
        self.data = data or {}


class EvilPickle(object):
    def __reduce__(self):
        return (eval, ("1 + 1",))


class IOFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.field = IOField()
        self.sample = {
            "key": "value",
            "items": [1, 2, 3],
            "nested": {"enabled": True},
        }
        self.runtime_field = IOField(restricted_loads=False)

    def test_get_prep_value_and_to_python_with_new_pickle_magic(self):
        prepared = self.field.get_prep_value(self.sample)

        self.assertIsInstance(prepared, bytes)
        self.assertTrue(zlib.decompress(prepared).startswith(PICKLE_MAGIC))
        self.assertEqual(self.field.to_python(prepared), self.sample)

    def test_to_python_with_legacy_pickle_payload(self):
        legacy_payload = zlib.compress(
            pickle.dumps(self.sample, protocol=pickle.HIGHEST_PROTOCOL)
        )

        self.assertEqual(self.field.to_python(legacy_payload), self.sample)

    def test_to_python_with_json_magic_payload(self):
        payload = zlib.compress(
            JSON_MAGIC + json.dumps(self.sample).encode("utf-8")
        )

        self.assertEqual(self.field.to_python(payload), self.sample)

    def test_to_python_with_fancydict_payload(self):
        value = FancyDict(self.sample)
        prepared = self.field.get_prep_value(value)

        result = self.field.to_python(prepared)

        self.assertIsInstance(result, FancyDict)
        self.assertEqual(result, value)

    def test_to_python_reject_unsafe_pickle_payload(self):
        payload = zlib.compress(
            PICKLE_MAGIC + pickle.dumps(EvilPickle(), protocol=pickle.HIGHEST_PROTOCOL)
        )

        self.assertIsNone(self.field.to_python(payload))

    def test_to_python_returns_none_for_invalid_compressed_payload(self):
        self.assertIsNone(self.field.to_python(b"not-a-valid-zlib-payload"))

    def test_get_prep_value_none(self):
        prepared = self.field.get_prep_value(None)

        self.assertIsInstance(prepared, bytes)
        self.assertTrue(zlib.decompress(prepared).startswith(PICKLE_MAGIC))
        self.assertIsNone(self.field.to_python(prepared))
        self.assertIsNone(self.field.to_python(None))

    def test_runtime_field_should_keep_pickle_object_roundtrip(self):
        runtime_object = RuntimeObject("pipeline-1", {"foo": "bar"})

        prepared = self.runtime_field.get_prep_value(runtime_object)
        restored = self.runtime_field.to_python(prepared)

        self.assertTrue(zlib.decompress(prepared).startswith(PICKLE_MAGIC))
        self.assertEqual(restored.id, "pipeline-1")
        self.assertEqual(restored.data, {"foo": "bar"})

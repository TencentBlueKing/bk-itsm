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
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from pipeline.core.data.base import DataObject
from pipeline.engine.core.data.redis_backend import (
    JSON_MAGIC,
    PICKLE_MAGIC,
    RedisDataBackend,
    _safe_dumps,
    _safe_loads,
)


class EvilPickle(object):
    def __reduce__(self):
        return (eval, ("1 + 1",))


class RedisDataBackendTestCase(SimpleTestCase):
    def setUp(self):
        self.backend = RedisDataBackend()
        self.redis_inst = MagicMock()
        self.sample = {
            "key": "value",
            "items": [1, 2, 3],
            "nested": {"enabled": True},
        }
        self.settings_patch = patch(
            "pipeline.engine.core.data.redis_backend.settings.REDIS_INST",
            self.redis_inst,
        )
        self.settings_patch.start()

    def tearDown(self):
        self.settings_patch.stop()

    def test_safe_dumps_adds_pickle_magic(self):
        dumped = _safe_dumps(self.sample)

        self.assertTrue(dumped.startswith(JSON_MAGIC))
        self.assertEqual(_safe_loads(dumped, "demo-key"), self.sample)

    def test_safe_loads_with_legacy_pickle_payload(self):
        dumped = pickle.dumps(self.sample, protocol=pickle.HIGHEST_PROTOCOL)

        self.assertEqual(_safe_loads(dumped, "demo-key"), self.sample)

    def test_safe_loads_with_json_magic_payload(self):
        dumped = JSON_MAGIC + json.dumps(self.sample).encode("utf-8")

        self.assertEqual(_safe_loads(dumped, "demo-key"), self.sample)

    def test_safe_loads_rejects_unsafe_pickle_payload(self):
        dumped = PICKLE_MAGIC + pickle.dumps(
            EvilPickle(), protocol=pickle.HIGHEST_PROTOCOL
        )

        self.assertIsNone(_safe_loads(dumped, "demo-key"))

    def test_get_object_returns_none_when_key_missing(self):
        self.redis_inst.get.return_value = None

        self.assertIsNone(self.backend.get_object("missing-key"))
        self.redis_inst.get.assert_called_once_with("missing-key")

    def test_set_and_get_object(self):
        dumped = _safe_dumps(self.sample)
        self.redis_inst.get.return_value = dumped

        self.backend.set_object("demo-key", self.sample)
        stored_payload = self.redis_inst.set.call_args[0][1]
        self.assertTrue(stored_payload.startswith(JSON_MAGIC))

        loaded = self.backend.get_object("demo-key")
        self.assertEqual(loaded, self.sample)

    def test_set_and_get_data_object(self):
        data_object = DataObject(
            inputs={"ticket_id": 1, "state_id": "sign-node"},
            outputs={"variables": {"foo": "bar"}},
        )
        dumped = _safe_dumps(data_object)
        self.redis_inst.get.return_value = dumped

        self.backend.set_object("schedule-parent-data", data_object)
        stored_payload = self.redis_inst.set.call_args[0][1]
        self.assertTrue(stored_payload.startswith(PICKLE_MAGIC))

        loaded = self.backend.get_object("schedule-parent-data")
        self.assertIsInstance(loaded, DataObject)
        self.assertEqual(loaded.inputs.ticket_id, 1)
        self.assertEqual(loaded.outputs.variables["foo"], "bar")

    def test_expire_cache_and_cache_for(self):
        dumped = _safe_dumps(self.sample)
        self.redis_inst.get.return_value = dumped

        self.assertTrue(self.backend.expire_cache("demo-key", self.sample, 30))
        self.redis_inst.set.assert_called_once()
        self.redis_inst.expire.assert_called_once_with("demo-key", 30)
        self.assertEqual(self.backend.cache_for("demo-key"), self.sample)

    def test_del_object(self):
        self.backend.del_object("demo-key")
        self.redis_inst.delete.assert_called_once_with("demo-key")

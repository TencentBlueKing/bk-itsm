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

import collections
import datetime
import logging
import pickle
from decimal import Decimal
from uuid import UUID

from pipeline.conf import settings
from pipeline.engine.core.data.base_backend import BaseDataBackend
from pipeline.engine.models.fields import (
    JSON_MAGIC,
    PICKLE_MAGIC,
    dumps_json_payload,
    dumps_pickle_payload,
    loads_json_payload,
)
from pipeline.utils.collections import FancyDict
from pipeline.utils.utils import convert_bytes_to_str

logger = logging.getLogger(__name__)


def _should_dump_as_json(data):
    if isinstance(data, FancyDict):
        return _should_dump_as_json(dict(data))

    if isinstance(data, collections.OrderedDict):
        return all(
            _should_dump_as_json(key) and _should_dump_as_json(item)
            for key, item in data.items()
        )

    if isinstance(data, collections.defaultdict):
        return _should_dump_as_json(dict(data))

    if isinstance(data, collections.deque):
        return all(_should_dump_as_json(item) for item in data)

    if isinstance(data, (list, tuple, set, frozenset)):
        return all(_should_dump_as_json(item) for item in data)

    if isinstance(data, dict):
        return all(
            isinstance(key, str) and _should_dump_as_json(item)
            for key, item in data.items()
        )

    return data is None or isinstance(
        data,
        (
            str,
            int,
            float,
            bool,
            bytes,
            bytearray,
            datetime.datetime,
            datetime.date,
            datetime.time,
            datetime.timedelta,
            Decimal,
            UUID,
        ),
    )


def _pickle_loads(data, key):
    try:
        return pickle.loads(data)
    except UnicodeDecodeError:
        logger.warning("RedisDataBackend 检测到历史 py2 pickle 数据，key=%s", key)
        return convert_bytes_to_str(pickle.loads(data, encoding="bytes"))


def _safe_loads(data, key):
    if not data:
        return None

    try:
        if data.startswith(JSON_MAGIC):
            return loads_json_payload(data[len(JSON_MAGIC) :])

        if data.startswith(PICKLE_MAGIC):
            return _pickle_loads(data[len(PICKLE_MAGIC) :], key)

        logger.warning("RedisDataBackend 检测到历史原生 pickle 缓存，key=%s", key)
        return _pickle_loads(data, key)
    except Exception:
        logger.exception("RedisDataBackend 反序列化异常，key=%s", key)
        return None


def _safe_dumps(data):
    if _should_dump_as_json(data):
        return dumps_json_payload(data)
    return dumps_pickle_payload(data)


class RedisDataBackend(BaseDataBackend):
    def set_object(self, key, obj):
        return settings.REDIS_INST.set(key, _safe_dumps(obj))

    def get_object(self, key):
        pickle_str = settings.REDIS_INST.get(key)
        if not pickle_str:
            return None
        return _safe_loads(pickle_str, key)

    def del_object(self, key):
        return settings.REDIS_INST.delete(key)

    def expire_cache(self, key, value, expires):
        settings.REDIS_INST.set(key, _safe_dumps(value))
        settings.REDIS_INST.expire(key, expires)
        return True

    def cache_for(self, key):
        cache = settings.REDIS_INST.get(key)
        return _safe_loads(cache, key) if cache else cache

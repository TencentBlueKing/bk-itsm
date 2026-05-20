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

import logging
import pickle

from pipeline.conf import settings
from pipeline.engine.core.data.base_backend import BaseDataBackend
from pipeline.engine.models.fields import (
    JSON_MAGIC,
    PICKLE_MAGIC,
    dumps_json_payload,
    loads_json_payload,
    restricted_pickle_loads,
)
from pipeline.utils.utils import convert_bytes_to_str

logger = logging.getLogger(__name__)


def _safe_pickle_loads(data, key):
    try:
        return restricted_pickle_loads(data)
    except UnicodeDecodeError:
        logger.warning("RedisDataBackend 检测到历史 py2 pickle 数据，key=%s", key)
        return convert_bytes_to_str(restricted_pickle_loads(data, encoding="bytes"))


def _safe_loads(data, key):
    if not data:
        return None

    try:
        if data.startswith(JSON_MAGIC):
            return loads_json_payload(data[len(JSON_MAGIC) :])

        if data.startswith(PICKLE_MAGIC):
            return _safe_pickle_loads(data[len(PICKLE_MAGIC) :], key)

        logger.warning("RedisDataBackend 检测到历史原生 pickle 缓存，key=%s", key)
        return _safe_pickle_loads(data, key)
    except pickle.UnpicklingError as error:
        logger.error(
            "RedisDataBackend 安全拦截：拒绝反序列化不安全的 pickle 数据，key=%s error=%s",
            key,
            error,
        )
        return None
    except Exception:
        logger.exception("RedisDataBackend 反序列化异常，key=%s", key)
        return None


def _safe_dumps(data):
    return dumps_json_payload(data)


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

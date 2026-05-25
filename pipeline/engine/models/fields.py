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

import base64
import collections
import datetime
import io
import json
import logging
import pickle
import zlib
from decimal import Decimal
from uuid import UUID

from django.db import models

from pipeline.engine.contants import PICKLE_SAFE_ALLOWLIST
from pipeline.utils.collections import FancyDict
from pipeline.utils.utils import convert_bytes_to_str

logger = logging.getLogger(__name__)

JSON_MAGIC = b"__JSON__"
PICKLE_MAGIC = b"__PICKLE__"
JSON_TYPE_KEY = "__pipeline_type__"
JSON_VALUE_KEY = "value"


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        allowed_names = PICKLE_SAFE_ALLOWLIST.get(module)
        if allowed_names is not None and name in allowed_names:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(
            "IOField 安全限制：不允许反序列化类型 {}.{}".format(module, name)
        )


def restricted_pickle_loads(data, encoding="ASCII", errors="strict"):
    return RestrictedUnpickler(
        io.BytesIO(data), encoding=encoding, errors=errors
    ).load()


def _to_json_safe(value):
    if isinstance(value, FancyDict):
        return {
            JSON_TYPE_KEY: "FancyDict",
            JSON_VALUE_KEY: _to_json_safe(dict(value)),
        }

    if isinstance(value, collections.OrderedDict):
        return {
            JSON_TYPE_KEY: "OrderedDict",
            JSON_VALUE_KEY: [
                [_to_json_safe(key), _to_json_safe(item)]
                for key, item in value.items()
            ],
        }

    if isinstance(value, collections.defaultdict):
        return {
            JSON_TYPE_KEY: "defaultdict",
            JSON_VALUE_KEY: _to_json_safe(dict(value)),
        }

    if isinstance(value, collections.deque):
        return {
            JSON_TYPE_KEY: "deque",
            JSON_VALUE_KEY: [_to_json_safe(item) for item in value],
        }

    if isinstance(value, tuple):
        return {
            JSON_TYPE_KEY: "tuple",
            JSON_VALUE_KEY: [_to_json_safe(item) for item in value],
        }

    if isinstance(value, set):
        return {
            JSON_TYPE_KEY: "set",
            JSON_VALUE_KEY: [_to_json_safe(item) for item in value],
        }

    if isinstance(value, frozenset):
        return {
            JSON_TYPE_KEY: "frozenset",
            JSON_VALUE_KEY: [_to_json_safe(item) for item in value],
        }

    if isinstance(value, bytes):
        return {
            JSON_TYPE_KEY: "bytes",
            JSON_VALUE_KEY: base64.b64encode(value).decode("ascii"),
        }

    if isinstance(value, bytearray):
        return {
            JSON_TYPE_KEY: "bytearray",
            JSON_VALUE_KEY: base64.b64encode(bytes(value)).decode("ascii"),
        }

    if isinstance(value, datetime.datetime):
        return {
            JSON_TYPE_KEY: "datetime",
            JSON_VALUE_KEY: value.isoformat(),
        }

    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        return {
            JSON_TYPE_KEY: "date",
            JSON_VALUE_KEY: value.isoformat(),
        }

    if isinstance(value, datetime.time):
        return {
            JSON_TYPE_KEY: "time",
            JSON_VALUE_KEY: value.isoformat(),
        }

    if isinstance(value, datetime.timedelta):
        return {
            JSON_TYPE_KEY: "timedelta",
            JSON_VALUE_KEY: value.total_seconds(),
        }

    if isinstance(value, Decimal):
        return {
            JSON_TYPE_KEY: "Decimal",
            JSON_VALUE_KEY: str(value),
        }

    if isinstance(value, UUID):
        return {
            JSON_TYPE_KEY: "UUID",
            JSON_VALUE_KEY: str(value),
        }

    if isinstance(value, list):
        return [_to_json_safe(item) for item in value]

    if isinstance(value, dict):
        return {key: _to_json_safe(item) for key, item in value.items()}

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def _from_json_safe(value):
    if isinstance(value, list):
        return [_from_json_safe(item) for item in value]

    if not isinstance(value, dict):
        return value

    value_type = value.get(JSON_TYPE_KEY)
    payload = value.get(JSON_VALUE_KEY)

    if value_type == "FancyDict":
        return FancyDict(_from_json_safe(payload))

    if value_type == "OrderedDict":
        return collections.OrderedDict(
            (_from_json_safe(item[0]), _from_json_safe(item[1])) for item in payload
        )

    if value_type == "defaultdict":
        return collections.defaultdict(None, _from_json_safe(payload))

    if value_type == "deque":
        return collections.deque(_from_json_safe(payload))

    if value_type == "tuple":
        return tuple(_from_json_safe(item) for item in payload)

    if value_type == "set":
        return set(_from_json_safe(item) for item in payload)

    if value_type == "frozenset":
        return frozenset(_from_json_safe(item) for item in payload)

    if value_type == "bytes":
        return base64.b64decode(payload.encode("ascii"))

    if value_type == "bytearray":
        return bytearray(base64.b64decode(payload.encode("ascii")))

    if value_type == "datetime":
        return datetime.datetime.fromisoformat(payload)

    if value_type == "date":
        return datetime.date.fromisoformat(payload)

    if value_type == "time":
        return datetime.time.fromisoformat(payload)

    if value_type == "timedelta":
        return datetime.timedelta(seconds=payload)

    if value_type == "Decimal":
        return Decimal(payload)

    if value_type == "UUID":
        return UUID(payload)

    return {key: _from_json_safe(item) for key, item in value.items()}


def dumps_json_payload(value):
    return JSON_MAGIC + json.dumps(_to_json_safe(value), ensure_ascii=False).encode(
        "utf-8"
    )


def dumps_pickle_payload(value):
    return PICKLE_MAGIC + pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)


def loads_json_payload(payload):
    return _from_json_safe(json.loads(payload.decode("utf-8")))


class IOField(models.BinaryField):
    def __init__(self, compress_level=6, restricted_loads=True, *args, **kwargs):
        super(IOField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level
        self.restricted_loads = restricted_loads

    def get_prep_value(self, value):
        value = super(IOField, self).get_prep_value(value)
        if self.restricted_loads:
            payload = dumps_json_payload(value)
        else:
            payload = dumps_pickle_payload(value)
        return zlib.compress(payload, self.compress_level)

    def _load_pickle_payload(self, payload):
        if not self.restricted_loads:
            return pickle.loads(payload)
        try:
            return restricted_pickle_loads(payload)
        except UnicodeDecodeError:
            return convert_bytes_to_str(
                restricted_pickle_loads(payload, encoding="bytes")
            )

    def to_python(self, value):
        if value is None:
            return None

        try:
            value = super(IOField, self).to_python(value)
            if value is None:
                return None

            decompressed = zlib.decompress(value)

            if decompressed.startswith(JSON_MAGIC):
                return loads_json_payload(decompressed[len(JSON_MAGIC):])

            if decompressed.startswith(PICKLE_MAGIC):
                logger.warning(
                    "IOField 检测到历史 PICKLE_MAGIC 数据，已切换为%s反序列化。",
                    "原生 pickle" if not self.restricted_loads else "受限",
                )
                return self._load_pickle_payload(decompressed[len(PICKLE_MAGIC):])

            logger.warning(
                "IOField 检测到历史原生 pickle 数据，已切换为%s反序列化。",
                "原生 pickle" if not self.restricted_loads else "受限",
            )
            return self._load_pickle_payload(decompressed)
        except pickle.UnpicklingError as error:
            logger.error("IOField 安全拦截：拒绝反序列化不安全的 pickle 数据: %s", error)
            return None
        except Exception:
            logger.exception("IOField to_python 异常")
            return None

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

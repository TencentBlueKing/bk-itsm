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

import io
import json
import logging
import pickle
import zlib

from django.db import models

from pipeline.engine.contants import PICKLE_SAFE_ALLOWLIST
from pipeline.utils.utils import convert_bytes_to_str

logger = logging.getLogger(__name__)

JSON_MAGIC = b"__JSON__"
PICKLE_MAGIC = b"__PICKLE__"


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        allowed_names = PICKLE_SAFE_ALLOWLIST.get(module)
        if allowed_names is not None and name in allowed_names:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(
            "IOField 安全限制：不允许反序列化类型 {}.{}".format(module, name)
        )


def _restricted_pickle_loads(data, encoding="ASCII", errors="strict"):
    return RestrictedUnpickler(io.BytesIO(data), encoding=encoding, errors=errors).load()


def _compat_pickle_loads(data, encoding="ASCII", errors="strict"):
    return pickle.loads(data, encoding=encoding, errors=errors)


class IOField(models.BinaryField):
    def __init__(self, compress_level=6, restricted_loads=True, *args, **kwargs):
        super(IOField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level
        self.restricted_loads = restricted_loads

    def get_prep_value(self, value):
        value = super(IOField, self).get_prep_value(value)
        payload = PICKLE_MAGIC + pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        return zlib.compress(payload, self.compress_level)

    def _pickle_loads(self, payload, encoding="ASCII", errors="strict"):
        if self.restricted_loads:
            return _restricted_pickle_loads(payload, encoding=encoding, errors=errors)
        return _compat_pickle_loads(payload, encoding=encoding, errors=errors)

    def _load_pickle_payload(self, payload):
        try:
            return self._pickle_loads(payload)
        except UnicodeDecodeError:
            # 兼容历史 py2 pickle 数据
            return convert_bytes_to_str(
                self._pickle_loads(payload, encoding="bytes")
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
                json_data = decompressed[len(JSON_MAGIC):]
                return json.loads(json_data.decode("utf-8"))

            if decompressed.startswith(PICKLE_MAGIC):
                return self._load_pickle_payload(decompressed[len(PICKLE_MAGIC):])

            logger.warning("IOField 检测到历史原生 pickle 数据，已切换为%s加载。", "受限反序列化" if self.restricted_loads else "兼容反序列化")
            return self._load_pickle_payload(decompressed)
        except pickle.UnpicklingError as error:
            logger.error("IOField 安全拦截：拒绝反序列化不安全的 pickle 数据: %s", error)
            return None
        except Exception:
            logger.exception("IOField to_python 异常")
            return None

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

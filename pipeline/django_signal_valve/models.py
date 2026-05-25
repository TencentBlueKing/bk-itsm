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
import traceback
import zlib

from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

# JSON 格式数据的魔术前缀
JSON_MAGIC = b"__JSON__"

# pickle 反序列化白名单
_PICKLE_SAFE_ALLOWLIST = {
    "builtins": {
        "set",
        "frozenset",
        "list",
        "tuple",
        "dict",
        "str",
        "bytes",
        "bytearray",
        "int",
        "float",
        "complex",
        "bool",
        "type",
        "range",
        "slice",
    },
    "datetime": {
        "datetime",
        "date",
        "time",
        "timedelta",
        "timezone",
    },
    "decimal": {
        "Decimal",
    },
    "collections": {
        "OrderedDict",
        "defaultdict",
        "deque",
    },
    "uuid": {
        "UUID",
    },
}


class RestrictedUnpickler(pickle.Unpickler):
    """受限的 Unpickler，仅允许反序列化白名单中的安全类型。"""

    def find_class(self, module, name):
        allowed_names = _PICKLE_SAFE_ALLOWLIST.get(module)
        if allowed_names is not None and name in allowed_names:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(
            "IOField 安全限制：不允许反序列化类型 {}.{}".format(module, name)
        )


def _restricted_pickle_loads(data):
    """使用受限 Unpickler 安全地加载 pickle 数据"""
    return RestrictedUnpickler(io.BytesIO(data)).load()


class IOField(models.BinaryField):
    """
    安全的二进制序列化字段。
    写入使用 JSON，读取兼容历史 pickle（白名单保护）。
    """

    def __init__(self, compress_level=6, *args, **kwargs):
        super(IOField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level

    def get_prep_value(self, value):
        """序列化并压缩数据（使用安全的 JSON 格式）"""
        value = super(IOField, self).get_prep_value(value)
        json_bytes = json.dumps(value, ensure_ascii=False, default=str).encode("utf-8")
        return zlib.compress(JSON_MAGIC + json_bytes, self.compress_level)

    def to_python(self, value):
        """反序列化数据，兼容新旧格式"""
        if value is None:
            return None
        try:
            value = super(IOField, self).to_python(value)
            decompressed = zlib.decompress(value)

            # 新格式：JSON_MAGIC 前缀标识
            if decompressed.startswith(JSON_MAGIC):
                json_data = decompressed[len(JSON_MAGIC) :]
                return json.loads(json_data.decode("utf-8"))

            # 历史格式：使用受限 pickle 反序列化（白名单保护）
            logger.warning(
                "IOField: 检测到历史 pickle 格式数据，使用受限反序列化加载。"
            )
            return _restricted_pickle_loads(decompressed)

        except pickle.UnpicklingError as e:
            logger.error("IOField 安全拦截：拒绝反序列化不安全的 pickle 数据: %s", e)
            return None
        except Exception:
            logger.error("IOField to_python 异常: %s", traceback.format_exc())
            return None

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)


class SignalManager(models.Manager):
    def dump(self, module_path, signal_name, kwargs):
        self.create(module_path=module_path, name=signal_name, kwargs=kwargs)


class Signal(models.Model):
    module_path = models.TextField(_("信号模块名"))
    name = models.CharField(_("信号属性名"), max_length=64)
    kwargs = IOField(verbose_name=_("信号参数"))

    objects = SignalManager()

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

import io
import json
import logging
import pickle
import traceback
import zlib

from django.db import models

logger = logging.getLogger(__name__)

# JSON 格式数据的魔术前缀，用于区分新旧格式
JSON_MAGIC = b"__JSON__"

# pickle 反序列化白名单：仅允许加载以下安全模块和类型
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
    """
    受限的 Unpickler，仅允许反序列化白名单中的安全类型。
    用于兼容读取历史遗留的 pickle 格式数据，防止恶意 payload 执行。
    """

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

    写入：使用 JSON 序列化 + zlib 压缩，以 JSON_MAGIC 前缀标识。
    读取：优先尝试 JSON 格式；对历史 pickle 数据使用受限反序列化（白名单机制）。

    安全保证：
    - 新数据完全不使用 pickle，消除 RCE 风险。
    - 历史数据通过 RestrictedUnpickler 白名单机制保护，
      仅允许加载基础数据类型，阻止恶意 payload。
    """

    def __init__(self, compress_level=6, *args, **kwargs):
        super(IOField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level

    def get_prep_value(self, value):
        """序列化并压缩数据（使用安全的 JSON 格式）"""
        value = super(IOField, self).get_prep_value(value)
        # 使用 JSON 序列化，并添加魔术前缀以标识格式
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
                "建议重新保存该记录以自动转换为安全的 JSON 格式。"
            )
            return _restricted_pickle_loads(decompressed)

        except pickle.UnpicklingError as e:
            # 白名单拦截了不安全的类型
            logger.error("IOField 安全拦截：拒绝反序列化不安全的 pickle 数据: %s", e)
            return None
        except Exception:
            logger.error("IOField to_python 异常: %s", traceback.format_exc())
            return None

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

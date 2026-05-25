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

RPC_CODE = "source_uri"
TICKET_CONTEXT_KEY = "ticket_id"
TRIGGER_SOURCE = 'trigger'

# RemoteApi 导入文件大小上限（字节）；默认 1 MiB，可通过 env 覆盖。
try:
    REMOTE_API_IMPORT_MAX_BYTES = int(
        os.environ.get("BKAPP_REMOTE_API_IMPORT_MAX_BYTES", 1024 * 1024)
    )
except (TypeError, ValueError):
    REMOTE_API_IMPORT_MAX_BYTES = 1024 * 1024

# RemoteApi 单次导入条目数上限；默认 20，可通过 env 覆盖。
try:
    REMOTE_API_IMPORT_MAX_ITEMS = int(
        os.environ.get("BKAPP_REMOTE_API_IMPORT_MAX_ITEMS", 20)
    )
except (TypeError, ValueError):
    REMOTE_API_IMPORT_MAX_ITEMS = 20

# RemoteApi 单条导入项必备字段（缺一即拒绝）。
REMOTE_API_IMPORT_REQUIRED_FIELDS = ("name", "path", "method")

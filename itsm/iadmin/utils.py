# -*- encoding:utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

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

from common.utils import cmp
from itsm.helper.tasks import _db_fix_from_1_1_22_to_2_1_x, _db_fix_from_2_1_x_to_2_2_1

from .models import SystemSettings
from .contants import TRIGGER_SWITCH, SWITCH_OFF

MIGRATE_VERSIONS = {"2.2.1": [_db_fix_from_2_1_x_to_2_2_1], "2.1.17": [_db_fix_from_1_1_22_to_2_1_x]}


def version_cmp(version1, version2):
    """
    比较版本号大小
    """
    parts1 = [int(x) for x in version1.split('.')]
    parts2 = [int(x) for x in version2.split('.')]

    lendiff = len(parts1) - len(parts2)
    if lendiff > 0:
        parts2.extend([0] * lendiff)
    elif lendiff < 0:
        parts1.extend([0] * (-lendiff))

    for i, p in enumerate(parts1):
        ret = cmp(p, parts2[i])
        if ret:
            return ret
    return 0


def is_trigger_switch_off():
    return SystemSettings.objects.filter(key=TRIGGER_SWITCH, value=SWITCH_OFF).exists()

# -*- coding: utf-8 -*-
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

# 结果处理函数

import re

from common.log import logger


def equal(result_value, reference_value):
    """
    结果数据与指定数据是否相等
    """
    if isinstance(result_value, (list, set)) and isinstance(reference_value, (list, set)):
        return set(result_value) == set(reference_value)
    else:
        return str(result_value) == str(reference_value)


def include(result_value, reference_value):
    """结果数据是否为指定数据的子项"""
    if isinstance(result_value, (list, set)) and isinstance(reference_value, (list, set)):
        return set(result_value).issubset(set(reference_value))
    else:
        return result_value in reference_value


def intersection(result_value, reference_value):
    """求交集"""
    if isinstance(result_value, (list, set)) and isinstance(reference_value, (list, set)):
        return set(result_value) & set(reference_value)
    else:
        return set([])


def difference(result_value, reference_value):
    """求差集"""
    if isinstance(result_value, (list, set)) and isinstance(reference_value, (list, set)):
        return set(result_value).difference(set(reference_value))
    else:
        return set([])


def regular(result_value, regex):
    try:
        reg = re.compile(r"%s" % regex)
        if reg.findall(result_value):
            return True
    except Exception as e:
        logger.warning("match regular error: %s %s %s" % (result_value, regex, e))
    return False


def exclude(result_value, reference_value):
    """结果数据与指定数据无交集"""
    return not include(result_value, reference_value)

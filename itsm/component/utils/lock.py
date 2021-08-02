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

import functools
import time

from django.core.cache import cache


def share_lock(ttl=300, identify=None):
    def wrapper(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            token = str(time.time())
            # 防止函数重名导致方法失效，增加一个ID参数，可以通过ID参数屏蔽多模块函数名重复的问题
            # 例如，可以为`${module}_${method_used_for}`
            cache_key = 'celery_%s' % func.__name__ if identify is None else identify

            if cache.get(cache_key):
                return
            cache.set(cache_key, token, ttl)

            try:
                return func(*args, **kwargs)
            finally:
                if cache.get(cache_key) == token:
                    cache.delete(cache_key)

        return _inner

    return wrapper

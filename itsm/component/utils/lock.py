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
import pickle
import time
from hashlib import md5

from django.core.cache import cache

from common.log import logger


def share_lock(ttl=300, identify=None):
    def wrapper(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            token = str(time.time())
            # 防止函数重名导致方法失效，增加一个ID参数，可以通过ID参数屏蔽多模块函数名重复的问题
            # 例如，可以为`${module}_${method_used_for}`

            if identify is None:
                try:
                    logger.info("[share_lock] 正在解析参数 -> args={}".format(args))
                    args_key = md5(str(pickle.dumps(args)).encode("utf-8")).hexdigest()
                    logger.info("[share_lock] 正在解析参数 -> kwargs={}".format(kwargs))
                    kwargs_key = md5(
                        str(pickle.dumps(kwargs)).encode("utf-8")
                    ).hexdigest()
                    cache_key = args_key + kwargs_key
                except Exception as e:
                    logger.info(
                        "[share_lock] 解析参数出现异常 -> error={}, kwargs={}".format(e, kwargs)
                    )
                    cache_key = "celery_%s" % func.__name__
            else:
                cache_key = identify

            logger.info("[share_lock] cache_key -> cache_key={}".format(cache_key))

            if cache.get(cache_key):
                logger.info(
                    "[share_lock] 发现重复执行 -> key={}, kwargs={}".format(cache_key, kwargs)
                )
                return
            cache.set(cache_key, token, ttl)

            try:
                return func(*args, **kwargs)
            finally:
                if cache.get(cache_key) == token:
                    cache.delete(cache_key)

        return _inner

    return wrapper

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


import logging
import time

from six.moves import map, range

import redis
from django.conf import settings
from redis.exceptions import ConnectionError
from redis.sentinel import Sentinel

logger = logging.getLogger(__name__)

REDIS_CONF = {
    "host": settings.REDIS_HOST,
    "port": settings.REDIS_PORT,
    "db": settings.REDIS_DB,
    "password": settings.REDIS_PASSWORD,
    "sentinel_password": settings.REDIS_SENTINEL_PASSWORD,
}


CACHE_BACKEND_CONF_MAP = {
    "SLA": REDIS_CONF,
    "DEFAULT": REDIS_CONF,
}


class BaseRedisCache(object):
    def __init__(self, redis_class=None):
        self.redis_class = redis_class or redis.Redis
        self._instance = None
        self.refresh_time = 0
        self.refresh_instance()

    @classmethod
    def instance(cls, backend):
        _instance = "_%s_instance" % backend
        if not hasattr(cls, _instance):
            ins = cls(REDIS_CONF)
            setattr(cls, _instance, ins)
        return getattr(cls, _instance)

    def create_instance(self):
        raise NotImplementedError()

    def close_instance(self, instance=None):
        raise NotImplementedError()

    def refresh_instance(self):

        if self._instance is not None:
            self.close_instance(self._instance)

        for _ in range(3):
            try:
                self._instance = self.create_instance()
                self.refresh_time = time.time()
                break
            except Exception as err:
                logger.exception(err)

    def __getattr__(self, name):
        command = getattr(self._instance, name)

        def handle(*args, **kwargs):
            exception = None
            for _ in range(3):
                try:
                    return command(*args, **kwargs)
                except ConnectionError as err:
                    exception = err
                    self.refresh_instance()
                except Exception as err:
                    raise err
            if exception:
                raise exception

        return handle


class RedisCache(BaseRedisCache):
    """"""

    def __init__(self, redis_conf, redis_class=None, decode_responses=True):
        self.redis_conf = redis_conf
        if "sentinel_password" in self.redis_conf:
            self.redis_conf.pop("sentinel_password")
        if decode_responses:
            self.redis_conf.update({"decode_responses": True, "encoding": "utf-8"})
        super(RedisCache, self).__init__(redis_class)

    def create_instance(self):
        return self.redis_class(**self.redis_conf)

    def close_instance(self, instance=None):
        if instance:
            instance.connection_pool.disconnect()


class SentinelRedisCache(BaseRedisCache):
    SOCKET_TIMEOUT = getattr(settings, "REDIS_SOCKET_TIMEOUT", 60)
    MASTER_NAME = getattr(settings, "REDIS_SERVICE_NAME", "mymaster")

    def __init__(self, conf, redis_class=None, decode_responses=True):
        redis_conf = conf.copy()
        self.sentinel_host = redis_conf.pop("host")
        self.sentinel_port = redis_conf.pop("port")
        self.sentinel_password = redis_conf.pop("sentinel_password")
        self.socket_timeout = int(redis_conf.pop("socket_timeout", self.SOCKET_TIMEOUT))
        self.master_name = redis_conf.pop("master_name", self.MASTER_NAME)
        self.cache_mode = redis_conf.pop("cache_mode", "master")
        self.redis_conf = redis_conf
        # 插入默认参数
        if decode_responses:
            self.redis_conf.update({"decode_responses": True, "encoding": "utf-8"})
        super(SentinelRedisCache, self).__init__(redis_class)

    def create_instance(self):
        redis_sentinel = Sentinel(
            [(self.sentinel_host, self.sentinel_port,)],
            socket_connect_timeout=self.socket_timeout,
            password=self.sentinel_password,
        )
        instance = redis_sentinel.master_for(self.master_name, redis_class=self.redis_class, **self.redis_conf)
        list(map(self.close_instance, redis_sentinel.sentinels))
        return instance

    def close_instance(self, instance=None):
        if instance:
            instance.connection_pool.disconnect()


class Cache(redis.Redis):
    CacheTypes = {
        "RedisCache": RedisCache,
        "SentinelRedisCache": SentinelRedisCache,
    }

    CacheBackendType = getattr(settings, "CACHE_BACKEND_TYPE", "RedisCache")

    def __new__(cls, backend=None):
        backend = backend if backend else "DEFAULT"
        type_ = cls.CacheTypes[cls.CacheBackendType]
        return type_.instance(backend)

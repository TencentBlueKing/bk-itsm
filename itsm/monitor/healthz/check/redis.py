# -*- coding: utf-8 -*-
import redis
from django.conf import settings

from itsm.monitor.healthz.check.base import checker


@checker(collect_metric="redis.status")
def redis_status_checker():
    try:
        settings.REDIS_INST.ping()
    except (redis.exceptions.ConnectionError, ConnectionRefusedError) as e:
        return False, str(e)

    return True, ""


@checker(collect_metric="redis.write_and_read.status")
def redis_write_and_read_checker():
    try:
        settings.REDIS_INST.set("redis_check", "ping")
        value = settings.REDIS_INST.get("redis_check")
        if value == "ping":
            return True, ""
    except (redis.exceptions.ConnectionError, ConnectionRefusedError) as e:
        return False, str(e)

    return True, ""

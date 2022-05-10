# -*- coding: utf-8 -*-
from django.conf import settings

from itsm.monitor.healthz.check.base import checker
from kombu import Connection


@checker(collect_metric="rabbitmq.status")
def rabbitmq_status_checker():
    try:
        BROKER_URL = settings.BROKER_URL
        if not BROKER_URL.startswith("amqp://"):
            BROKER_URL = "amqp://guest:guest@localhost:5672//"
        conn = Connection(BROKER_URL)
        conn.connect()
        result = conn.connected, ""
        conn.release()
        return result
    except Exception as e:
        return False, str(e)

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

from __future__ import absolute_import

import threading
import time

import six
import celery
import celery.signals


import statsd


_state = threading.local()


def task_key(task):
    prefix = getattr(celery.current_app.conf,
                     "CELERY_STATSD_PREFIX", "celery.")

    if isinstance(task, six.string_types):
        return '{}{}'.format(prefix, task)
    else:
        return '{}{}'.format(prefix, task.name)


def get_client(celery_app):
    try:
        client = _state.clients[celery_app]
    except AttributeError:
        client = statsd.StatsClient(
            celery_app.conf.STATSD_HOST,
            celery_app.conf.STATSD_PORT
        )

        _state.clients = {celery_app: client}
    except KeyError:
        client = statsd.StatsClient(
            celery_app.conf.STATSD_HOST,
            celery_app.conf.STATSD_PORT
        )

        _state.clients[celery_app] = client

    return client


def start_timer(name, group, instance):
    try:
        _state.timers[(name, group, instance)] = time.time()
    except AttributeError:
        _state.timers = {(name, group, instance): time.time()}


def _get_timer(name, group, instance):
    try:
        return _state.timers.pop((name, group, instance))
    except (AttributeError, KeyError):
        return


def stop_timer(name, group, instance):

    start = _get_timer(name, group, instance)

    if start is None:
        return

    total = time.time() - start

    get_client(celery.current_app).timing(
        "{0}.{1}".format(group, name),
        total * 1000
    )


def inc_counter(name, group):
    get_client(celery.current_app).incr("{0}.{1}".format(group, name))


@celery.signals.before_task_publish.connect
def statsd_before_task_publish(sender, body, headers, **kwargs):
    task_id = headers.get('id') or body.get('id')
    start_timer("enqueue", task_key(sender), task_id)


@celery.signals.after_task_publish.connect
def statsd_after_task_publish(sender, body, headers, **kwargs):
    task_id = headers.get('id') or body.get('id')
    stop_timer("enqueue", task_key(sender), task_id)


@celery.signals.task_prerun.connect
def statsd_task_prerun(sender, task_id, **kwargs):
    start_timer("run", task_key(sender), task_id)


@celery.signals.task_postrun.connect
def statsd_task_postrun(sender, task_id, **kwargs):
    stop_timer("run", task_key(sender), task_id)


@celery.signals.task_retry.connect
def statsd_task_retry(sender, **kwargs):
    inc_counter("retry", task_key(sender))


@celery.signals.task_success.connect
def statsd_task_success(sender, **kwargs):
    inc_counter("success", task_key(sender))


@celery.signals.task_failure.connect
def statsd_task_failure(sender, **kwargs):
    inc_counter("failure", task_key(sender))


@celery.signals.task_revoked.connect
def statsd_task_revoked(sender, **kwargs):
    inc_counter("revoked", task_key(sender))

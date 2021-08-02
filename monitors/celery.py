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

# [2020-01-30 16:35:20,601: WARNING/Worker-3] celery.itsm.ticket.tasks.notify.published
# [2020-01-30 16:35:20,604: INFO/MainProcess] Received task: itsm.ticket.tasks.notify
# [f24e49b4-4b2f-49d7-b912-e7420f808fa7]
# [2020-01-30 16:35:20,609: WARNING/Worker-4] celery.itsm.ticket.tasks.notify.start
# [2020-01-30 16:35:20,610: WARNING/Worker-4] celery.itsm.ticket.tasks.notify.done
# [2020-01-30 16:35:20,612: INFO/MainProcess] Task itsm.ticket.tasks.notify
# [f24e49b4-4b2f-49d7-b912-e7420f808fa7] succeeded...
# [2020-01-30 16:35:20,636: WARNING/Worker-3] celery.pipeline.engine.tasks.start.done
# [2020-01-30 16:35:20,638: INFO/MainProcess] Task pipeline.engine.tasks.start
# [2c8a0134-1c9b-48e5-bbc6-828dbb87b786] succeeded...

from __future__ import absolute_import

import time

from statsd.defaults.django import statsd


_task_start_times = {}


def on_task_published(sender=None, task_id=None, task=None, **kwargs):
    """
    Handle Celery ``after_task_publish`` signals.
    """
    # Increase statsd counter.
    # print('celery.%s.published' % kwargs['body']['task'])
    statsd.incr("celery.%s.published" % kwargs["body"]["task"])


def on_task_prerun(sender=None, task_id=None, task=None, **kwargs):
    """
    Handle Celery ``task_prerun``signals.
    """
    # Increase statsd counter.
    # print('celery.%s.start' % task.name)
    statsd.incr("celery.%s.start" % task.name)

    # Keep track of start times. (For logging the duration in the postrun.)
    _task_start_times[task_id] = time.time()


def on_task_postrun(sender=None, task_id=None, task=None, **kwargs):
    """
    Handle Celery ``task_postrun`` signals.
    """
    # Increase statsd counter.
    # print('celery.%s.done' % task.name)
    statsd.incr("celery.%s.done" % task.name)

    # Log duration.
    start_time = _task_start_times.pop(task_id, False)
    if start_time:
        ms = int((time.time() - start_time) * 1000)
        statsd.timing("celery.%s.runtime" % task.name, ms)


def on_task_failure(sender=None, task_id=None, exception=None, *args, **kwargs):
    """
    Handle Celery ``task_failure`` signals.
    """
    # Increase statsd counter.
    # print('celery.%s.failure' % sender.name)
    statsd.incr("celery.%s.failure" % sender.name)


def on_task_success(sender=None, result=None, **kwargs):
    """
    Handle Celery ``task_success`` signals.
    """
    # Increase statsd counter.
    # print('celery.%s.success' % sender.name)
    statsd.incr("celery.%s.success" % sender.name)


def register_celery_events():
    try:
        from celery import signals
    except ImportError:
        pass
    else:
        signals.after_task_publish.connect(on_task_published)
        signals.task_prerun.connect(on_task_prerun)
        signals.task_postrun.connect(on_task_postrun)
        signals.task_failure.connect(on_task_failure)
        signals.task_success.connect(on_task_success)

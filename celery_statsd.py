# -*- coding: utf-8 -*-
"""
参考：
    https://docs.celeryproject.org/en/latest/userguide/monitoring.html
    https://lxkaka.wang/2018/11/21/celery-monitor/#&gid=1&pid=5
    https://www.infoq.com/news/2018/02/monitoring-queues-meilleursagent/
使用方法:

1.启动graphite和grafana: cd monitors && docker-compose up
2.修改`celery_statsd.py`的参数`http_api`为rabbitmq的api地址，默认为：
'http://guest:guest@localhost:15672/api/'
3.启动celery
4.监测worker和队列：python manage.py celery events -c celery_statsd.Camera -F 2.0
5.监测celery事件（任务、心跳等）：python celery_statsd.py
6.打开grafana，并导入`monitors/grafana_dashboard.json`

可选：python flowerd.py --persistent=true --port=6666 --url_prefix=flower --basic_auth=admin:admin
--broker_api=http://guest:guest@localhost:15672/api/
    启动flower作为实时监控方案，并提供一定的实时干预能力

statsd上报目录：
    celery.workers.{worker_hostname}.*
    celery.queues.{queue_name}.tasks
    celery.{task.name}.*

任务监控维度：
    统计维度 - count
        总任务数
        失败任务数【主要】
        成功任务数
    单任务维度 - count
        成功数
        失败数【主要】
        平均耗时/最大耗时【主要】
异常监控维度：
    worker
        心跳监测
        离线监测
    queue
        堵塞监测
    flow
        启动异常【start_pipeline/start】
        分支执行异常
        节点失败异常【service_schedule】

"""

import os
from collections import defaultdict

import django
from celery import states
from celery.events.snapshot import Polaroid

from monitors.utils import Broker


class Camera(Polaroid):
    clear_after = True  # clear after flush (incl, state.event_count).

    def on_shutter(self, state):
        if not state.event_count:
            # No new events since last snapshot.
            return
        # print('Workers: {0}'.format(pformat(state.workers, indent=4)))
        # print('Tasks: {0}'.format(pformat(state.tasks, indent=4)))
        # print('Total: {0.event_count} events, {0.task_count} tasks'.format(state))

        proceed_success, proceed_failure = defaultdict(int), defaultdict(int)
        for _, task in state.itertasks():
            if task.state == states.SUCCESS:
                proceed_success[task.worker.hostname] += 1
            if task.state == states.FAILURE:
                proceed_failure[task.worker.hostname] += 1

        for worker in state.workers:
            print(worker)
            if worker not in proceed_success:
                proceed_success[worker] = 0
            if worker not in proceed_failure:
                proceed_failure[worker] = 0

        from statsd.defaults.django import statsd as statsd_client

        for hostname, worker in state.workers.items():
            worker_name = worker.hostname
            statsd_client.gauge(f"celery.workers.{worker_name}.active", worker.active)
            statsd_client.gauge(f"celery.workers.{worker_name}.alive", worker.alive)
            statsd_client.gauge(f"celery.workers.{worker_name}.processed", worker.processed)
            statsd_client.gauge(
                f"celery.workers.{worker_name}.processed_succeeded", proceed_success[worker_name],
            )
            statsd_client.gauge(
                f"celery.workers.{worker_name}.processed_failed", proceed_failure[worker_name],
            )
            # statsd_client.gauge(
            #     f"celery.workers.{worker_name}.status_string", worker.status_string
            # )

        from blueapps.core.celery.celery import app as celery_app

        try:
            broker = Broker(
                celery_app.connection().as_uri(include_password=True),
                http_api="http://guest:guest@localhost:15672/api/",
            )
        except NotImplementedError:
            return

        # inspect active queue names
        inspect = celery_app.control.inspect()
        queue_names = set()
        for worker_name, queues in inspect.active_queues().items():
            for q in queues:
                queue_names.add(q["name"])

        # query broker: rq/redis...
        data = defaultdict(int)
        for queue in broker.queues(queue_names):
            data[queue["name"]] = queue.get("messages", 0)
            statsd_client.gauge(f"celery.queues.{queue['name']}.tasks", queue.get("messages", 0))

        # print("Queues: {0}".format(pformat(data, indent=4)))


def monitor(celery_app, statsd_client):
    state = celery_app.events.State()

    def _get_task(event):
        # task name is sent only with -received event,
        # and state will keep track of this for us.
        state.event(event)
        return state.tasks.get(event["uuid"])

    def on_task_received(event):
        task = _get_task(event)
        statsd_client.incr(f"celery.{task.name}.received")
        # print('TASK RECEIVED: %s[%s] %s' % (task.name, task.uuid, task.info(),))

    def on_task_revoked(event):
        task = _get_task(event)
        statsd_client.incr(f"celery.{task.name}.revoked")
        # print('TASK REVOKED: %s[%s] %s' % (task.name, task.uuid, task.info(),))

    def on_task_started(event):
        task = _get_task(event)
        statsd_client.incr(f"celery.{task.name}.started")
        # print('TASK STARTED: %s[%s] %s' % (task.name, task.uuid, task.info(),))

    def on_task_failed(event):
        task = _get_task(event)
        statsd_client.incr(f"celery.{task.name}.failed")
        # print('TASK FAILED: %s[%s] %s' % (task.name, task.uuid, task.info(),))

    def on_task_succeeded(event):
        task = _get_task(event)
        task_info = task.info()
        statsd_client.incr(f"celery.{task.name}.succeeded")
        statsd_client.timing(f"celery.{task.name}.runtime", int(task_info["runtime"] * 1000))
        # print('TASK SUCCEEDED: %s[%s] %s' % (task.name, task.uuid, task_info,))

    def on_worker_online(event):
        statsd_client.incr(f'celery.workers.{event["hostname"]}.online')

    def on_worker_offline(event):
        statsd_client.incr(f'celery.workers.{event["hostname"]}.offline')

    def on_worker_heartbeat(event):
        statsd_client.incr(f'celery.workers.{event["hostname"]}.heartbeat')

    with celery_app.connection() as connection:
        recv = celery_app.events.Receiver(
            connection,
            handlers={
                "task-started": on_task_started,
                "task-revoked": on_task_revoked,
                "task-received": on_task_received,
                "task-failed": on_task_failed,
                "task-succeeded": on_task_succeeded,
                "worker-online": on_worker_online,
                "worker-offline": on_worker_offline,
                "worker-heartbeat": on_worker_heartbeat,
            },
        )
        recv.capture(limit=None, timeout=None, wakeup=True)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    django.setup()

    from blueapps.core.celery.celery import app as celery_app
    from statsd.defaults.django import statsd as statsd_client

    monitor(celery_app, statsd_client)

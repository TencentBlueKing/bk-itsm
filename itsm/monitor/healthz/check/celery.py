# -*- coding: utf-8 -*-
from blueapps.core.celery.celery import app

from itsm.monitor.healthz.check.base import checker
from celery.app.control import Control


class CeleryClient(object):
    _application = None
    _control = None
    _default_queue = None

    def __init__(self, app):
        self._application = app
        self._control = Control(self._application)
        self._default_queue = self._application.amqp.default_queue.name
        self._routes = {}

    @property
    def application(self):
        return self._application

    @property
    def default_queue(self):
        return self._default_queue

    @property
    def routes(self):
        return self._routes

    def enable_events(self):
        self._control.enable_events()

    def disable_events(self):
        self._control.disable_events()

    def workers(self):
        response = self._control.inspect().stats()
        if not response:
            return []
        statuses = self.worker_statuses()
        queues = self.active_queues()
        workers = []
        for name, info in response.items():
            worker = dict()
            worker["name"] = name
            worker["status"] = statuses[worker["name"]]
            worker["concurrency"] = info["pool"]["max-concurrency"]
            worker["broker"] = {
                "transport": info["broker"]["transport"],
                "hostname": info["broker"]["hostname"],
                "port": info["broker"]["port"],
            }
            worker["queues"] = queues[worker["name"]]
            workers.append(worker)
        return workers

    def worker_statuses(self):
        """
        get worker statuses
        :return:
        """
        response = self._control.ping()
        if not response:
            return []
        workers = {}
        for w in response:
            for k, v in w.items():
                for k_inner, v_inner in v.items():
                    if k_inner == "ok" and v_inner == "pong":
                        workers[k] = "Active"
                    else:
                        workers[k] = "Passive"
                    break
        return workers

    def active_queues(self):
        """
        get queue mappings with workers
        :return:
        """
        response = self._control.inspect().active_queues()
        if not response:
            return []
        workers = {}
        for w, queues in response.items():
            workers[w] = list()
            for q in queues:
                workers[w].append(q["name"])
        return workers

    def registered_tasks(self):
        """
        get registered task list
        :return:
        """
        response = self._control.inspect().registered()
        if not response:
            return []
        all_tasks = set()
        for worker, tasks in response.items():
            for task in tasks:
                all_tasks.add(task)

        registered_tasks = {}
        for task in all_tasks:
            if task in self.routes:
                queue = self.routes[task].get("queue", self.default_queue)
            else:
                queue = self.default_queue
            registered_tasks[task] = queue
        return registered_tasks

    def active_tasks(self):
        """
        get active tasks which is running currently
        :return:
        """
        response = self._control.inspect().active()
        if not response:
            return []
        tasks = []
        for worker, task_list in response.items():
            for task in task_list:
                t = dict()
                t["queue"] = task["delivery_info"]["routing_key"]
                t["name"] = task["name"]
                t["id"] = task["id"]
                t["worker"] = worker
                tasks.append(t)
        return tasks

    def reserved_tasks(self):
        """
        get reserved tasks which is in queue but still waiting to be executed
        :return:
        """

        response = self._control.inspect().reserved()
        if not response:
            return []
        tasks = []
        for worker, task_list in response.items():
            for task in task_list:
                t = dict()
                t["queue"] = task["delivery_info"]["routing_key"]
                t["name"] = task["name"]
                t["id"] = task["id"]
                t["worker"] = worker
                tasks.append(t)
        return tasks


@checker(collect_metric="celery_worker.status")
def celery_worker_checker():
    try:
        client = CeleryClient(app=app)
        workers = client.workers()
        worker_count = len(workers)
        worker_active = 0
        for worker in workers:
            if worker["status"] == "Active":
                worker_active += 1

        if worker_active != worker_count:
            return False, "worker状态异常，异常数：{}/{}".format(
                worker_count - worker_active, worker_count
            )

        return True, "worker状态正常，{}/{}".format(worker_active, worker_count)
    except Exception as e:
        return False, str(e)

    return True, ""

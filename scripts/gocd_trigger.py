# -*- coding: utf-8 -*-
import contextlib
import datetime
import json
import shelve

import requests
import tornado.ioloop
import tornado.web

# global config
BRANCHES = ["refs/heads/develop_component_upgrade", "refs/heads/km"]
DEPLOY_KEY = "[ci deploy]"
BRANCHE_PIPELINES = {
    "refs/heads/develop_component_upgrade": "sync_develop",
    "refs/heads/km": "sync_km",
}


@contextlib.contextmanager
def shelve_open(name, **kwargs):
    try:
        db = shelve.open(name, **kwargs)
        yield db
    finally:
        db.close()


def incr(key, record):
    with shelve_open("shelve.db") as db:
        db[key] += 1
        db["last_time"] = str(datetime.datetime.now())
        db_records = db["records"]
        db_records.append(record)
        db["records"] = db_records


def fetch_stats():
    with shelve_open("shelve.db") as db:
        return dict(db)


def schedule_pipeline(pipeline):
    headers = {
        "Accept": "application/vnd.go.cd.v1+json",
        "Content-Type": "application/json",
    }
    url = "http://gocd.bksaas.com/go/api/pipelines/{}/schedule".format(pipeline)
    data = {
        "update_materials_before_scheduling": True,
    }

    return requests.post(url, headers=headers, json=data, auth=("miya", "miya.1009"))


def push_handler(data):
    """推送事件"""
    # "environment_variables": [
    #     {"name": "BRANCH", "secure": False, "value": branch},
    #     {"name": "APP_ID", "value": branch['branch'], "secure": False},
    # ],

    target_branch = data.get("ref")
    if target_branch not in BRANCHES:
        return False, "branch skipped"

    last_commit = data.get("commits")[0]
    last_commit_message = last_commit["message"]
    # if DEPLOY_KEY not in last_commit_message:
    #     return False, "push skipped"

    schedule_pipeline(BRANCHE_PIPELINES[target_branch])

    incr(
        "total",
        [data["user_name"], "push", target_branch, last_commit_message, last_commit["timestamp"], ],
    )

    return True, "success"


def merge_handler(data):
    """合并事件"""

    object_attributes = data["object_attributes"]
    target_branch, title = object_attributes["target_branch"], object_attributes["title"]

    if target_branch not in BRANCHES:
        return False, "target_branch skipped"

    if object_attributes["state"] != "merged":
        return False, "not merged skipped"

    # if DEPLOY_KEY not in object_attributes["title"]:
    #     return False, "title skipped"

    schedule_pipeline(BRANCHE_PIPELINES[target_branch])

    incr(
        "total", [object_attributes["user"]["name"], "merge", target_branch, title,
                  object_attributes["updated_at"], ],
    )

    return True, "success"


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(fetch_stats())

    def post(self):
        print(self.request.body)

        data = json.loads(self.request.body)
        action = data.get("object_kind")

        if action == "push":
            _, message = push_handler(data)

        elif action == "merge_request":
            _, message = merge_handler(data)
        else:
            message = "skip event: {}".format(action)

        self.write(message)


def make_app():
    return tornado.web.Application([(r"/", MainHandler), ])


if __name__ == "__main__":

    app = make_app()
    app.listen(8888)

    # store task stats in shelve.db
    with shelve_open("shelve.db", writeback=True) as db:
        if not db.keys():
            db.update(last_time=None, total=0, succeed=0, failed=0, records=[])

        print("please visit http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()

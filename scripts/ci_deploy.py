import contextlib
import datetime
import json
import shelve
import subprocess

import tornado.ioloop
import tornado.web

# global config
BRANCHES = ["refs/heads/master", "refs/heads/km"]
DEPLOY_KEY = "[ci deploy]"


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


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(fetch_stats())

    def post(self):
        print(self.request.body)

        data = json.loads(self.request.body)
        action = data.get("object_kind")

        if action == "push":
            target_branch = data.get("ref")
            if target_branch not in BRANCHES:
                self.write("branch skipped")
                return

            last_commit = data.get("commits")[0]
            last_commit_message = last_commit["message"]
            if DEPLOY_KEY not in last_commit_message:
                self.write("push skipped")
                return

            deploy_cmd = "python deploy.py xxx"
            subprocess.Popen(deploy_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            incr(
                "total", [data["user_name"], action, target_branch, last_commit_message,
                          last_commit["timestamp"], ],
            )

        elif action == "merge_request":
            object_attributes = data["object_attributes"]
            target_branch, title = object_attributes["target_branch"], object_attributes["title"]

            if target_branch not in BRANCHES:
                self.write("target_branch skipped")
                return

            if object_attributes["state"] != "merged":
                self.write("not merged skipped")
                return

            if DEPLOY_KEY not in object_attributes["title"]:
                self.write("title skipped")
                return

            deploy_cmd = "python deploy.py xxx"
            subprocess.Popen(deploy_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            incr(
                "total",
                [object_attributes["user"]["name"], action, target_branch, title,
                 object_attributes["updated_at"], ],
            )

        self.write("success")


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

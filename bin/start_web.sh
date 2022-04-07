#!/bin/bash

python manage.py collectstatic --noinput
gunicorn wsgi -w 8 -b :$PORT --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"' --max-requests=200 --log-level debug --timeout 120

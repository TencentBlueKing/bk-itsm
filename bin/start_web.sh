#!/bin/bash

python manage.py sync_saas_apigw
python manage.py collectstatic --noinput
gunicorn wsgi -w 1 -b :$PORT -k gthread --threads 3 --timeout 600 --max-requests 500 --max-requests-jitter 100 --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"'
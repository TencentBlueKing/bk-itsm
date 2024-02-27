#!/bin/bash

python manage.py sync_saas_apigw
python manage.py collectstatic --noinput
echo "register notice center"
python manage.py register_notice
gunicorn wsgi -w 1 -b [::]:${PORT:-5000} -k gthread --threads $GUNICORN_THREAD_NUM --timeout 600 --max-requests 500 --max-requests-jitter 100 --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"'

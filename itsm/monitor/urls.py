# -*- coding: utf-8 -*-
from django.conf.urls import url

from itsm.monitor.views import healthz, ping

urlpatterns = [
    # main
    url(r"^healthz/$", healthz),
    url(r"ping/$", ping),
]

# -*- coding: utf-8 -*-
from django.urls import re_path

from itsm.monitor.views import healthz, ping

urlpatterns = [
    # main
    re_path(r"^healthz/$", healthz),
    re_path(r"ping/$", ping),
]

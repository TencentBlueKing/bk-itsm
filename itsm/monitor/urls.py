# -*- coding: utf-8 -*-
from django.conf.urls import url

from itsm.monitor.views import healthz, metrics

urlpatterns = [
    # main
    url(r"^healthz/$", healthz),
    url(r"metrics/$", metrics),
]

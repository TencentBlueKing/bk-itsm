# -*- coding: utf-8 -*-
from django.conf.urls import url

from itsm.openapi.devops_plugin import views

urlpatterns = [
    # main
    url(r"^devops_plugin/services/$", views.services),
    url(r"^devops_plugin/fields/$", views.service_fields),
]

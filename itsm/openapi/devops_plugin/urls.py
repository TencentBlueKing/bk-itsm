# -*- coding: utf-8 -*-
from django.urls import re_path

from itsm.openapi.devops_plugin import views

urlpatterns = [
    # main
    re_path(r"^devops_plugin/services/$", views.services),
    re_path(r"^devops_plugin/fields/$", views.service_fields),
]

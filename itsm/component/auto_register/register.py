# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from distutils.version import StrictVersion

import django
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from django.db import models

from .contants import ADMIN_FIELDS
from .strategy import StrategyDispatcher
from .utils import get_fields_from_model, create_admin_class, register_admin_class


def auto_register_admin_for_model(model: models.Model, **kwargs) -> None:
    """
    auto register admin for model
    :param model: model obj
    :param kwargs: user custom configuration, @example {
        list_display = ["x", "y", "z]
    }
    :return: None
    """
    fields = get_fields_from_model(model)
    config = {}
    for admin_field in ADMIN_FIELDS:
        dev_value = kwargs.get(admin_field, None)
        if dev_value:
            config[admin_field] = dev_value
            continue
        
        dispatcher = StrategyDispatcher(admin_field)
        config[admin_field] = dispatcher.get_value(fields)
        
    admin_class = create_admin_class(model, **config)
    register_admin_class(model, admin_class)


def django_greater_than(version: str) -> bool:
    """
    Check that the Django version meets the requirements

    :param version: str @example: 3.2.1
    :return: Boolean
    """
    v = django.get_version().split(".")
    django_version = "{}.{}".format(v[0], v[1])
    return StrictVersion(django_version) >= StrictVersion(version)


def get_apps(application_labels=None):
    """
    application_labels is a app_label list.
    :param application_labels: list["app_label", "app_label2"]
    :return: applications_list list[module_obj, module_obj]
    @example return [<module 'auto_register' from '/xxx/auto_register/__init__.py'>,]
    """
    if application_labels is None:
        application_labels = []
    if application_labels:
        applications = []
        for app_label in application_labels:
            if django_greater_than('1.7'):
                app_config = apps.get_app_config(app_label)
                applications.append(app_config.module)
            else:
                applications.append(models.get_app(app_label))
    else:
        applications = models.get_apps()

    return applications


def get_models_of_an_app(app_module):
    """
    app_module is the object returned by get_apps method (python module)
    """
    if django_greater_than('1.7'):
        app_name = get_app_name(app_module)
        app_config = apps.get_app_config(app_name)
        return list(app_config.get_models())
    else:
        return models.get_models(app_module)


def get_app_name(app_module):
    """
    app is the object (python module) returned by get_apps method
    """
    return app_module.__name__.split('.')[-1]


def auto_configure_admin_for_app(app):
    """
    根据app_name 自动注册 admin
    :param app: app module class
    :return: None
    """
    model_list = get_models_of_an_app(app)
    for model in model_list:
        try:
            auto_register_admin_for_model(model)
        except AlreadyRegistered:
            pass


def auto_configure_admin(applications=None) -> None:
    """
    批量从多个apps 中注册model
    # todo 支持黑名单过滤
    :param applications: list["app1", "app2", "app3]
    :param exclude_applications: list["app1", "app2", "app3"]
    :return: None
    """
    if applications is None:
        applications = []
    apps = get_apps(applications)
    for app in apps:
        auto_configure_admin_for_app(app)

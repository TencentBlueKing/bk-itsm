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

import os

from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate

# 执行app初始化操作，步骤位于migrate操作后，需要print信息到标准输出
# http://www.koopman.me/2015/01/django-signals-example/


def app_ready_handler(sender, **kwargs):
    from itsm.iadmin.models import CustomNotice, SystemSettings, ReleaseVersionLog
    from itsm.postman.models import RemoteApi, RemoteSystem
    from itsm.service.models import Service
    from itsm.workflow.models import TemplateField, Table, Workflow, Notify
    from itsm.component.constants import DEFAULT_TEMPLATE_FIELDS, DEFAULT_TABLE
    
    print("update notify type")
    Notify.init_builtin_notify()
    print("update notify template")
    CustomNotice.init_default_template()
    print("update notify system_settings")
    SystemSettings.init_default_settings()
    print("create default remote sys")
    RemoteSystem.init_default_system()
    print("create default remote api")
    RemoteApi.init_default_remote_api()
    # 解析release.md文件将版本日志信息存入存入数据库
    ReleaseVersionLog.objects.init_version_log_info("zh-cn")
    ReleaseVersionLog.objects.init_version_log_info("en")
    print("create_default_template_field")
    TemplateField.objects.create_default_template_field(DEFAULT_TEMPLATE_FIELDS)
    print("create default tables")
    Table.objects.init_table(DEFAULT_TABLE)
    print("create default workflows")
    Workflow.objects.init_builtin_workflow()
    print("create default services")
    Service.objects.init_builtin_services()
    print("init superusers")
    init_super_user()


def init_super_user():
    from blueapps.account.models import User

    for name in settings.INIT_SUPERUSER:
        try:
            User.objects.update_or_create(
                username=name,
                defaults={"is_staff": True, "is_active": True, "is_superuser": True},
            )
        except BaseException as error:
            print("init superuser %s error： %s" % (name, str(error)))


class IadminConfig(AppConfig):
    name = "itsm.iadmin"

    def ready(self):
        print("init redis settings")
        if not hasattr(settings, "REDIS") and "BKAPP_REDIS_HOST" in os.environ:
            settings.REDIS = {
                "host": os.getenv("BKAPP_REDIS_HOST"),
                "port": os.getenv("BKAPP_REDIS_PORT"),
                "password": os.getenv("BKAPP_REDIS_PASSWORD"),
                "service_name": os.getenv("BKAPP_REDIS_SERVICE_NAME", "mymaster"),
                "mode": os.getenv("BKAPP_REDIS_MODE", "single"),
                "db": os.getenv("BKAPP_REDIS_DB", 0),
            }
        post_migrate.connect(app_ready_handler, sender=self)

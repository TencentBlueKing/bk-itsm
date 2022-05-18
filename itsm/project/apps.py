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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

# 执行app初始化操作，步骤位于migrate操作后，需要print信息到标准输出
# http://www.koopman.me/2015/01/django-signals-example/

from django.apps import AppConfig
from django.db.models.signals import post_migrate


def check_and_create_new_settings():
    from itsm.iadmin.contants import PROJECT_SETTING
    from itsm.project.models import ProjectSettings
    from itsm.project.models import Project

    project_keys = Project.objects.values_list("key", flat=True)
    for project_key in project_keys:
        if project_key == "public":
            continue
        for project_setting in PROJECT_SETTING:
            ProjectSettings.objects.get_or_create(
                type=project_setting[1],
                key=project_setting[0],
                value=project_setting[2],
                project_id=project_key,
            )


def app_ready_handler(sender, **kwargs):
    from itsm.project.models import Project

    print("init default project start")
    try:
        Project.init_default_project()
        check_and_create_new_settings()
    except Exception as e:
        print("init default project exception: %s" % e)


class ProjectConfig(AppConfig):
    name = "itsm.project"

    def ready(self):
        post_migrate.connect(app_ready_handler, sender=self)

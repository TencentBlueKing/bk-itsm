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
import datetime

from django.apps import AppConfig
from django.db.models import signals
from django.conf import settings


def app_ready_handler(sender, **kwarg):
    from .models import TaskSchema

    # 初始化数据
    if not TaskSchema.objects.filter(component_type="SOPS", is_deleted=False).exists():
        print("create sops task schema")
        TaskSchema.objects.create(
            component_type="SOPS",
            name="标准运维任务模板",
            is_builtin=True,
            is_draft=False,
            is_enabled=True,
        )

    if settings.INIT_DEVOPS_TEMPLATE:
        if not TaskSchema.objects.filter(component_type="DEVOPS").exists():
            print("create devops task schema")
            TaskSchema.objects.create(
                component_type="DEVOPS",
                name="蓝盾任务模板",
                is_builtin=True,
                is_draft=False,
                is_enabled=True,
            )


def fix_migrate_error(sender, **kwarg):
    from django.db import connection

    migrations = {
        "0044_auto_20211002_1733": "0046_auto_20211021_0948",
        "0045_state_is_allow_skip": "0047_state_is_allow_skip",
    }
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT `app`, `name` FROM django_migrations where app="workflow";'
            )
            rows = cursor.fetchall()
            rows = [item[1] for item in rows]
            for migration, value in migrations.items():
                dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                if migration not in rows:
                    cursor.execute(
                        'INSERT INTO `django_migrations` (`app`, `name`, `applied`) VALUES ("{}", "{}", "{}");'.format(  # noqa
                            "workflow", migration, dt
                        )
                    )
                else:
                    if value not in rows:
                        cursor.execute(
                            'INSERT INTO `django_migrations` (`app`, `name`, `applied`) VALUES ("{}", "{}", "{}");'.format(  # noqa
                                "workflow", value, dt
                            )
                        )

    except BaseException as err:
        print(err)


class WorkflowConfig(AppConfig):
    name = "itsm.workflow"

    def ready(self):
        # post_migrate.connect(app_ready_handler, sender=self)
        # ======================================================================
        # WORKFLOW SIGNALS REGISTER
        # ======================================================================
        from .models import Workflow, Table, TemplateField, TaskSchema
        from .signals import dispatch
        from .signals.handlers import (
            init_after_workflow_created,
            after_basic_model_saved,
            after_base_field_saved,
            task_schema_created_handler,
        )

        signals.post_migrate.connect(app_ready_handler, sender=self)
        # signals.pre_migrate.connect(fix_migrate_error, sender=self)

        signals.post_save.connect(init_after_workflow_created, Workflow)
        signals.post_save.connect(after_basic_model_saved, Table)
        signals.post_save.connect(after_base_field_saved, TemplateField)
        signals.post_save.connect(task_schema_created_handler, TaskSchema)

        dispatch.dispatch()

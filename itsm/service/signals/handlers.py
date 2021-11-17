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

import traceback
from django.db import transaction


def register_builtin_approve_service(sender, **kwargs):
    try:
        from itsm.component.constants import INVISIBLE
        from itsm.service.models import Service, ServiceCatalog
        from itsm.workflow.signals.handlers import builtin_approval_workflow_create

        print("register builtin approve service begin")

        with transaction.atomic():
            parent = ServiceCatalog.objects.get(key="root")
            catalog, created = ServiceCatalog._objects.update_or_create(
                defaults={'name': "内置审批目录", "parent": parent, "is_deleted": False}, **{'key': "approve_service_catalog"}
            )
            version = builtin_approval_workflow_create()

            instance, created = Service.objects.get_or_create(
                defaults={'key': "request", "workflow": version, "creator": ""},
                **{"name": "内置审批服务", "display_type": INVISIBLE}
            )
            if created:
                instance.bind_catalog(catalog.id)
    except Exception as e:
        print(traceback.format_exc())
        print('register builtin approve service exception, msg is {} '.format(e))


def register_builtin_iam_service(sender, **kwargs):
    from itsm.workflow.models import Workflow
    from itsm.service.models import Service

    try:
        Workflow.objects.init_iam_default_workflow()
        Workflow.objects.init_iam_system()
        Service.objects.init_iam_services()
    except Exception as err:
        print(traceback.format_exc())
        print('register builtin iam exception, msg is {} '.format(err))
    
       
def register_builtin_bkbase_service(sender, **kwargs):
    from itsm.workflow.models import Workflow
    from itsm.service.models import Service

    try:
        Workflow.objects.init_bkbase_workflow()
        Service.objects.init_bkbase_services()
    except Exception as err:
        print(traceback.format_exc())
        print('register builtin bkbase exception, msg is {} '.format(err))


def register_builtin_service(sender, **kwargs):
    import os
    import json
    from django.conf import settings
    from itsm.workflow.models import Workflow
    from itsm.service.models import Service, ServiceCatalog
    from itsm.role.models import UserRole

    print("start to  register_builtin_service ")
    file_path = os.path.join(settings.PROJECT_ROOT, 'initials/service/')

    parent = ServiceCatalog.objects.get(key="root")
    catalog, _ = ServiceCatalog._objects.update_or_create(
        defaults={'name': "内置审批目录", "parent": parent, "is_deleted": False}, **{'key': "approve_service_catalog"}
    )
    for file_name in os.listdir(file_path):
        with open(os.path.join(file_path, file_name), "r", encoding="utf-8") as f:
            data = json.loads(f.read())
        for new_flow in data.get("flows"):
            Workflow.objects.restore(data=new_flow)

        insert_result = Service.objects.insert_services(data.get("services"), catalog=catalog)
        if not insert_result.get("result"):
            print(insert_result.get("message"))

        new_system = data.get("system")
        if UserRole.objects.filter(role_key=new_system.get("role_key")).exists():
            continue

        UserRole.objects.create(**new_system)

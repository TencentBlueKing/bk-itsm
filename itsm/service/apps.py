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

import traceback

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from itsm.service.signals.handlers import (
    register_builtin_approve_service,
    register_builtin_iam_service,
    register_builtin_service,
    register_builtin_bkbase_service,
)


def app_ready_handler(sender, **kwargs):
    from itsm.service.models import (
        # PropertyRecord,
        ServiceCatalog,
        ServiceCategory,
        # ServiceProperty,
        # OldSla,
        SysDict,
    )
    from itsm.component.constants import CATALOG

    try:
        ServiceCategory.init_service_data()
        # ServiceProperty.init_service_data()
        # PropertyRecord.init_service_data()
        # OldSla.init_sla_from_property()
        SysDict.objects.init_builtin_dicts()
        SysDict.objects.init_change_type_from_property()
        SysDict.objects.init_event_type_from_property()
        ServiceCatalog.objects.migrate_from_service_category()
        ServiceCatalog.objects.init_default_catalog(CATALOG)
    except Exception as e:
        print(traceback.format_exc())
        print('init/update service data exception: %s' % str(e))


class ServiceConfig(AppConfig):
    name = 'itsm.service'

    def ready(self):
        post_migrate.connect(app_ready_handler, sender=self)
        post_migrate.connect(register_builtin_approve_service, sender=self)
        post_migrate.connect(register_builtin_iam_service, sender=self)
        post_migrate.connect(register_builtin_service, sender=self)
        post_migrate.connect(register_builtin_bkbase_service, sender=self)

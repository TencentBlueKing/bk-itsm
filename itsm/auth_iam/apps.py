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

from django.apps import AppConfig
from django.db.models import signals


def app_ready_handler(sender, **kwargs):
    print('init builtin auth data')


class AuthIamConfig(AppConfig):
    name = 'itsm.auth_iam'

    def ready(self):
        from .signal_handler import grant_related_action_after_instance_created

        signals.post_migrate.connect(app_ready_handler, sender=self)
        signals.post_save.connect(grant_related_action_after_instance_created)

        from itsm.component.constants.iam import RESOURCES, ACTIONS
        from iam.meta import setup_system, setup_action, setup_resource
        from django.conf import settings

        setup_system(settings.BK_IAM_SYSTEM_ID, settings.BK_IAM_SYSTEM_NAME)
        for action in ACTIONS:
            setup_action(settings.BK_IAM_SYSTEM_ID, action['id'], action['name'])

        for resource in RESOURCES:
            setup_resource(settings.BK_IAM_SYSTEM_ID, resource['id'], resource['name'])

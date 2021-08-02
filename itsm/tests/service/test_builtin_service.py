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
__copyright__ = "Copyright © 2012-Now Tencent BlueKing. All Rights Reserved."

from django.test import TestCase
from itsm.service.signals.handlers import register_builtin_approve_service, register_builtin_service
from itsm.service.models import Service, ServiceCatalog
from itsm.workflow.models import Workflow, WorkflowVersion


class TicketTest(TestCase):
    def setUp(self):
        Workflow.objects.all().delete()
        WorkflowVersion.objects.all().delete()

    def tearDown(self):
        ServiceCatalog.objects.all().delete()
        Workflow.objects.all().delete()
        WorkflowVersion.objects.all().delete()

    def test_builtin(self):
        register_builtin_approve_service(sender=None)
        self.assertEqual(ServiceCatalog.objects.filter(key="approve_service_catalog").exists(), True)
        self.assertEqual(Service.objects.filter(name="内置审批服务", display_type="INVISIBLE").exists(), True)
        self.assertEqual(Workflow.objects.filter(name="内置审批流", flow_type="internal").exists(), True)
        self.assertEqual(WorkflowVersion.objects.filter(name="内置审批流", flow_type="internal").exists(), True)

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

import unittest

from iam.resource.utils import get_page_obj, get_filter_obj
from itsm.workflow.models import Workflow, WorkflowVersion
from itsm.auth_iam.resources.workflow import WorkFlowResourceProvider
from itsm.service.models import Service
from itsm.auth_iam.resources.service import ServiceResourceProvider
from itsm.auth_iam.resources.flow_version import WorkflowVersionResourceProvider


class IamSearchInstanceTest(unittest.TestCase):
    def setUp(self):
        keywords = ["测试", "test", "Test"]
        Workflow.objects.all().delete()
        WorkflowVersion.objects.all().delete()
        for index in range(0, 100):
            w = Workflow.objects.create(
                name="{keyword}_{index}".format(
                    keyword=keywords[index % 3], index=index
                )
            )
            flow_version = w.create_version()
            Service.objects.create(
                name="{keyword}_{index}".format(
                    keyword=keywords[index % 3], index=index
                ),
                workflow_id=flow_version.id,
            )

    def test_ch_search_instance(self):
        provider = WorkFlowResourceProvider()

        filter_obj = get_filter_obj({"keyword": "测试"}, ["keyword"])

        page = {"limit": 100, "offset": 0}

        page_obj = get_page_obj(page)
        instances = provider.search_instance(filter_obj, page_obj)

        self.assertEqual(instances.count, 34)

        s_provider = ServiceResourceProvider()
        service_instances = s_provider.search_instance(filter_obj, page_obj)

        self.assertEqual(service_instances.count, 34)

        v_provider = WorkflowVersionResourceProvider()
        version_instances = v_provider.search_instance(filter_obj, page_obj)

        self.assertEqual(version_instances.count, 34)

    def test_en_search_instance(self):
        provider = WorkFlowResourceProvider()

        filter_obj = get_filter_obj({"keyword": "test"}, ["keyword"])

        page = {"limit": 100, "offset": 0}

        page_obj = get_page_obj(page)
        instances = provider.search_instance(filter_obj, page_obj)

        self.assertEqual(instances.count, 66)

        s_provider = ServiceResourceProvider()
        service_instances = s_provider.search_instance(filter_obj, page_obj)

        self.assertEqual(service_instances.count, 100)

        v_provider = WorkflowVersionResourceProvider()
        version_instances = v_provider.search_instance(filter_obj, page_obj)

        self.assertEqual(version_instances.count, 66)

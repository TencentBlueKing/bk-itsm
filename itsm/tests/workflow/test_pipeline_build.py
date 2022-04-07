# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import sys

from django.test import TestCase

from pipeline.core.pipeline import Pipeline
from pipeline.parser.pipeline_parser import PipelineParser

from .pipeline_data import PIPELINE_DATA


class TestPipeline(TestCase):
    def setUp(self):
        from pipeline.component_framework.component import Component
        from pipeline.core.flow.activity import Service

        class TestService(Service):
            def execute(self, data, parent_data):
                return True

            def outputs_format(self):
                return []

        class TestComponent(Component):
            name = 'test'
            code = 'test'
            bound_service = TestService
            form = ''

    def test_build_tree(self):
        print(sys._getframe().f_code.co_name)

        # TODO：从workflow转换得到PIPELINE_DATA
        parser_obj = PipelineParser(PIPELINE_DATA, cycle_tolerate=True)
        self.assertIsInstance(parser_obj.parse(), Pipeline)

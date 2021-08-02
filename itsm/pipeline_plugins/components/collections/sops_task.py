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

import logging

from itsm.task.models import Task
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

logger = logging.getLogger("celery")


class SopsTaskService(Service):
    __need_schedule__ = True
    __multi_callback_enabled__ = True

    def execute(self, data, parent_data):
        logger.info("SopsTaskService execute: data={}, parent_data={}".format(data.inputs, parent_data.inputs))
        task_id = data.inputs.task_id
        task = Task.objects.get(id=task_id)
        task.do_before_enter_task()
        return True

    def schedule(self, data, parent_data, callback_data=None):
        logger.info(
            "SopsTaskService schedule: data={}, parent_data={}, callback_data={}".format(
                data.inputs, parent_data.inputs, callback_data
            )
        )
        task_id = callback_data["task_id"]
        operator = callback_data["operator"]
        fields = callback_data.get("fields", [])

        task = Task.objects.get(id=task_id)
        task.operate_sops_task(operator=operator, fields=fields)
        task.do_before_exit_task(operator)
        self.finish_schedule()

        return True


class SopsTaskComponent(Component):
    name = "标准运维任务"
    code = "sops_task"
    bound_service = SopsTaskService

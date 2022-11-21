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

from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.response import Response

from blueapps.account.decorators import login_exempt

from itsm.component.decorators import custom_apigw_required
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.drf.mixins import ApiGatewayMixin
from itsm.task.models import Task, SopsTask
from itsm.task.tasks import sops_task_poller


@method_decorator(login_exempt, name="dispatch")
class TaskViewSet(ApiGatewayMixin, component_viewsets.ModelViewSet):
    """
    任务视图集
    """

    pagination_class = None
    queryset = Task.objects.filter(is_valid=True)

    @action(detail=False, methods=["post"])
    @custom_apigw_required
    def sops_task_status(self, request):
        """
        sops状态回调接口
        """
        sops_tasks = SopsTask.objects.filter(sops_task_id__in=request.data.get("tasks"))
        task_id_list = [sops_task.task_id for sops_task in sops_tasks]
        sops_task_poller(task_id_list)

        return Response()

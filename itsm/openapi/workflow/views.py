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
from itsm.component.exceptions import ObjectNotExist
from itsm.openapi.workflow.serializers import WorkflowSerializer
from itsm.workflow.models import WorkflowVersion


@method_decorator(login_exempt, name="dispatch")
class WorkflowViewSet(ApiGatewayMixin, component_viewsets.ModelViewSet):
    """
    服务项视图集合
    """

    pagination_class = None
    queryset = WorkflowVersion.objects.all()

    @action(detail=False, methods=["get"], serializer_class=WorkflowSerializer)
    @custom_apigw_required
    def get_workflow_detail(self, request):
        """
        服务流程详情
        """

        workflow_id = request.query_params.get("workflow_id")

        try:
            workflow = self.queryset.get(pk=workflow_id)
            serializer = self.serializer_class(workflow)
        except WorkflowVersion.DoesNotExist:
            return Response(
                {
                    "result": False,
                    "code": ObjectNotExist.ERROR_CODE_INT,
                    "data": None,
                    "message": ObjectNotExist.MESSAGE,
                }
            )

        return Response(serializer.data)

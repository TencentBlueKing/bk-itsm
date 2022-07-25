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

from django.utils.translation import ugettext as _
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.constants import ResponseCodeStatus
from itsm.ticket.models import TicketField, TicketGlobalVariable
from itsm.ticket.permissions import TicketFieldPermissionValidate
from itsm.ticket.serializers import FieldSerializer
from itsm.ticket.utils import get_custom_api_data
from itsm.workflow.views import BaseFieldViewSet


class FieldViewSet(BaseFieldViewSet):
    """工单字段序列化"""

    serializer_class = FieldSerializer
    queryset = TicketField.objects.all()

    pagination_class = None
    filter_fields = {
        "ticket": ["exact"],
        "state_id": ["exact"],
    }
    permission_classes = (TicketFieldPermissionValidate,)

    @action(detail=True, methods=["get"])
    def custom_api_choices(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.source_type != "CUSTOM_API":
            return Response([])
        data = get_custom_api_data(obj)
        return Response(data)

    @action(detail=True, methods=["post"])
    def api_field_choices(self, request, *args, **kwargs):
        """
        api字段选项列表获取，支持跨节点字段引用、当局全局变量和字段引用
        """

        field_object = self.get_object()
        api_instance = field_object.api_instance
        ticket = field_object.ticket

        if api_instance is None:
            return Response(
                {
                    "result": False,
                    "code": ResponseCodeStatus.OBJECT_NOT_EXIST,
                    "message": _("对应的api配置不存在，请查询"),
                    "data": [],
                }
            )

        # 前端上下文
        params = {"params_%s" % key: value for key, value in request.data.items()}

        # 前端上下文除外的历史单据字段
        params.update(
            {
                "params_%s" % field["key"]: field["_value"]
                for field in ticket.fields.filter(_value__isnull=False)
                .exclude(_value="")
                .values("key", "_value")
                if field["key"] not in request.data.keys()
            }
        )

        # 单据全局变量
        params.update(
            {
                "params_%s" % item["key"]: item["value"]
                for item in TicketGlobalVariable.objects.filter(
                    ticket_id=ticket.id
                ).values("key", "value")
            }
        )

        # 单据全局属性
        global_context = ticket.get_global_context(
            return_format="dict", prefix="params_"
        )
        params.update(global_context)

        return Response(api_instance.get_api_choice(field_object.kv_relation, params))

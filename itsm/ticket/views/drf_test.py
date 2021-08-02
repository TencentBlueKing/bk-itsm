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

__author__ = u"蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

from rest_framework import serializers

from itsm.component.drf import viewsets as component_viewsets
from itsm.ticket.models import Ticket


class TicketTestSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, max_length=128)
    sn = serializers.CharField(required=False, max_length=128)
    current_status = serializers.CharField(default='CREATED')

    class Meta:
        model = Ticket
        fields = ('id', 'title', 'sn', 'current_status')


class TicketTestModelViewSet(component_viewsets.ModelViewSet):
    serializer_class = TicketTestSerializer
    queryset = Ticket.objects.all()

    def get_queryset(self):
        queryset = super(TicketTestModelViewSet, self).get_queryset()
        return queryset.values(*self.serializer_class.Meta.fields)

    def list(self, request, *args, **kwargs):
        return super(TicketTestModelViewSet, self).list(request, *args, **kwargs)

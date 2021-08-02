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

#  views相关模块代码

from rest_framework import viewsets
from rest_framework.views import APIView

from itsm.component.drf.mixins import ApiGenericMixin, PermissionApiGenericMixin
from itsm.component.drf.permissions import IamAuthPermit, IamAuthProjectViewPermit


class APIView(ApiGenericMixin, APIView):
    """APIView"""

    pass


class NormalModelViewSet(ApiGenericMixin, viewsets.ModelViewSet):
    pass


class ModelViewSet(ApiGenericMixin, viewsets.ModelViewSet):
    """按需改造DRF默认的ModelViewSet类"""

    permission_free_actions = []

    def perform_create(self, serializer):
        """创建时补充基础Model中的字段
        """

        user = serializer.context.get('request').user
        username = getattr(user, 'username', 'guest')
        serializer.save(creator=username, updated_by=username)

    def perform_update(self, serializer):
        """更新时补充基础Model中的字段
        """
        user = serializer.context.get('request').user
        username = getattr(user, 'username', 'guest')
        serializer.save(updated_by=username)


class AuthModelViewSet(ModelViewSet):
    permission_classes = (IamAuthPermit,)


class AuthWithoutResourceModelViewSet(ModelViewSet):
    permission_classes = (IamAuthProjectViewPermit,)


class PermissionModelViewSet(PermissionApiGenericMixin, ModelViewSet):
    """按需改造DRF默认的ModelViewSet类"""

    pass


class ReadOnlyModelViewSet(ApiGenericMixin, viewsets.ReadOnlyModelViewSet):
    """按需改造DRF默认的ModelViewSet类"""

    pass


class ViewSet(ApiGenericMixin, viewsets.ViewSet):
    """按需改造DRF默认的ViewSet类"""

    pass


class GenericViewSet(ApiGenericMixin, viewsets.GenericViewSet):
    """按需改造DRF默认的GenericViewSet类"""

    pass

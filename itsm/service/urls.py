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

from rest_framework.routers import DefaultRouter

from itsm.service.views import (
    CatalogServiceViewSet,
    CategoryModelViewSet,
    FavoriteModelViewSet,
    ServiceCatalogViewSet,
    ServiceViewSet,
    SlaViewSet,
    SysDictDataViewSet,
    SysDictViewSet,
)

routers = DefaultRouter(trailing_slash=True)

routers.register(r'catalogs', ServiceCatalogViewSet, basename="catalog")
routers.register(r'catalog_services', CatalogServiceViewSet, basename="catalog_service")
routers.register(r'slas', SlaViewSet, basename="sla")
routers.register(r'projects', ServiceViewSet, basename="project")
routers.register(r'datadicts', SysDictViewSet, basename="datadict")
routers.register(r'dictdatas', SysDictDataViewSet, basename="dictdatas")
routers.register(r'categories', CategoryModelViewSet, basename="services")
routers.register(r'favorites', FavoriteModelViewSet, basename="favorites")

urlpatterns = routers.urls

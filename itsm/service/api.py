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

from django.core.cache import cache
from django.utils.translation import ugettext as _
from itsm.component.constants import PREFIX_KEY

from .models import Service, ServiceCatalog


def get_catalog_fullname(catalog_id):
    """
    获取服务目录全名
    :param catalog_id: 
    :return: 
    """
    cache_key = "%scatalog_fullname_%s" % (PREFIX_KEY, catalog_id)
    catalog_fullname = cache.get(cache_key)
    if catalog_fullname:
        return _(catalog_fullname)
    catalog_fullname = ServiceCatalog._objects.get(id=catalog_id).link_parent_name_ex_root
    cache.set(cache_key, catalog_fullname, 30)
    return _(catalog_fullname)


def get_service_name(service_id):
    """
    获取服务名称
    """
    cache_key = "%sservice_name_%s" % (PREFIX_KEY, service_id)
    service_name = cache.get(cache_key)
    if service_name:
        return _(service_name)
    service_name = Service._objects.get(id=service_id).name
    cache.set(cache_key, service_name, 30)
    return _(service_name)

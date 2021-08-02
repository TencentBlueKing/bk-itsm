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

from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from itsm.service.models import Service, ServiceCatalog, OldSla


class ServiceCatalogAdmin(MPTTModelAdmin):
    list_display = (
        "id",
        "name",
        "parent",
        "level",
        "xt_only",
    )
    mptt_level_indent = 30

    def get_queryset(self, request):
        qs = super(ServiceCatalogAdmin, self).get_queryset(request)
        return qs.filter(is_deleted=False)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "name", "workflow", "is_valid")
    list_filter = (
        "key",
        "is_valid",
    )


class SlaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "level",
        "resp_time",
        "deal_time",
    )


admin.site.register(ServiceCatalog, ServiceCatalogAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(OldSla, SlaAdmin)

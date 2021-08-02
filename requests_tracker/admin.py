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

from requests_tracker.models import Record


class RecordAdmin(admin.ModelAdmin):
    list_display = ("id",
                    'api_uid', 'ticket_id', 'state_id', 'api_instance_id',
                    'status_code',
                    'show_date_created',
                    # "request_host",
                    # 'operator',
                    'duration',
                    '__unicode__',
                    )
    list_filter = ('date_created', 'method', 'api_uid', 'status_code')
    search_fields = ('request_message', 'operator', 'response_message')

    fieldsets = (
        (None, {
            'fields': ('uid',),
        }),
        ("Request", {
            'fields': ('operator', 'method', 'url', 'request_message',),
        }),
        ("Response", {
            'fields': ('status_code', 'response_message', "request_host"),
        }),
        ("Other Infamation", {
            'fields': ('api_uid', 'ticket_id', 'state_id', 'api_instance_id'),
        }),
        ("Important Datetimes", {
            'fields': ('date_created', 'duration',),
        }),
    )

    readonly_fields = (
        'uid', 'operator',
        'ticket_id', 'state_id', 'api_instance_id',
        'method', 'url',
        'status_code', "request_host",
        'api_uid', 'remark',
        'date_created', 'duration'
    )
    ordering = ["-date_created"]

    def show_date_created(self, obj):
        return obj.date_created.strftime("%Y-%m-%d %H:%M:%S")

    show_date_created.short_description = "Date created"


admin.site.register(Record, RecordAdmin)

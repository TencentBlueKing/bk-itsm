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

# Register your models here.
from itsm.iadmin.models import CustomNotice, MigrateLogs, SystemSettings, ReleaseVersionLog
from itsm.postman.models import RemoteApi, RemoteSystem


class CustomNoticeAdmin(admin.ModelAdmin):
    list_display = ("id", "update_at", "updated_by", "action", "notify_type")


admin.site.register(CustomNotice, CustomNoticeAdmin)


class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ("creator", "create_at", "updated_by", "update_at", "type", "key", "value")


admin.site.register(SystemSettings, SystemSettingsAdmin)


class RemoteSystemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "is_activated")


admin.site.register(RemoteSystem, RemoteSystemAdmin)


class RemoteApiAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "func_name", "is_activated")


admin.site.register(RemoteApi, RemoteApiAdmin)


class VersionLogAdmin(admin.ModelAdmin):
    list_display = ("version", "log", "create_at", "is_latest")


admin.site.register(ReleaseVersionLog, VersionLogAdmin)


class MigrateLogsAdmin(admin.ModelAdmin):
    list_display = (
        "version_from",
        "version_to",
        "operator",
        "create_at",
        "note",
        "exe_func",
        "is_finished",
        "is_success",
    )


admin.site.register(MigrateLogs, MigrateLogsAdmin)

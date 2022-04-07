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

from itsm.component.constants import NOTIFY_GLOBAL_VARIABLES, PUBLIC_PROJECT_PROJECT_KEY
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.exceptions import MigrateDataError
from itsm.iadmin.contants import ACTION_CHOICES, ACTION_CLASSIFY
from itsm.iadmin.models import (
    CustomNotice,
    MigrateLogs,
    SystemSettings,
    ReleaseVersionLog,
)
from itsm.iadmin.permissions import (
    IsMigrateSuperuser,
    SystemSettingPermit,
    CustomNotifyPermit,
)
from itsm.iadmin.serializers import (
    CustomNotifySerializer,
    MigrateLogsSerializer,
    SystemSettingsSerializer,
    VersionListSerializer,
    VersionLogsSerializer,
)
from itsm.iadmin.tasks import db_fix_by_version_list
from itsm.iadmin.utils import MIGRATE_VERSIONS, version_cmp


class ModelViewSet(component_viewsets.ModelViewSet):
    """按需改造DRF默认的ModelViewSet类"""

    def perform_create(self, serializer):
        """创建时补充基础Model中的字段"""
        user = serializer.context.get("request").user
        username = getattr(user, "username", "guest")
        serializer.save(creator=username, updated_by=username)

    def perform_update(self, serializer):
        """更新时补充基础Model中的字段"""
        user = serializer.context.get("request").user
        username = getattr(user, "username", "guest")
        serializer.save(updated_by=username)


class SystemSettingsViewSet(ModelViewSet):
    """系统设置视图"""

    serializer_class = SystemSettingsSerializer
    queryset = SystemSettings.objects.all()
    permission_classes = (SystemSettingPermit,)
    pagination_class = None
    filter_fields = {
        "key": ["exact"],
        "type": ["exact"],
        "id": ["exact"],
    }

    @action(detail=False, methods=["get"])
    def configrations(self, request, *args, **kwargs):
        """获取系统配置表"""

        return Response({q.key: q.value for q in self.queryset})


class CustomNotifyViewSet(ModelViewSet):
    """自定义通知视图"""

    serializer_class = CustomNotifySerializer
    queryset = CustomNotice.objects.all()
    pagination_class = None
    permission_classes = (CustomNotifyPermit,)

    filter_fields = {
        "notify_type": ["exact"],
        "used_by": ["exact"],
        "content_template": ["icontains", "contains"],
    }

    def list(self, request, *args, **kwargs):
        project_key = request.query_params.get(
            "project_key", PUBLIC_PROJECT_PROJECT_KEY
        )

        queryset = self.filter_queryset(self.get_queryset()).filter(
            project_key=project_key
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def variable_list(self, request, *args, **kwargs):
        """获取通知模板可用的变量列表"""

        return Response(NOTIFY_GLOBAL_VARIABLES)

    @action(detail=False, methods=["get"])
    def action_type(self, request, *args, **kwargs):
        used_by = request.query_params.get("used_by")
        data = dict(ACTION_CHOICES)
        return Response(ACTION_CLASSIFY.get(used_by, data))


class VersionLogsViewSet(component_viewsets.ReadOnlyModelViewSet):
    serializer_class = VersionLogsSerializer

    queryset = ReleaseVersionLog.objects.all()
    pagination_class = None
    http_method_names = ["get"]

    def get_queryset(self):
        lang = self.request.COOKIES.get("blueking_language", "zh-cn")
        return self.queryset.filter(lang=lang).order_by("-version_size")


class VersionListViewSet(component_viewsets.ReadOnlyModelViewSet):
    serializer_class = VersionListSerializer
    queryset = ReleaseVersionLog.objects.all()
    pagination_class = None
    http_method_names = ["get"]

    @action(detail=False, methods=["get"])
    def version_list(self, request, *args, **kwargs):
        """获取版本列表"""
        queryset = self.get_queryset()
        versions = []
        for item in queryset:
            versions.append(item.version)
        versions.sort(key=lambda x: tuple(int(v) for v in x.split(".")), reverse=True)
        return Response(versions)


class MigrateLogsViewSet(component_viewsets.ModelViewSet):
    """数据库迁移记录类"""

    serializer_class = MigrateLogsSerializer
    queryset = MigrateLogs.objects.all().order_by("-create_at")
    permission_classes = (IsMigrateSuperuser,)
    pagination_class = None
    regex_display_dict = {}
    regex_error_display = []

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 判断是否有未完成的异步数据迁移任务 调用异步任务去执行需要的数据迁移任务
        migrate_logs = MigrateLogs.objects.all()
        if migrate_logs.exists():
            if not migrate_logs.last().is_finished:
                raise MigrateDataError(_("有数据迁移任务未完成"))

        versions = list(MIGRATE_VERSIONS.keys())
        versions.sort(key=lambda x: tuple(int(v) for v in x.split(".")))
        version_from = serializer.validated_data["version_from"]
        version_to = serializer.validated_data["version_to"]

        # # 根据用户选取的版本范围选取要执行数据迁移函数的版本号列表
        valid_versions = []
        for item in versions:
            # 从已有版本号中过滤出属于用户选择范围的版本号列表
            if (
                version_cmp(version_from, item) <= 0
                and version_cmp(item, version_to) <= 0
            ):
                valid_versions.append(item)

        # 组装需要执行的函数列表
        exe_funcs = []
        for item in valid_versions:
            exe_funcs += MIGRATE_VERSIONS[item]

        # 从数据库中获取已经执行过的函数列表
        migrate_logs_queryset = migrate_logs.filter(is_success=True, is_finished=True)
        finished_funcs = []
        for item in migrate_logs_queryset:
            finished_funcs += item.exe_func
        finished_funcs = set(finished_funcs)

        # 过滤出需要执行的函数列表
        need_exe_funcs = []
        store_need_exe_funcs = []
        for item in exe_funcs:
            # 默认需要添加is_add为True
            is_add = True
            for finish_item in finished_funcs:
                if item.__name__ == finish_item:
                    # 如果已经被执行过则不需要添加is_add为False
                    is_add = False
                    break

            if is_add:
                need_exe_funcs.append(item)
                store_need_exe_funcs.append(item.__name__)

        # 如果需要执行的数据迁移函数列表为空则无需升级
        if not need_exe_funcs:
            raise MigrateDataError(_("已经是最新版本，无需升级。"))

        # 数据库记录迁移操作
        migrate_log = MigrateLogs.objects.create(
            version_from=version_from,
            version_to=version_to,
            operator=request.user.username,
            exe_func=store_need_exe_funcs,
        )
        # 调用异步任务去执行需要的数据迁移操作
        db_fix_by_version_list.apply_async((need_exe_funcs, migrate_log.id))
        return Response()

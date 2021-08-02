# coding=utf-8
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
from rest_framework import serializers
from rest_framework.fields import empty

from itsm.component.constants import LEN_NORMAL, LEN_XXX_LONG
from itsm.component.exceptions import ParamError
from itsm.component.drf.serializers import AuthModelSerializer
from itsm.iadmin.models import CustomNotice, MigrateLogs, SystemSettings, ReleaseVersionLog
from itsm.iadmin.utils import version_cmp
from itsm.iadmin.validators import PathTypeValidators


class MigrateLogsSerializer(serializers.ModelSerializer):
    """模板序列化"""

    version_from = serializers.CharField(required=True, max_length=LEN_NORMAL)
    version_to = serializers.CharField(required=True, max_length=LEN_NORMAL)
    exe_func = serializers.JSONField(required=False)

    class Meta:
        model = MigrateLogs
        fields = ("version_from", "version_to", "operator", "create_at", "note", "exe_func")

    def validate(self, data):
        """
        Check that version_from is before version_to.
        """
        if version_cmp(data["version_from"], data["version_to"]) > 0:
            raise ParamError(_("version_to must occur after version_from"))
        return data


class VersionLogsSerializer(serializers.ModelSerializer):
    """模板序列化"""

    class Meta:
        model = ReleaseVersionLog
        fields = ("version", "log", "create_at", "is_latest", "version_size")


class VersionListSerializer(serializers.ModelSerializer):
    """模板序列化"""

    class Meta:
        model = ReleaseVersionLog
        fields = ("version",)


class CustomNotifySerializer(AuthModelSerializer):
    """模板序列化"""

    content_template = serializers.CharField(
        required=True, min_length=1, max_length=LEN_XXX_LONG, error_messages={"blank": _("消息模板不能为空")}
    )

    class Meta:
        model = CustomNotice
        fields = (
            "id",
            "title_template",
            "content_template",
            "notify_type",
            "action",
            "action_name",
            "updated_by",
            "update_at",
            "used_by",
        )


class SystemSettingsSerializer(AuthModelSerializer):
    """系统配置序列化"""

    type = serializers.CharField(required=True, max_length=LEN_NORMAL)
    key = serializers.CharField(required=True, max_length=LEN_NORMAL)

    class Meta:
        model = SystemSettings
        fields = ("id", "type", "key", "value")

    def run_validation(self, data=empty):
        self.validators = (PathTypeValidators(self.instance),)
        return super(SystemSettingsSerializer, self).run_validation(data)

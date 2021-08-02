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

import datetime
import hashlib
import os
import time
from wsgiref.util import FileWrapper

from django.conf import settings
from django.db import connection
from django.http import StreamingHttpResponse
from django.utils.encoding import escape_uri_path
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from itsm.component.decorators import (
    validate_file_name,
    validate_filepath_settings,
    validate_files_name,
)
from itsm.component.utils.response import Fail, Success
from itsm.iadmin.models import SystemSettings
from weixin.core.decorators import weixin_login_exempt

# 文件存储对象
store = settings.STORE


def clean_cache(request):
    """清理缓存"""

    try:
        cursor = connection.cursor()
        cursor.execute("delete from `django_cache`")

        # 更新用户角色表的更新时间，达到清理缓存目的
        from itsm.role.models import BKUserRole

        BKUserRole.objects.update(update_at=datetime.datetime.now() - datetime.timedelta(minutes=30))

        return Success(message=_("缓存更新成功")).json()
    except Exception as e:
        return Fail(message=_("缓存更新失败：%s") % e).json()


def compile_file_path(request):
    """
    组装路径参数
    :param request: 如果为单据的为ticket_id, 为模版的用workflow_id
    :return:file_path 文件路径
    """
    tmp_key = request.GET.get("key") or ("tmp_%s" % int(time.time()))
    system_file_path = SystemSettings.objects.get(key="SYS_FILE_PATH").value

    file_prefix = request.GET.get("ticket_id") or "workflow_%s" % request.GET.get("workflow_id")

    file_path = os.path.join(system_file_path, "%s_%s" % (file_prefix, request.GET.get("state_id", "")), tmp_key)

    return file_path, tmp_key


@validate_filepath_settings
@require_POST
@csrf_exempt
@validate_files_name
def upload(request):
    """
    根据ticket_id 和 state_id上传文件
    加入了default的原因支持预览测试
    暂无权限控制
    """

    root = SystemSettings.objects.get(key="SYS_FILE_PATH").value

    fields_root = os.path.join(root, "fields")

    succeed_files = {}
    file_list = request.FILES.getlist("field_file")
    for upload_file in file_list:
        origin_name = upload_file.name
        file_name = f"{datetime.datetime.now()}{origin_name}"  # noqa
        file_name = hashlib.md5(file_name.encode()).hexdigest()

        file_path = os.path.join(fields_root, file_name)
        store.save(file_path, upload_file)

        succeed_files[file_name] = {"name": origin_name, "path": file_path}

    # 前端控件要求: PC端code必须为0，WEIXIN端code必须为OK
    code = "OK" if "weixin" in request.path else 0

    return Success({"succeed_files": succeed_files}, code=code).json()


@weixin_login_exempt
@validate_filepath_settings
@require_GET
@validate_file_name
def download(request):
    """
    根据ticket_id 和 state_id下载文件
    暂无权限控制
    """
    file_path, tmp_key = compile_file_path(request)
    file_name = request.GET.get("file_name")

    download_file_path = os.path.join(file_path, file_name)
    if not store.exists(download_file_path):
        return Fail(_("文件【{}】不存在").format(file_name), "NO_SUCH_FILE").json()

    response = StreamingHttpResponse(FileWrapper(store.open(file_path, "rb"), 512))
    response["Content-Type"] = "application/octet-stream"
    response["Content-Disposition"] = "attachment; filename* = UTF-8''%s" % format(escape_uri_path(file_name))

    return response

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

import datetime

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET
from mako.template import Template

from itsm.project.models import UserProjectAccessRecord
from common.log import logger
from config.default import FRONTEND_URL
from itsm.role.models import BKUserRole, UserRole


def index(request):
    """首页"""
    from adapter.core import TITLE, DOC_URL, LOGIN_URL

    # 默认为当前pass host
    BK_USER_MANAGE_HOST = settings.BK_USER_MANAGE_HOST
    # 如果来源域名非微信外网域名，则使用的BK_USER_MANAGE_HOST地址
    if (
        settings.WEIXIN_APP_EXTERNAL_HOST
        and settings.WEIXIN_APP_EXTERNAL_HOST.find(request.get_host()) == -1
    ):
        BK_USER_MANAGE_HOST = FRONTEND_URL

    logger.info("HTTP_REFERER={}".format(request.META.get("HTTP_REFERER", "")))
    # 更新cmdb通用角色
    UserRole.update_cmdb_common_roles()
    # 更新用户在各个系统的角色缓存
    BKUserRole.get_or_update_user_roles(request.user.username)
    try:
        DEFAULT_PROJECT = UserProjectAccessRecord.objects.get(
            username=request.user.username
        ).project_key
    except Exception:
        DEFAULT_PROJECT = ""

    return render(
        request,
        "index.html",
        {
            "is_vip": "true",
            # "is_vip": "true" if request.META.get("HTTP_X_TIF_UID", "") else "false",
            "chname": request.user.get_property("chname"),
            "username": request.user.username,
            "all_access": UserRole.get_access_by_user(request.user.username),
            "BK_CC_HOST": settings.BK_CC_HOST,
            "BK_JOB_HOST": settings.BK_JOB_HOST,
            "IS_ITSM_ADMIN": 1
            if UserRole.is_itsm_superuser(request.user.username)
            else 0,
            "CUSTOM_TITLE": TITLE(),
            "USE_LOG": "true",
            "LOGIN_URL": LOGIN_URL,
            "LOG_NAME": settings.LOG_NAME or _("流程服务"),
            "IS_USE_INVITE_SMS": "true" if settings.IS_USE_INVITE_SMS else "false",
            "BK_USER_MANAGE_HOST": BK_USER_MANAGE_HOST,
            "TAM_PROJECT_ID": settings.TAM_PROJECT_ID,
            "DEFAULT_PROJECT": DEFAULT_PROJECT,
            "DOC_URL": DOC_URL,
            "SOPS_URL": settings.SOPS_SITE_URL,
            "RUN_VER": settings.RUN_VER,
        },
    )


@require_GET
def get_footer(request):
    """
    @summary: 获取当前环境的页面 footer
    @param request:
    @return:
    """
    from adapter.core import FOOTER

    return JsonResponse(
        {
            "result": True,
            "data": Template(FOOTER()).render(year=datetime.datetime.now().year),
            "code": "OK",
            "message": "success",
        }
    )


template_name = "wiki/create.html"

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

import os
import datetime

from blueapps.account.decorators import login_exempt
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET
from mako.template import Template

from itsm.iadmin.contants import NOTICE_CENTER_SWITCH
from itsm.iadmin.models import SystemSettings
from itsm.project.models import UserProjectAccessRecord
from common.log import logger
from config.default import FRONTEND_URL
from itsm.role.models import BKUserRole, UserRole


class HttpResponseIndexRedirect(HttpResponseRedirect):
    def __init__(self, redirect_to, *args, **kwargs):
        super(HttpResponseIndexRedirect, self).__init__(redirect_to, *args, **kwargs)
        self["Location"] = os.path.join(
            settings.WEIXIN_APP_EXTERNAL_HOST.replace("https", "http"),
            redirect_to.lstrip("/"),
        )


def init(request):
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
    return JsonResponse(
        {
            "code": 0,
            "result": True,
            "data": {
                "DEFAULT_PROJECT": DEFAULT_PROJECT,
                "chname": request.user.get_property("chname"),
                "username": request.user.username,
                "all_access": UserRole.get_access_by_user(request.user.username),
                "IS_ITSM_ADMIN": 1
                if UserRole.is_itsm_superuser(request.user.username)
                else 0,
                "need_target": False,  # 不需要强制跳转无权限页
                "location": "",
            },
            "message": "",
        }
    )


@login_exempt
def index(request):
    """首页"""
    from adapter.core import TITLE, LOGIN_URL

    # 如果发现不是woa过来的域名
    if (
        settings.WEIXIN_APP_EXTERNAL_HOST
        and settings.WEIXIN_APP_EXTERNAL_HOST.find(request.get_host()) == -1
    ):
        # 如果 host的值和HTTP_REFERER一致，则跳转
        # 如果是从开发者中心中出来的，此时有HTTP_REFERER
        if "HTTP_REFERER" not in request.META or request.get_host() in request.META.get(
            "HTTP_REFERER", ""
        ):
            return HttpResponseIndexRedirect(request.path)

    # 默认为当前pass host
    BK_USER_MANAGE_HOST = settings.BK_USER_MANAGE_HOST
    # 如果来源域名非微信外网域名，则使用的BK_USER_MANAGE_HOST地址
    if (
        settings.WEIXIN_APP_EXTERNAL_HOST
        and settings.WEIXIN_APP_EXTERNAL_HOST.find(request.get_host()) == -1
    ):
        BK_USER_MANAGE_HOST = FRONTEND_URL

    logger.info("HTTP_REFERER={}".format(request.META.get("HTTP_REFERER", "")))

    try:
        notice_center_switch_value = SystemSettings.objects.get(
            key=NOTICE_CENTER_SWITCH
        ).value
    except SystemSettings.DoesNotExist:
        notice_center_switch_value = "off"

    return render(
        request,
        "index.html",
        {
            "is_vip": "true",
            "BK_CC_HOST": settings.BK_CC_HOST,
            "BK_JOB_HOST": settings.BK_JOB_HOST,
            "CUSTOM_TITLE": TITLE,
            "USE_LOG": "true",
            "LOGIN_URL": LOGIN_URL,
            "LOG_NAME": _("流程服务"),
            "IS_USE_INVITE_SMS": "true" if settings.IS_USE_INVITE_SMS else "false",
            "BK_USER_MANAGE_HOST": BK_USER_MANAGE_HOST,
            "BK_PAAS_ESB_HOST": settings.BK_PAAS_ESB_HOST,
            "TAM_PROJECT_ID": settings.TAM_PROJECT_ID,
            "DOC_URL": settings.BK_DOC_URL,
            "SOPS_URL": settings.SOPS_SITE_URL,
            "NOTICE_CENTER_SWITCH": notice_center_switch_value,
            "BK_SHARED_RES_URL": settings.BK_SHARED_RES_URL,
            "BK_PLATFORM_NAME": settings.BK_PLATFORM_NAME,
            "VERSION": get_version()
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


def get_version():
    """
    @summary: 获取版本信息
    """
    # 读取文件内容
    app_desc = os.path.join(settings.PROJECT_ROOT, "VERSION")
    with open(app_desc, 'r') as file:
        content = file.read()
    return content.strip()


template_name = "wiki/create.html"

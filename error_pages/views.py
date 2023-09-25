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
from django.conf import settings
from django.http import HttpResponseRedirect

from common.mymako import render_mako_context


def error_404(request, exception):
    """
    404提示页
    """
    if settings.ENABLE_NOTIFY_ROUTER:
        url_flag = "/{}/".format(settings.NOTIFY_ROUTER_NAME)
        if url_flag in request.path:
            return HttpResponseRedirect(
                request.get_full_path().replace(url_flag, "/#/")
            )

    return render_mako_context(request, "404.html")


def error_500(request):
    """
    500提示页
    """
    return render_mako_context(request, "500.html")


def error_401(request):
    """
    401提示页
    """
    return render_mako_context(request, "401.html")


def error_403(request, exception):
    """
    403提示页
    """
    return render_mako_context(request, "403.html")

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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

from django.urls import include, re_path
from django_nyt.urls import get_pattern as get_nyt_pattern

from itsm.sites.views import index, get_footer, init
from weixin import views as weixin_views

urlpatterns = [
    # main
    re_path(r"^$", index),
    re_path(r"^init/$", init),
    # flower, celery monitor
    re_path(r"^o/bk_sops/", include("sops_proxy.urls")),
    # helper, fix database
    re_path(r"^helper/", include("itsm.helper.urls")),
    # weixin
    re_path(r"^weixin/$", weixin_views.index),
    re_path(r"^weixin/login/", include("weixin.core.urls")),
    re_path(r"^weixin/api/", include("weixin.urls")),
    # wiki
    re_path(r"^notifications/", get_nyt_pattern()),
    re_path(r"^core/footer/$", get_footer),
]

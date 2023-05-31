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

from django.conf.urls import include, url
from django_nyt.urls import get_pattern as get_nyt_pattern

from itsm.sites.views import index, get_footer, init
from weixin import views as weixin_views

urlpatterns = [
    # main
    url(r"^$", index),
    url(r"^init/$", init),
    # flower, celery monitor
    url(r"^o/bk_sops/", include("sops_proxy.urls")),
    # helper, fix database
    url(r"^helper/", include("itsm.helper.urls")),
    # weixin
    url(r"^weixin/$", weixin_views.index),
    url(r"^weixin/login/", include("weixin.core.urls")),
    url(r"^weixin/api/", include("weixin.urls")),
    # wiki
    url(r"^notifications/", get_nyt_pattern()),
    url(r"^core/footer/$", get_footer),
]

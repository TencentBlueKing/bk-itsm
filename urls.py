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
from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views import static

# 公共URL配置
urlpatterns = [
    # Django后台数据库管理®
    url(r"^admin/", admin.site.urls),
    # 用户登录鉴权
    # url(r'^account/', include('account.urls')),
    url(r"^account/", include("blueapps.account.urls")),
    # 接口版本管理
    url(r"^api/", include("itsm.api.v1")),
    # 对外开放的接口
    url(r"^openapi/", include("itsm.api.open_v1")),
    url(r"^openapi/v2/", include("itsm.api.open_v2")),
    # 监控，普罗米修斯相关的接口
    url(r"^monitor/", include("itsm.monitor.urls")),
    # 各种入口：微信/wiki/首页等
    url(r"^", include("itsm.sites.urls")),
]

# handler404 = 'error_pages.views.error_404'
handler500 = "error_pages.views.error_500"
handler403 = "error_pages.views.error_403"
handler401 = "error_pages.views.error_401"

# 本地生效：DEBUG=True
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 全局生效：不推荐生产环境使用
urlpatterns += [
    # wiki上传图片404也可以这样简单解决：路由层面不复用MEDIA_URL，后者只用来生成url，比如可以自定义prefix为SITE_URL
    url(r"^media/(?P<path>.*)$", static.serve, {"document_root": settings.MEDIA_ROOT}),
]

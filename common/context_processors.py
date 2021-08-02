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


# context_processor for common(setting)
# 除setting外的其他context_processor内容，均采用组件的方式(string)

from django.conf import settings


def mysetting(request):
    # 通过代理访问到系统的情况下，对静态资源地址做相应处理，如/o/bk_itsm -> /bkitsm/o/bk_itsm（bkitsm为转发带过来的前缀）
    proxy_path = request.META.get('HTTP_PROXY_PATH', '')
    proxy_path = '/{}'.format(proxy_path) if proxy_path and not proxy_path.startswith('/') else ''
    show_wiki = 'false' if proxy_path else 'true'

    return {
        # 静态资源（代理地址）
        'SHOW_WIKI': show_wiki,
        # 标准运维插件服务地址
        'SITE_URL_SOPS': settings.SITE_URL_SOPS,
        'PREFIX_SOPS': settings.PREFIX_SOPS,
        "BK_IAM_APP_CODE": settings.BK_IAM_APP_CODE,
    }

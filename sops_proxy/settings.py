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


from django.conf import settings as django_settings


def default_before_proxy_func(request, json_data, request_headers):
    """预留钩子，可修改转发接口的header和body"""
    pass


# 统一转发前缀
PREFIX_SOPS = getattr(django_settings, "PREFIX_SOPS", "sops")

# AJAX接口转发前的
BEFORE_PROXY_FUNC = getattr(django_settings, "BEFORE_PROXY_FUNC", None)

# 设置被代理的标准运维插件AJAX请求地址，比如API网关的接口
SOPS_PROXY_URL = getattr(django_settings, "SOPS_PROXY_URL", "")

# 设置被代理的标准运维插件静态资源地址，比如标准运维的site_url或API网关接口
SOPS_SITE_URL = getattr(django_settings, "SOPS_SITE_URL", "")

ALLOW_ACCESS = getattr(django_settings, "SOPS_ALLOW_ACCESS", [])

BK_ESB_PAAS_HOST = getattr(django_settings, "BK_IAM_ESB_PAAS_HOST", "")

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

import json
import requests
from django.conf import settings

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from revproxy.views import ProxyView

from sops_proxy.settings import (
    PREFIX_SOPS,
    BEFORE_PROXY_FUNC,
    SOPS_PROXY_URL,
    SOPS_SITE_URL,
    BK_ESB_PAAS_HOST,
)
from sops_proxy.utils import normalize_request_headers, get_django_response


def dispatch_static(request, path):
    """
    代理sops插件的静态资源相关接口
    """

    sops_path = path.replace("/{}".format(PREFIX_SOPS), "")
    sops_url = SOPS_SITE_URL + "/static/" + sops_path

    try:
        res = requests.get(sops_url, verify=False)
        return HttpResponse(
            content=res.content,
            status=res.status_code,
            content_type=res.headers._store["content-type"][1],
        )
    except Exception as e:
        return HttpResponse("dispatch_static exception: {}".format(e))


def dispatch_query(request, path):
    """
    代理sops插件相关接口
        url1: /pipeline/xxx
        url2: /api/v3/core/xxx
        client = get_client_by_request(request)
        return client.sops.dispatch_plugin_query(
            {'url': request.path, 'method': request.method, 'data': request.body}
        )
    """

    try:

        full_path = request.get_full_path()
        sops_path = full_path.replace(PREFIX_SOPS, "")
        request_headers = normalize_request_headers(request)

        try:
            request_data = json.loads(request.body)
        except Exception:
            request_data = {}

        json_data = {
            "url": sops_path,
            "method": request.method.lower(),
            "data": request_data,
        }

        # 转发前的预处理，可以在外部修改body和header
        BEFORE_PROXY_FUNC(request, json_data, request_headers)

        try:
            proxy_response = requests.post(
                url=SOPS_PROXY_URL,
                json=json_data,
                headers=request_headers,
            )

            return JsonResponse(proxy_response.json())

        except Exception as e:
            return JsonResponse(
                {
                    "result": False,
                    "message": "[{}]: dispatch_query post exception: {}".format(
                        path, e
                    ),
                }
            )

    except Exception as e:
        return JsonResponse(
            {
                "result": False,
                "message": "[{}]: dispatch_query self exception: {}".format(path, e),
            }
        )


class SopsProxy(ProxyView):
    upstream = SOPS_SITE_URL

    def build_form(self, form):
        # 如果是域名, 则替换
        return "{}o/bk_sops{}".format(settings.FRONTEND_URL, form.split(".com")[1])

    def process(self, response):
        try:
            content = json.loads(response.content)
            if "form" not in content:
                return response
            content["form"] = self.build_form(content["form"])
            return JsonResponse(content)
        except Exception:
            return response

    def dispatch(self, request, path):
        self.request_headers = self.get_request_headers()

        redirect_to = self._format_path_to_redirect(request)
        if redirect_to:
            return redirect(redirect_to)

        proxy_response = self._created_proxy_response(request, path)

        self._replace_host_on_redirect_location(request, proxy_response)
        self._set_content_type(request, proxy_response)

        response = get_django_response(
            proxy_response, strict_cookies=self.strict_cookies
        )

        self.log.debug("RESPONSE RETURNED: %s", response)

        if settings.RUN_VER == "ieod":
            if path.startswith("api/v3/component/"):
                response = self.process(response)
            elif path.startswith("api/v3/variable/"):
                response = self.process(response)
        return response


class UserManageProxy(ProxyView):
    upstream = BK_ESB_PAAS_HOST

    def dispatch(self, request, path):
        path = "api/c/compapi/v2/usermanage/fs_list_users/"
        path = self.get_quoted_path(path)

        request_url = self.get_upstream(path) + path
        print("proxyrequest URL: %s", request_url)

        response = super(UserManageProxy, self).dispatch(request, path)

        print("proxyRESPONSE RETURNED: %s" % getattr(response, "content", "unknown"))
        return response

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

import base64
import os
import pstats
import time
from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from pyinstrument import Profiler

from common.log import logger
from common.mymako import render_mako_context
from itsm.component.constants import EXEMPT_HTTPS_REDIRECT
from itsm.iadmin.contants import SERVICE_SWITCH
from itsm.iadmin.models import SystemSettings
from itsm.auth_iam.utils import IamRequest

try:
    import cProfile
except ImportError:
    import profile  # noqa

User = get_user_model()


class ProfilerMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.profiler = None

    def __call__(self, request):
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, "process_response"):
            response = self.process_response(request, response)
        return response

    def can(self, request):
        if settings.PROFILER["enable"]:
            request_paths = settings.PROFILER.get("request_paths", [])
            if not request_paths:
                return True
            for path in request_paths:
                if path["path"] == request.path and request.method in path["method"]:
                    return True

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if self.can(request):
            self.profiler = cProfile.Profile()
            self.profiler.enable()

    def process_response(self, request, response):
        if self.can(request):
            self.profiler.disable()

            s = StringIO()

            sortby = settings.PROFILER.get("sort", "time")
            count = settings.PROFILER.get("count", None)
            outputs = settings.PROFILER.get("output", ["console"])

            pstats.Stats(self.profiler, stream=s).sort_stats(sortby).print_stats(count)
            for output in outputs:
                if output == "console":
                    print(s.getvalue())

                if output == "file":
                    file_location = settings.PROFILER.get("file_location", "profiles")
                    if not os.path.exists(file_location):
                        os.mkdir(file_location)
                    file_loc = os.path.join(
                        file_location,
                        "%s%s-profile%s.log"
                        % (
                            request.method,
                            request.path.replace("/", "-"),
                            int(time.time()),
                        ),
                    )
                    with open(file_loc, "a+") as file:
                        file.write("request path {}".format(request.path))
                        for counter in s.getvalue().split("\n"):
                            if (
                                "django/db/models/" in counter
                                or "pymysql/connections.py" in counter
                                or "site-packages" in counter
                            ):
                                continue

                            file.write("{}\n".format(counter))
                        file.close()
        return response


class InstrumentProfilerMiddleware(ProfilerMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if self.can(request):
            self.profiler = Profiler()
            self.profiler.start()

    def process_response(self, request, response):
        if not (self.can(request) and self.profiler):
            return response
        self.profiler.stop()
        outputs = settings.PROFILER.get("output", ["console"])
        file_location = settings.PROFILER.get("file_location", "profiles")
        if not os.path.exists(file_location):
            os.mkdir(file_location)

        for output in outputs:
            output_text = self.profiler.output_html()
            if output == "console":
                print(output_text)

            if output == "file":
                file_loc = os.path.join(
                    file_location,
                    "%s%s-profile%s.html"
                    % (
                        request.method,
                        request.path.replace("/", "-"),
                        int(time.time()),
                    ),
                )
                with open(file_loc, "a+") as file:
                    try:
                        file.write(output_text)
                    except BaseException:
                        pass
                    finally:
                        file.close()
        if getattr(settings, "PYINSTRUMENT_URL_ARGUMENT", "profile") in request.GET:
            return HttpResponse(output_text)
        return response


class ApiIgnoreCheck(MiddlewareMixin):
    def process_request(self, request):
        if (
            request.path.find("/api/ticket/comments/get_comment") >= 0
            or request.path.find("/api/ticket/comments/post_comment") >= 0
            or request.path.find("/api/ticket/operational/get_tickets") >= 0
            or request.path.find("/api/ticket/operational/comments") >= 0
            or request.path.find("/api/ticket/operational/workflows") >= 0
            or request.path.find("/api/ticket/receipts/get_ticket_log") >= 0
            or request.path.find("/openapi/") >= 0
        ):
            setattr(request, "_dont_enforce_csrf_checks", True)
            setattr(request, "_login_exempt", True)

        return None

    def process_view(self, request, view, args, kwargs):
        """process_view."""
        if getattr(request, "_login_exempt", False):
            setattr(view, "login_exempt", True)
        return None


class ServiceSwitchCheck(MiddlewareMixin):
    """
    手动关闭服务中间件，需要到admin里设置key='SERVICE_SWITCH'这条数据的value
    'on' 为开启服务
    'off' 为关闭服务
    """

    def process_view(self, request, view, args, kwargs):
        """process_view."""

        try:
            if SystemSettings.objects.get(key=SERVICE_SWITCH).value != "on":
                return render_mako_context(request, "close_service.html", {})
        except SystemSettings.DoesNotExist:
            return None

        return None


class NginxAuthProxy(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        """process_view."""

        forwarded_user = request.META.get("HTTP_X_FORWARDED_USER")
        forwarded_auth = request.META.get("HTTP_AUTHORIZATION")

        if forwarded_user and forwarded_auth:
            try:
                auth_infos = forwarded_auth.split()
                if auth_infos[0] != "Basic":
                    return None

                username, password = base64.b64decode(auth_infos[1]).decode().split(":")

                # simple validate
                user = User.objects.get(username=forwarded_user)
                if user.username == username:
                    setattr(request, "user", user)
                    setattr(view, "login_exempt", True)
            except BaseException:
                return None

        return None


class WikiIamAuthMiddleware(MiddlewareMixin):
    """
    设置用户的知识管理员权限
    """

    def process_view(self, request, view, args, kwargs):
        """process_view."""
        if request.user.username and "/wiki/" in request.path:
            apply_actions = ["knowledge_manage"]
            iam_client = IamRequest(request)
            auth_actions = iam_client.resource_multi_actions_allowed(apply_actions, [])
            request.user.set_property(
                "is_wiki_superuser", 1 if auth_actions.get("knowledge_manage") else 0
            )


class HttpResponseIndexRedirect(HttpResponseRedirect):
    def __init__(self, redirect_to, *args, **kwargs):
        super(HttpResponseIndexRedirect, self).__init__(redirect_to, *args, **kwargs)
        self["Location"] = os.path.join(
            settings.WEIXIN_APP_EXTERNAL_HOST, redirect_to.lstrip("/")
        )


class HttpsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if settings.RUN_VER == "ieod":
            # 对于openapi 跳转豁免
            if request.path.startswith(EXEMPT_HTTPS_REDIRECT):
                return None

            # 如果发现不是woa过来的域名
            if (
                settings.WEIXIN_APP_EXTERNAL_HOST
                and settings.WEIXIN_APP_EXTERNAL_HOST.find(request.get_host()) == -1
            ):
                # 如果 host的值和HTTP_REFERER一致，则跳转
                # 如果是从开发者中心中出来的，此时有HTTP_REFERER
                if (
                    "HTTP_REFERER" not in request.META
                    or request.get_host() in request.META.get("HTTP_REFERER", "")
                ):
                    logger.info("执行跳转: request.path = {}".format(request.path))
                    return HttpResponseIndexRedirect(request.path)

            if not request.is_secure():
                return HttpResponseIndexRedirect(request.path)

        return None

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

import os
import traceback
from django.conf import settings

from config import APP_ID, APP_TOKEN, RUN_VER
from requests.exceptions import ReadTimeout
from common.log import logger
from itsm.component.constants import ResponseCodeStatus
from itsm.component.utils.sandbox import map_data
from itsm.component.apigw.base import APIResource


_BK_API_URL_TMPL = getattr(settings, "BK_API_URL_TMPL", os.environ.get("BK_API_URL_TMPL", ""))
_BK_APIGATEWAY_BASE_URL = _BK_API_URL_TMPL.replace("{api_name}", "") if _BK_API_URL_TMPL else ""


class BkApigw(APIResource):
    """
    蓝鲸 API 网关（bk-apigateway）接口基类
    base_url 从 BK_API_URL_TMPL 环境变量中提取，格式：
        https://bkapi.sg.bk2game.com/api/{api_name}
    替换 {api_name} 为 bk-apigateway 后得到 base_url
    """

    base_url = _BK_APIGATEWAY_BASE_URL
    module_name = "bk-apigateway"

    @property
    def label(self):
        return self.__doc__

    @property
    def action(self):
        raise NotImplementedError

    @property
    def method(self):
        raise NotImplementedError

    def __call__(self, request_data):
        # bk-apigateway 接口不需要 username，直接发起请求
        return self.perform_request(request_data)

    def perform_request(self, request_data):
        """
        发起 http 请求，使用 APP_ID/APP_TOKEN 进行认证
        """
        from config import APP_ID, APP_TOKEN
        import requests
        from requests.exceptions import ReadTimeout
        from itsm.component.exceptions import RemoteCallError
        from common.log import logger

        request_url = self.get_request_url(request_data)
        headers = {
            "X-Bkapi-Authorization": '{"bk_app_code": "%s", "bk_app_secret": "%s"}' % (APP_ID, APP_TOKEN),
            "Content-Type": "application/json",
        }

        try:
            if self.method == "GET":
                result = self.session.get(
                    url=request_url,
                    params=request_data,
                    headers=headers,
                    verify=False,
                    timeout=self.TIMEOUT,
                )
            else:
                result = self.session.post(
                    url=request_url,
                    json=request_data,
                    headers=headers,
                    verify=False,
                    timeout=self.TIMEOUT,
                )
        except ReadTimeout:
            raise RemoteCallError("{}接口返回结果超时".format(request_url))

        try:
            result.raise_for_status()
        except Exception as e:
            logger.exception("【模块：%s】请求 bk-apigateway 错误：%s，请求url: %s" % (self.module_name, e, request_url))
            raise RemoteCallError("{} 调用失败: {}".format(request_url, str(e)))

        result_json = result.json()

        if not self.is_result_success(result_json):
            raise RemoteCallError("{} 返回结果错误: {}".format(request_url, result_json))

        return self.handle_response(result_json)

    def is_result_success(self, response_data):
        return response_data.get("code", -1) == 0

    def handle_response(self, response_data):
        return response_data.get("data", [])


class GetApis(BkApigw):
    """
    获取网关 API 列表
    GET /prod/api/v1/apis/
    """

    action = "/prod/api/v1/apis/"
    method = "GET"

    def __call__(self, request_data):
        from common.log import logger
        try:
            return self.perform_request(request_data)
        except Exception as e:
            logger.error("获取网关 API 列表失败: %s" % str(e))
            return []


class GetReleasedResources(BkApigw):
    """
    获取网关已发布环境的资源列表
    GET /{stage_name}/api/v1/apis/{api_name}/released/stages/{stage_name}/resources/
    """

    method = "GET"

    @property
    def action(self):
        from django.conf import settings
        stage_name = "prod" if getattr(settings, "RUN_MODE", "") == "PRODUCT" else "stag"
        return "/%s/api/v1/apis/{api_name}/released/stages/%s/resources/" % (stage_name, stage_name)

    def get_request_url(self, request_data):
        api_name = request_data.pop("api_name", "")
        url = self.base_url + self.action.format(api_name=api_name)
        return url

    def __call__(self, request_data):
        from common.log import logger
        try:
            return self.perform_request(request_data)
        except Exception as e:
            logger.error("获取网关已发布环境资源列表失败: %s" % str(e))
            return []


get_apis = GetApis()
get_released_resources = GetReleasedResources()


class BkApigwComponent(object):
    TIMEOUT = 60

    def __init__(self):
        import requests as _requests
        self.session = _requests.session()

    def _build_url(self, api_name, path):
        if not api_name and path:
            trailing_slash = "/" if path.endswith("/") else ""
            parts = path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "api":
                api_name = parts[1]
                path = "/" + "/".join(parts[2:]) + trailing_slash
        base = _BK_API_URL_TMPL.replace("{api_name}", api_name) if _BK_API_URL_TMPL else ""
        return base.rstrip("/") + "/" + path.lstrip("/")

    def http(self, config):
        """
        发起 API 网关请求
        """
        path = config.get("path", "")
        method = (config.get("method") or "POST").upper()
        api_name = config.get("api_name", "")
        query_params = dict(config.get("query_params") or {})
        path_params = dict(config.get("path_params") or {})
        map_code = config.get("map_code")
        before_req = config.get("before_req")

        # 获取用户身份和 token：优先从 query_params 中取，其次从请求上下文中取
        remote_user = (
            config.get("__remote_user__")
            or query_params.pop("__remote_user__", None)
        )
        
        bk_token = None
        access_token = None
        try:
            from blueapps.utils import get_request
            request_object = get_request()
            if not remote_user:
                remote_user = getattr(request_object.user, "username", None)
            # open 环境从 Cookie 中取 bk_token
            bk_token = request_object.COOKIES.get("bk_token", "")
        except Exception:
            pass
        
        if remote_user:
            try:
                import bkoauth
                access_token_obj = bkoauth.get_access_token_by_user(remote_user)
                access_token = access_token_obj.access_token
            except Exception:
                logger.warning("[BkApigwComponent] 获取 access_token 失败，user={}，降级使用 bk_token/bk_username".format(remote_user))
        
        # 优先用专门的 path_params 替换路径占位符
        if path_params and path:
            for key, value in path_params.items():
                placeholder = "{%s}" % key
                if placeholder in path:
                    path = path.replace(placeholder, str(value))

        if query_params and path:
            for key in list(query_params.keys()):
                placeholder = "{%s}" % key
                if placeholder in path:
                    path = path.replace(placeholder, str(query_params.pop(key)))

        if before_req:
            try:
                query_params = map_data(before_req, query_params, "query_params")
            except Exception:
                return {
                    "result": False,
                    "code": ResponseCodeStatus.FAILED,
                    "message": traceback.format_exc().split("\n")[-2],
                    "data": {},
                }

        request_url = self._build_url(api_name, path)
        # 根据环境构造认证信息：open 环境用 bk_token，ieod 环境用 bk_username
        auth_info = {"bk_app_code": APP_ID, "bk_app_secret": APP_TOKEN}
        if RUN_VER == "ieod":
            if access_token:
                auth_info["access_token"] = access_token
            elif remote_user:
                auth_info["bk_username"] = remote_user
        else:
            # open 环境：优先用 bk_token，没有则降级用 bk_username
            if access_token:
                auth_info["access_token"] = access_token
            elif bk_token:
                auth_info["bk_token"] = bk_token
        import json
        headers = {
            "X-Bkapi-Authorization": json.dumps(auth_info),
            "Content-Type": "application/json",
        }

        try:
            if method == "GET":
                result = self.session.get(
                    url=request_url,
                    params=query_params,
                    headers=headers,
                    verify=False,
                    timeout=self.TIMEOUT,
                )
            else:
                result = self.session.post(
                    url=request_url,
                    json=query_params,
                    headers=headers,
                    verify=False,
                    timeout=self.TIMEOUT,
                )
        except ReadTimeout:
            return {
                "result": False,
                "code": ResponseCodeStatus.FAILED,
                "message": "{}接口返回结果超时".format(request_url),
                "data": {},
            }
        except Exception as e:
            logger.error("[{}] response.Exception: {}".format(request_url, e))
            return {
                "result": False,
                "code": ResponseCodeStatus.FAILED,
                "message": str(e),
                "data": {},
            }

        try:
            result.raise_for_status()
        except Exception as e:
            logger.exception("【BkApigwComponent】请求错误：%s，请求url: %s" % (e, request_url))
            return {
                "result": False,
                "code": ResponseCodeStatus.FAILED,
                "message": "{} 调用失败: {}".format(request_url, str(e)),
                "data": {},
            }

        try:
            response = result.json()
        except Exception:
            return {
                "result": False,
                "code": ResponseCodeStatus.FAILED,
                "message": "not support invalid json response: {}".format(request_url),
                "data": {},
            }

        # 响应后处理
        if map_code:
            try:
                response = map_data(map_code, response, "response")
            except Exception:
                return {
                    "result": False,
                    "code": ResponseCodeStatus.FAILED,
                    "message": traceback.format_exc().split("\n")[-2],
                    "data": {},
                }

        # if response.get("result", False) and rsp_data:
        #     return {
        #         "result": True,
        #         "message": "success",
        #         "code": ResponseCodeStatus.OK,
        #         "data": self._handle_response(response, rsp_data),
        #     }

        return response

    def _handle_response(self, response, rsp_data):
        """提取 response 中的字段值，例如 rsp_data='data.info'"""
        import jmespath
        from common.log import logger

        data = {}
        for attr in rsp_data.split(","):
            if not attr:
                continue
            try:
                data[attr] = jmespath.search(attr, response)
            except AttributeError as e:
                logger.warning("handle_response attribute_error[{}]: {}".format(attr, e))
                data[attr] = ""
        return data


bk_apigw = BkApigwComponent()

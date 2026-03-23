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

from django.conf import settings

from itsm.component.apigw.base import APIResource

# 从 BK_API_URL_TMPL 中提取 base_url
# BK_API_URL_TMPL 格式：https://bkapi.sg.bk2game.com/api/{api_name}
# bk-apigateway 对应的 base_url：https://bkapi.sg.bk2game.com/api/bk-apigateway
_BK_API_URL_TMPL = getattr(settings, "BK_API_URL_TMPL", os.environ.get("BK_API_URL_TMPL", ""))
_BK_APIGATEWAY_BASE_URL = _BK_API_URL_TMPL.replace("{api_name}", "bk-apigateway") if _BK_API_URL_TMPL else ""


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

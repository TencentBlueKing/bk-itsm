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

import logging

import requests
from requests.exceptions import HTTPError, ReadTimeout
from itsm.component.exceptions import RemoteCallError

logger = logging.getLogger(__name__)


class APIResource:
    """
    API类型的Resource
    """

    TIMEOUT = 60

    @property
    def base_url(self):
        """
        api gateway 基本url生成规则
        """
        raise NotImplementedError

    @property
    def module_name(self):
        """
        在apigw中的模块名
        """
        raise NotImplementedError

    @property
    def action(self):
        """
        url的后缀，通常是指定特定资源
        """
        raise NotImplementedError

    @property
    def method(self):
        """
        请求方法，仅支持GET或POST
        """
        raise NotImplementedError

    def __init__(self):
        self.method = self.method.upper()
        self.session = requests.session()
        self.user = ""

    def __call__(self, request_data):
        self.user = request_data.pop("username")
        return self.perform_request(request_data)

    @property
    def access_token(self):

        try:
            import bkoauth

            # 新的access_token，会自动根据refresh_token刷新
            access_token_obj = bkoauth.get_access_token_by_user(self.user)
            access_token = access_token_obj.access_token
        except Exception:
            logger.exception(u"根据user（%s）获取access_token失败，请检查 bkoauth 配置" % self.user)
            # raise Exception(u"根据user（%s）获取access_token失败，请检查 bkoauth 配置" % self.user)
            raise Exception(u"根据user（%s）获取access_token失败，请检查 bkoauth 配置" % self.user)
        return access_token

    def perform_request(self, request_data):
        """
        发起http请求
        """
        request_url = self.get_request_url(request_data)
        params = {"access_token": self.access_token}
        try:
            if self.method == "GET":
                params.update(request_data)
                result = self.session.get(url=request_url, params=params, verify=False, timeout=self.TIMEOUT)
            else:
                headers = {"X-DEVOPS-UID": self.user}
                result = self.session.post(
                    url=request_url,
                    params=params,
                    verify=False,
                    timeout=self.TIMEOUT,
                    json=request_data,
                    headers=headers,
                )
        except ReadTimeout:
            raise RemoteCallError("{}接口返回结果超时".format(request_url))

        try:
            result.raise_for_status()
        except HTTPError as e:
            logger.exception("【模块：%s】请求APIGW错误：%s，请求url: %s " % (self.module_name, e, request_url))
            raise RemoteCallError("{} 调用失败:{}".format(request_url, str(e.response.content)))

        result_json = result.json()

        if not self.is_result_success(result_json):
            raise RemoteCallError("{} 返回结果错误:{}".format(request_url, result_json))

        response_data = self.handle_response(result_json)

        return response_data

    @property
    def label(self):
        return ""

    def get_request_url(self, request_data):
        """
        获取最终请求的url，也可以由子类进行重写
        """
        return self.base_url.rstrip("/") + "/" + self.action.lstrip("/").format(**request_data)

    def is_result_success(self, response_data):
        return True

    def handle_response(self, response_data):
        return response_data.get("data")

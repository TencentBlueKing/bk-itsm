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

from abc import abstractmethod

from json import JSONDecodeError

import urllib
import traceback
import requests

from django.conf import settings

from config import APP_ID, APP_TOKEN, RUN_VER

from blueapps.utils import get_request
from common.log import logger
from itsm.component.constants import ResponseCodeStatus
from itsm.component.utils.auth import get_tapd_oauth_url
from itsm.component.utils.sandbox import map_data
from itsm.component.utils.bk_bunch import Bunch, bunchify, unbunchify  # noqa


class BaseClient(object):
    @abstractmethod
    def build_absolute_url(self, path, domain=None):
        raise NotImplementedError

    @abstractmethod
    def get_client(self, data):
        raise NotImplementedError

    def request(self, method, path, data, domain=None, **kwargs):

        try:
            request_object = get_request()
            data["__remote_user__"] = getattr(
                request_object.user, "username", settings.SYSTEM_CALL_USER
            )
        except BaseException:
            pass

        client = self.get_client(data)
        url = self.build_absolute_url(path, domain)

        # 根据__env__强制取消测试环境
        if data.pop("__env__", None) == "product":
            client.set_use_test_env(False)

        api_auth = data.pop("api_auth", None)
        if api_auth:
            kwargs.update({"auth": api_auth})

        # 对额外添加的header进行处理
        origin_headers = kwargs.get("headers", {})
        headers = data.pop("headers", {})
        origin_headers.update(headers)
        kwargs["headers"] = origin_headers

        if method == "POST":
            if data.get("content_type") == "text":
                # 发送格式为文本的时候，直接用requests发送请求
                res = self.raw_post_request(url, data=data.get("raw", ""), **kwargs)
            else:
                res = client.request("POST", url, data=data, **kwargs)
        else:
            res = client.request("GET", url, params=data, **kwargs)

        if not res:
            message = "empty response: {}, status code ={}, resp content = {}".format(
                url, res.status_code, res.content
            )
            # 获取tapd授权链接
            if settings.ITSM_TAPD_APIGW and settings.ITSM_TAPD_APIGW in url:
                workspace_id = data.get("workspace_id", "")
                message = get_tapd_oauth_url(workspace_id)
            return {
                "result": False,
                "message": message,
                "data": {},
            }

        try:
            return res.json()
        except JSONDecodeError:
            logger.warning("[{}]: JSONDecodeError".format(url))
            return {
                "result": False,
                "message": "not support invalid json response: {}".format(url),
                "data": {},
            }

    @staticmethod
    def raw_post_request(url, data, **kwargs):
        """
        支持原生的text请求方式
        :param url: 请求链接
        :param data: 请求数据
        :param kwargs: 其他参数
        :return:
        """

        return requests.request(
            "POST",
            url,
            data=data,
            verify=False,
            timeout=20,
            headers=kwargs.get("headers"),
            **kwargs
        )


class OpenClient(BaseClient):
    from blueking.component.open import conf
    from blueking.component.open.shortcuts import get_client_by_user

    domain = conf.COMPONENT_SYSTEM_HOST

    @classmethod
    def build_absolute_url(cls, path, domain=None):
        system_domain = domain if domain else cls.domain
        return urllib.parse.urljoin(system_domain, path)

    @classmethod
    def get_client(cls, data):
        # 支持从外部指定请求所用的用户身份
        if data.get("__remote_user__"):
            client = cls.get_client_by_user(data.pop("__remote_user__"))
        else:
            client = cls.get_client_by_user(settings.SYSTEM_CALL_USER)

        return client


class IeodClient(BaseClient):
    try:
        from blueking.component.ieod import conf
        from blueking.component.ieod.shortcuts import get_client_by_user

        domain = conf.COMPONENT_SYSTEM_HOST
    except Exception:
        pass

    @classmethod
    def build_absolute_url(cls, path, domain=None):
        system_domain = domain if domain else cls.domain
        return urllib.parse.urljoin(system_domain, path)

    @classmethod
    def get_common_args(self, username):
        try:
            import bkoauth

            # 新的access_token，会自动根据refresh_token刷新
            access_token_obj = bkoauth.get_access_token_by_user(username)
            access_token = access_token_obj.access_token
            common_args = {"access_token": access_token}
            logger.info("[IeodClient] 用户access_token获取成功")
            return common_args
        except Exception:
            logger.info("根据用户获取access_token 失败, username={}".format(username))
            return {}

    @classmethod
    def get_client(cls, data):
        # 支持从外部指定请求所用的用户身份
        if data.get("__remote_user__"):
            user = data.pop("__remote_user__")
            common_args = cls.get_common_args(user)
            logger.info("[IeodClient] execute, user={}".format(user))
            client = cls.get_client_by_user(user, **common_args)
        else:
            client = cls.get_client_by_user(settings.SYSTEM_CALL_USER)

        return client


ENV_MAP = {
    "open": {"client": OpenClient},
    "ieod": {"client": IeodClient},
}


class BkComponent(object):
    def __init__(self, app_code, app_secret, ver="open"):
        self.app_code = app_code
        self.app_secret = app_secret
        self._conf = ENV_MAP[ver]
        self.client = self._conf["client"]()

    def http(self, config):

        # post.body or get.query_params
        query_params = config.get("query_params")
        path = config.get("path")
        method = config.get("method")
        system_domain = config.get("system_domain")
        map_code = config.get("map_code")
        before_req = config.get("before_req")
        rsp_data = config.get("rsp_data")
        kwargs = {}

        # 请求参数预处理
        if before_req:
            try:
                query_params = map_data(before_req, query_params, "query_params")
            except Exception:
                return {
                    "result": False,
                    "message": traceback.format_exc().split("\n")[-2],
                    "data": {},
                }

        try:
            response = self.client.request(
                method, path, query_params, system_domain, **kwargs
            )
        except Exception as e:
            logger.error("[{}] response.Exception: {}".format(path, e))
            return {
                "result": False,
                "message": str(e),
                "data": {},
            }

        # 返回结果后处理
        if map_code:
            try:
                response = map_data(map_code, response, "response")
            except Exception:
                return {
                    "result": False,
                    "message": traceback.format_exc().split("\n")[-2],
                    "data": {},
                }

        if response.get("result", False) and rsp_data:
            return {
                "result": True,
                "message": "success",
                "code": ResponseCodeStatus.OK,
                "data": self.handle_response(response, rsp_data),
            }

        return response

    def handle_response(self, response, rsp_data):
        """提取response中的字段值，比如
        rsp_data = 'data.info'
        return reponse['data']['info']
        """
        data = {}
        for attr in rsp_data.split(","):
            if not attr:
                continue

            try:
                handle_code = (
                    "handle_data = unbunchify(bunchify(response).{rsp_data})".format(
                        rsp_data=attr
                    )
                )
                exec(handle_code)
                data[attr] = locals()["handle_data"]
            except AttributeError as e:
                logger.warning(
                    "handle_response attribute_error[{}]: {}".format(attr, e)
                )
                data[attr] = ""

        return data


bk = BkComponent(APP_ID, APP_TOKEN, ver=RUN_VER)

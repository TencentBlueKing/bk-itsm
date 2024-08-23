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

# """Component API Client
# """

import json
import logging
import random
import time
import urllib.parse

import requests

from . import collections, conf
from .utils import get_signature

# shutdown urllib3's warning
try:
    requests.packages.urllib3.disable_warnings()
except BaseException:
    pass

logger = logging.getLogger("component")


class BaseComponentClient(object):
    """Base client class for component"""

    @classmethod
    def setup_components(cls, components):
        cls.available_collections = components

    def __init__(
        self,
        app_code=None,
        app_secret=None,
        common_args=None,
        use_test_env=False,
        language=None,
        bk_app_code=None,
        bk_app_secret=None,
    ):
        """
        :param str app_code: App code to use
        :param str app_secret: App secret to use
        :param dict common_args: Args that will apply to every request
        :param bool use_test_env: whether use test version of components
        """
        self.app_code = bk_app_code or app_code or conf.APP_CODE
        self.app_secret = bk_app_secret or app_secret or conf.SECRET_KEY
        self.bk_api_ver = conf.DEFAULT_BK_API_VER
        self.common_args = common_args or {}
        self._cached_collections = {}
        self.use_test_env = use_test_env
        self.language = language or self.get_cur_language()

    def set_use_test_env(self, use_test_env):
        """Change the value of use_test_env

        :param bool use_test_env: whether use test version of components
        """
        self.use_test_env = use_test_env

    def set_language(self, language):
        self.language = language

    def get_cur_language(self):
        try:
            from django.utils import translation

            return translation.get_language()
        except BaseException:
            return None

    def set_bk_api_ver(self, bk_api_ver):
        self.bk_api_ver = bk_api_ver

    def get_bk_api_ver(self):
        return self.bk_api_ver

    def merge_params_data_with_common_args(
        self, method, params, data, enable_app_secret=False
    ):
        """get common args when request"""
        common_args = dict(bk_app_code=self.app_code, **self.common_args)
        if enable_app_secret:
            common_args["bk_app_secret"] = self.app_secret
        if method == "GET":
            _params = common_args.copy()
            _params.update(params or {})
            params = _params
        elif method == "POST":
            _data = common_args.copy()
            _data.update(data or {})
            data = json.dumps(_data)
        return params, data

    def build_auth_header(self, method, params, data, enable_app_secret=False):
        """build auth header"""

        def extract_auth_keys(source, auth_header):
            """process the case when auth key is in params or data"""

            return {
                key: source[key]
                for key in auth_header
                if key in source and source[key] is not None
            }

        auth_header = dict(bk_app_code=self.app_code, **self.common_args)
        if enable_app_secret:
            auth_header["bk_app_secret"] = self.app_secret
        if method == "GET":
            auth_header.update(extract_auth_keys(params, auth_header))
        elif method == "POST":
            auth_header.update(extract_auth_keys(data, auth_header))
        return auth_header

    def request(self, method, url, params=None, data=None, **kwargs):
        """Send request"""
        # determine whether access test environment of third-party system
        headers = kwargs.pop("headers", {})
        if self.use_test_env:
            headers["x-use-test-env"] = "1"
        if self.language:
            headers["blueking-language"] = self.language

        auth_header = self.build_auth_header(method, params, data, True)
        headers["X-Bkapi-Authorization"] = json.dumps(auth_header)

        logger.debug(
            "Calling %s %s with params=%s, data=%s, headers=%s",
            method,
            url,
            params,
            data,
            headers,
        )
        return requests.request(
            method,
            url,
            params=params,
            data=data,
            verify=False,
            timeout=20,
            headers=headers,
            **kwargs
        )

    def __getattr__(self, key):
        if key not in self.available_collections:
            return getattr(super(BaseComponentClient, self), key)

        if key not in self._cached_collections:
            collection = self.available_collections[key]
            self._cached_collections[key] = collection(self)
        return self._cached_collections[key]


class ComponentClientWithSignature(BaseComponentClient):
    """Client class for component with signature"""

    def request(self, method, url, params=None, data=None, **kwargs):
        """Send request, will add "signature" parameter."""
        # determine whether access test environment of third-party system
        headers = kwargs.pop("headers", {})
        if self.use_test_env:
            headers["x-use-test-env"] = "1"
        if self.language:
            headers["blueking-language"] = self.language

        params, data = self.merge_params_data_with_common_args(
            method, params, data, enable_app_secret=False
        )
        if method == "POST":
            params = {}

        url_path = urllib.parse.urlparse(url).path
        # signature always in GET params
        params.update(
            {
                "bk_timestamp": int(time.time()),
                "bk_nonce": random.randint(1, 2147483647),
            }
        )
        params["bk_signature"] = get_signature(
            method, url_path, self.app_secret, params=params, data=data
        )

        logger.debug("Calling %s %s with params=%s, data=%s", method, url, params, data)
        return requests.request(
            method,
            url,
            params=params,
            data=data,
            verify=False,
            headers=headers,
            **kwargs
        )


# 根据是否开启signature来判断使用的Client版本
if conf.CLIENT_ENABLE_SIGNATURE:
    ComponentClient = ComponentClientWithSignature
else:
    ComponentClient = BaseComponentClient

ComponentClient.setup_components(collections.AVAILABLE_COLLECTIONS)

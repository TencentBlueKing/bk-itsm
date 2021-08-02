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

from itsm.component.dlls.component import BaseComponentMeta
from itsm.component.exceptions import RpcAPIError
from itsm.postman.rpc.core.response import CompResponse


class BaseComponent(metaclass=BaseComponentMeta):
    """
    Base class for component
    """

    name = 'UNKNOWN'  # 显示名称
    code = 'unknown'  # 在rpc组件里唯一, API path: [POST] /api/postman/${code}/rpc_api/
    type = 'rpc'  # 组件类型

    # 如果定义一个Form，请求将会使用这个Form来验证输入参数的有效性
    Form = None

    def __init__(self, request):
        self.request = request
        self.response = CompResponse()
        self.form_data = {}

    def handle_request(self):
        if self.request.method not in ("GET", "POST", "RPC"):
            raise RpcAPIError("Request method error, please apply GET, POST or RPC request.")

        # "GET"方法
        if self.request.method == "GET":
            request_params = self.request.query_params

        # "POST"方法 or "RPC"方法
        else:
            request_params = self.request.data

        self.request.kwargs = request_params

    def handle(self):
        """
        All Component should override this class
        """
        pass

    def invoke(self):
        """
        调用组件
        """
        self.handle_request()
        self.validate_input()
        self.handle()
        self.validate_payload()
        return self.response.get_payload()

    def validate_input(self):
        """
        Validate the given input
        """
        if self.Form:
            self.form_data = self.Form(self.request.kwargs).get_cleaned_data_or_error()
            self.request.kwargs.update(self.form_data)

    def validate_payload(self):
        if not isinstance(self.response.payload, list):
            raise RpcAPIError("Result must be List Type")

        for item in self.response.payload:
            if isinstance(item, dict) and not all(k in item for k in ["key", "name"]):
                raise RpcAPIError("Each item must both contain key and name")

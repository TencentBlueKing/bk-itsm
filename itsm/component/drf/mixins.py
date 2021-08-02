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

from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from itsm.component.constants import ResponseCodeStatus
from itsm.component.utils.basic import dotted_name


class ApiGenericMixin(object):
    """API视图类通用函数"""

    # TODO 权限部分加载基类中
    permission_classes = ()

    def finalize_response(self, request, response, *args, **kwargs):
        """统一数据返回格式"""
        # 文件导出时response {HttpResponse}
        if not isinstance(response, Response):
            return response
        if response.data is None:
            response.data = {'result': True, 'code': ResponseCodeStatus.OK, 'message': 'success', 'data': []}
        elif isinstance(response.data, (list, tuple)):
            response.data = {
                'result': True,
                "code": ResponseCodeStatus.OK,
                "message": 'success',
                "data": response.data,
            }
        elif isinstance(response.data, dict) and not ("code" in response.data and "result" in response.data):
            response.data = {
                'result': True,
                "code": ResponseCodeStatus.OK,
                "message": 'success',
                "data": response.data,
            }
        if response.status_code == status.HTTP_204_NO_CONTENT and request.method == "DELETE":
            response.status_code = status.HTTP_200_OK

        return super(ApiGenericMixin, self).finalize_response(request, response, *args, **kwargs)


class PermissionApiGenericMixin(ApiGenericMixin):
    def finalize_response(self, request, response, *args, **kwargs):
        """接入权限中心中心的统一数据返回格式"""
        if not isinstance(response, Response):
            return response

        response_data = {
            "auth_meta": {
                "auth_resource": getattr(self.serializer_class.Meta.model, "auth_resource", {}),
                "auth_operations": getattr(self.serializer_class.Meta.model, "auth_operations", {}),
            }
        }

        if response.data is None:
            response.data = {'result': True, 'code': ResponseCodeStatus.OK, 'message': 'success', 'data': response_data}
        elif isinstance(response.data, (list, tuple)):
            response_data.update({"items": response.data})
            response.data = {
                'result': True,
                "code": ResponseCodeStatus.OK,
                "message": 'success',
                "data": response_data,
            }
        elif isinstance(response.data, dict):
            if not ("code" in response.data and "result" in response.data):
                response_data.update(response.data)
                response.data = {
                    'result': True,
                    "code": ResponseCodeStatus.OK,
                    "message": 'success',
                    "data": response_data,
                }
            else:
                response.data['data'].update(response_data)
        if response.status_code == status.HTTP_204_NO_CONTENT and request.method == "DELETE":
            response.status_code = status.HTTP_200_OK

        return super(PermissionApiGenericMixin, self).finalize_response(request, response, *args, **kwargs)


class AuthListModelMixin(ListModelMixin):
    """
    带权限的资源列表请求
    """

    def list(self, request, *args, **kwargs):
        response = super(AuthListModelMixin, self).list(request, *args, **kwargs)
        return self.auth_mixin(response)

    def auth_mixin(self, response):
        response_data = {
            "auth_meta": {
                "auth_resource": getattr(self.serializer_class.Meta.model, "auth_resource", {}),
                "auth_operations": getattr(self.serializer_class.Meta.model, "auth_operations", {}),
            }
        }
        if isinstance(response.data, list):
            response_data.update(code=ResponseCodeStatus.OK, message="success", data=response.data, result=True)

        elif isinstance(response.data, dict):
            response_data.update(response.data)
        response.data = response_data
        return response


class ApiGatewayMixin(object):
    """对外开放API返回格式统一
        错误码返回规范为数字：
            正确：0
            错误：39XXXXX
    """

    def finalize_response(self, request, response, *args, **kwargs):
        """统一数据返回格式"""

        if not isinstance(response, Response):
            return response

        if response.data is None:
            response.data = {'result': True, 'code': 0, 'message': 'success', 'data': []}
        elif isinstance(response.data, (list, tuple)):
            response.data = {
                'result': True,
                "code": 0,
                "message": 'success',
                "data": response.data,
            }
        elif isinstance(response.data, dict) and not ("code" in response.data and "result" in response.data):
            response.data = {
                'result': True,
                "code": 0,
                "message": 'success',
                "data": response.data,
            }

        return super(ApiGatewayMixin, self).finalize_response(request, response, *args, **kwargs)


class DynamicListModelMixin(object):
    """
    动态取消分页，动态修改返回字段
    说明：子类（xxModelViewset）的序列化类（xxSerializer）必须继承：DynamicFieldsModelSerializer
    否则会报错：TypeError: __init__() got an unexpected keyword argument 'fields'
    """

    def list(self, request, *args, **kwargs):
        serializer_kwargs = {}
        if request.query_params.get('scope') == 'shortcut':
            serializer_kwargs.update(fields=('id', 'name', 'key', 'desc', 'owners', 'creator', 'updated_by'))

        queryset = self.filter_queryset(self.get_queryset())

        if request.query_params.get("page_size"):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True, **serializer_kwargs)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, **serializer_kwargs)
        return Response(serializer.data)


class ObjectManagerMixin(object):
    def is_obj_manager(self, username):
        """新增和修改权限：创建人和负责人"""
        return username == self.creator or dotted_name(username) in self.owners

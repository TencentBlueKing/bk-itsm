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

import datetime
import json

from django.db.models import Q
from django.forms.forms import DeclarativeFieldsMetaclass
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from rest_framework.decorators import action
from rest_framework.response import Response

from common.log import logger
from itsm.component.constants import ResponseCodeStatus, PUBLIC_PROJECT_PROJECT_KEY
from itsm.component.dlls.component import ComponentLibrary
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.drf.mixins import DynamicListModelMixin
from itsm.component.drf.permissions import IamAuthProjectViewPermit
from itsm.component.esb.backend_component import bk
from itsm.component.exceptions import NotAllowedError, ParamError, RpcAPIError
from itsm.component.utils.client_backend_query import get_components, get_systems
from itsm.component.utils.misc import JsonEncoder
from itsm.postman.constants import RPC_CODE
from itsm.postman.models import RemoteApi, RemoteApiInstance, RemoteSystem
from itsm.postman.permissions import RemoteApiPermit
from itsm.postman.rpc.core.request import CompRequest
from itsm.postman.serializers import (
    ApiInstanceSerializer,
    RemoteApiSerializer,
    RemoteSystemSerializer,
)


class ModelViewSet(component_viewsets.ModelViewSet):
    """按需改造DRF默认的ModelViewSet类"""

    def perform_create(self, serializer):
        """创建时补充基础Model中的字段"""
        user = serializer.context.get("request").user
        username = getattr(user, "username", "guest")
        serializer.save(creator=username, updated_by=username)

    def perform_update(self, serializer):
        """更新时补充基础Model中的字段"""
        user = serializer.context.get("request").user
        username = getattr(user, "username", "guest")
        serializer.save(updated_by=username)


class ApiInstanceViewsSet(ModelViewSet):
    serializer_class = ApiInstanceSerializer
    queryset = RemoteApiInstance._objects.all()
    permission_classes = ()

    @action(detail=True, methods=["post", "get"])
    def field_choices(self, request, *args, **kwargs):
        kv_relation = request.data.pop("kv_relation", {})
        params = {"params_%s" % key: value for key, value in list(request.data.items())}

        instance = self.get_object()
        choices = instance.get_api_choice(kv_relation, params)

        return Response(choices)


class RemoteSystemViewSet(ModelViewSet):
    """系统设置视图"""

    serializer_class = RemoteSystemSerializer
    queryset = RemoteSystem.objects.all()
    permission_classes = (IamAuthProjectViewPermit,)
    pagination_class = None

    filter_fields = {
        "is_activated": ["exact"],
    }

    def list(self, request, *args, **kwargs):

        project_key = request.query_params.get(
            "project_key", PUBLIC_PROJECT_PROJECT_KEY
        )

        queryset = self.filter_queryset(self.get_queryset()).filter(
            project_key=project_key
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def all(self, request, *args, **kwargs):
        project_key = request.query_params.get(
            "project_key", PUBLIC_PROJECT_PROJECT_KEY
        )

        queryset = self.filter_queryset(self.get_queryset()).filter(
            Q(project_key=project_key) | Q(project_key=PUBLIC_PROJECT_PROJECT_KEY)
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def get_systems(self, request):
        """接入系统列表"""

        systems = get_systems()

        project_key = request.query_params.get("project_key", 0)

        data = []
        codes = set()

        # ESB接入的系统
        for sys in systems:
            data.append(
                {
                    "name": sys.get("label") or sys.get("name", ""),
                    "code": sys.get("name", ""),
                    "domain": sys.get("domain", ""),
                    "desc": sys.get("remark", ""),
                    "system_id": sys.get("id", 0),
                }
            )
            codes.add(sys.get("name"))

        # 自定义添加的系统
        for sys in self.queryset.exclude(code__in=codes, project_key=project_key):
            data.append(
                {
                    "name": sys.name,
                    "code": sys.code,
                    "domain": sys.domain,
                    "desc": sys.desc,
                    "system_id": sys.system_id,
                }
            )

        return Response(data)

    @action(detail=False, methods=["get"])
    def get_components(self, request):
        system_code = request.GET.get("system_code")
        components = get_components([system_code])
        return Response(components)


class RemoteApiViewSet(DynamicListModelMixin, ModelViewSet):
    """第三方系统API请求配置表"""

    serializer_class = RemoteApiSerializer
    queryset = RemoteApi.objects.all()
    permission_classes = (RemoteApiPermit,)

    filter_fields = {
        "is_activated": ["exact"],
    }

    def get_queryset(self):
        queryset = super(RemoteApiViewSet, self).get_queryset()

        key = self.request.query_params.get("key")
        if key:
            queryset = queryset.filter(Q(name__icontains=key) | Q(path__icontains=key))

        remote_system = self.request.query_params.get("remote_system")
        if remote_system:
            return queryset.filter(remote_system__id=remote_system)

        project_key = self.request.query_params.get("project_key")

        if project_key:
            public_remote_system_ids = RemoteSystem.objects.filter(
                project_key=project_key
            ).values_list("id", flat=True)
            return queryset.filter(remote_system__id__in=public_remote_system_ids)

        return queryset

    @action(detail=True, methods=["post"])
    def run_api(self, request, *args, **kwargs):
        api = self.get_object()
        if api.method == "POST":
            query_params = request.data.get("req_body", {})
        else:
            query_params = request.data.get("req_params", {})

        api_config = api.get_api_config(query_params)

        # overwrite map_code
        map_code = request.data.get("map_code", "")
        before_req = request.data.get("before_req", "")
        api_config.update(map_code=map_code, before_req=before_req)

        rsp = bk.http(config=api_config)

        # 多加一层是因为前端对返回的message有一个统一添加msg的逻辑（为了屏蔽返回差异），所以此处加一层包裹，前端取data里面的值
        return Response(
            {
                "result": True,
                "message": "success",
                "code": ResponseCodeStatus.OK,
                "data": rsp,
            }
        )

    @action(detail=False, methods=["post"])
    def batch_delete(self, request, *args, **kwargs):
        """批量删除操作
        TODO: 缺少负责人鉴权
        """

        id_list = [i for i in request.data.get("id").split(",") if i.isdigit()]

        will_deleted = self.queryset.filter(id__in=id_list)
        real_deleted = list(will_deleted.values_list("id", flat=True))
        will_deleted.delete()

        return Response(real_deleted)

    @action(detail=True, methods=["get"])
    def exports(self, request, pk=None):
        """
        导出Api接口
        """

        api = self.get_object()
        data = api.tag_data()

        response = HttpResponse(content_type="application/octet-stream; charset=utf-8")
        response[
            "Content-Disposition"
        ] = "attachment; filename=bk_itsm_api_{}_{}.json".format(
            api.func_name, datetime.datetime.now().strftime("%Y%m%d%H%M")
        )

        # 统一导入导出格式为列表数据
        response.write(json.dumps([data], cls=JsonEncoder, indent=2))

        return response

    @action(detail=True, methods=["post"])
    def imports(self, request, pk=None):
        """
        导入Api接口
        """
        if pk == "0":
            apis = []
            try:
                remote_system = request.data.get("remote_system", "0")
                data = json.loads(request.FILES.get("file").read())
            except ValueError:
                raise ParamError(_("文件格式有误，请提供从本系统导出的json文件"))

            for item in data:
                try:
                    item["remote_system_id"] = remote_system
                    api = RemoteApi.restore_api(item, request.user.username)
                    apis.append(api)
                except Exception as e:
                    logger.error("import workflow exception: %s" % e)

            return Response({"success": len(apis), "failed": len(data) - len(apis)})

        raise NotAllowedError(_("暂不支持当前操作"))


class RpcApiViewSet(component_viewsets.APIView):
    def get(self, request, *args, **kwargs):
        """获取rpc的API列表"""
        ret = []
        for code, component_cls in ComponentLibrary.components.get("rpc", {}).items():
            rpc_api = {"name": component_cls.name, "key": code, "req_params": []}
            # API传入参数
            if isinstance(component_cls.Form, DeclarativeFieldsMetaclass):
                for field_name, field in component_cls.Form.declared_fields.items():
                    rpc_api["req_params"].append(
                        {
                            "name": field_name,
                            "desc": field.label,
                            "sample": field.initial,
                            "is_necessary": field.required,
                        }
                    )
            ret.append(rpc_api)

        return Response(ret)

    def post(self, request, *args, **kwargs):
        """指定rpc的API, 获取返回结果"""
        if RPC_CODE not in request.data:
            raise RpcAPIError(_("【%s】为必需参数" % RPC_CODE))

        result, request_params = CompRequest.parse_params(request.data)
        # 构造参数不成功
        if not result:
            return Response(
                {
                    "result": False,
                    "code": ResponseCodeStatus.OK,
                    "message": "Render context error, see the log for details",
                    "data": [],
                }
            )

        request.data.update(**request_params)
        component_cls = ComponentLibrary.get_component_class(
            "rpc", request.data[RPC_CODE]
        )
        component_obj = component_cls(request)
        return Response(component_obj.invoke())

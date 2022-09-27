# -*- coding: utf-8 -*-
import json

import requests
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.decorators import custom_apigw_required
from itsm.component.drf import viewsets
from itsm.component.exceptions import GetCustomApiDataError
from itsm.openapi.base_service.serializers import (
    PostManSerializer,
    PostManRemoteApiSerializer,
)
from itsm.postman.models import RemoteSystem, RemoteApi


class PostManViewSet(viewsets.GenericViewSet):
    serializer_class = PostManSerializer

    @custom_apigw_required
    @action(detail=False, methods=["get"])
    def systems(self, request, *args, **kwargs):
        queryset = RemoteSystem.objects.filter(project_key="public")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @custom_apigw_required
    @action(detail=False, methods=["get"], serializer_class=PostManRemoteApiSerializer)
    def remote_api(self, request, *args, **kwargs):
        system_id = request.query_params.get("system_id")
        queryset = RemoteApi.objects.filter(remote_system_id=system_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @custom_apigw_required
    @action(detail=False, methods=["post"])
    def run_api(self, request, *args, **kwargs):
        config = request.data
        method = config.get("method", "GET")
        url = config.get("url", "")
        query_params = config.get("query_params", {})
        headers = config.get("headers", {})
        body = config.get("body", {})

        # 默认 增加 application/json 的json头
        headers.update({"Content-Type": "application/json"})
        # 如果自带了鉴权token，则不使用流程服务默认的选项
        if "x-bkapi-authorization" not in headers:
            auth_headers = {
                "bk_app_code": settings.APP_ID,
                "bk_app_secret": settings.APP_TOKEN,
                "bk_username": settings.SYSTEM_USE_API_ACCOUNT,
            }
            headers.update({"x-bkapi-authorization": json.dumps(auth_headers)})
        try:
            response = requests.request(
                method,
                url,
                data=json.dumps(body),
                params=query_params,
                headers=headers,
                timeout=10,
                verify=False,
            )
        except Exception as e:
            raise GetCustomApiDataError("请求错误，error={}".format(e))

        try:
            resp_data = response.json()
        except Exception as e:
            raise GetCustomApiDataError("请求失败，返回内容非Json，error={}".format(e))

        return Response(resp_data)

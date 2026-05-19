# -*- coding: utf-8 -*-
import json
from urllib.parse import urlparse

import requests
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.decorators import custom_apigw_required
from itsm.component.drf import viewsets
from itsm.component.exceptions import GetCustomApiDataError
from itsm.meta.services.context import ContextService
from itsm.openapi.base_service.serializers import (
    PostManSerializer,
    PostManRemoteApiSerializer,
)
from itsm.postman.models import RemoteSystem, RemoteApi


class PostManViewSet(viewsets.GenericViewSet):
    serializer_class = PostManSerializer
    ALLOWED_HOST_SUFFIXES_CONTEXT_KEY = "postman_run_api_allowed_host_suffixes"

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

        self.validate_run_api_url(url)

        headers.update({"Content-Type": "application/json"})
        if not headers.get("x-bkapi-authorization"):
            raise GetCustomApiDataError("请求失败，缺少 x-bkapi-authorization 请求头")
        try:
            response = requests.request(
                method,
                url,
                data=json.dumps(body),
                params=query_params,
                headers=headers,
                timeout=10,
                allow_redirects=False,
            )
        except Exception as e:
            raise GetCustomApiDataError("请求错误，error={}".format(e))

        try:
            resp_data = response.json()
        except Exception as e:
            raise GetCustomApiDataError("请求失败，返回内容非Json，error={}".format(e))

        return Response(resp_data)
    
    
    @classmethod
    def get_allowed_host_suffixes(cls):
        raw_value = (
            ContextService.get_context_value(cls.ALLOWED_HOST_SUFFIXES_CONTEXT_KEY) or ""
        )
        normalized_value = raw_value.replace("\n", ",").replace(";", ",")
        allowed_hosts = []

        for item in normalized_value.split(","):
            item = item.strip().lower().rstrip(".")
            if not item:
                continue
            allowed_hosts.append(item)

        return list(dict.fromkeys(allowed_hosts))

    @classmethod
    def is_allowed_hostname(cls, hostname):
        normalized_hostname = hostname.strip().lower().rstrip(".")
        allowed_hosts = cls.get_allowed_host_suffixes()
        if not allowed_hosts:
            raise GetCustomApiDataError("请求失败，未配置可访问的授权域名")

        for pattern in allowed_hosts:
            if pattern.startswith("*."):
                suffix = pattern[2:]
                if suffix and normalized_hostname.endswith("." + suffix):
                    return True
                continue

            if normalized_hostname == pattern:
                return True

        return False


    def validate_run_api_url(self, url):
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise GetCustomApiDataError("请求失败，URL 格式错误，error={}".format(e))

        if parsed.scheme not in ["http", "https"]:
            raise GetCustomApiDataError("请求失败，仅支持 http/https 协议")

        if not parsed.hostname:
            raise GetCustomApiDataError("请求失败，URL 缺少 hostname")

        if not self.is_allowed_hostname(parsed.hostname):
            raise GetCustomApiDataError(
                "请求失败，目标域名未被授权访问，hostname={}".format(parsed.hostname)
            )

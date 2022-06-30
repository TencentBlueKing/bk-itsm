# -*- coding: utf-8 -*-
from bkapi.bk_apigateway.client import Client
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response

from config.default import BK_APIGW_NAME
from itsm.component.decorators import custom_apigw_required
from itsm.component.drf import viewsets
from itsm.openapi.base_service.serializers import ApiGwSerializer


def grant(app_code, resource_names, stage):
    # 需提供网关地址 endpoint，环境 stage 默认为 prod
    client = Client(stage=stage, endpoint=settings.BK_API_URL_TMPL)
    # 根据需求，提供应用认证、用户认证信息
    client.update_bkapi_authorization(
        bk_app_code=settings.BK_APP_CODE,
        bk_app_secret=settings.BK_APP_SECRET,
        bk_username="admin",
    )
    # 发起请求，检查 response.raise_for_status()，返回 response.json() 数据
    params = {
        "target_app_code": app_code,
        "grant_dimension": "resource",
        "resource_names": resource_names,
    }
    path_params = {"api_name": BK_APIGW_NAME}
    try:
        result = client.api.grant_permissions(data=params, path_params=path_params)
    except Exception:
        return False
    return result["result"]


class ApiGwViewSet(viewsets.GenericViewSet):
    serializer_class = ApiGwSerializer

    @custom_apigw_required
    @action(detail=False, methods=["post"])
    def grant(self, request, *args, **kwargs):
        app_code = request.data.get("app_code")
        resource_names = request.data.get("resource_names")
        stage = request.data.get("stage", "prod")
        result = grant(app_code, resource_names, stage)
        return Response({"result": result})

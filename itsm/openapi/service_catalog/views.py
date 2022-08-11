# -*- coding: utf-8 -*-
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.constants import DEFAULT_PROJECT_PROJECT_KEY
from itsm.component.decorators import custom_apigw_required
from itsm.component.drf.mixins import ApiGatewayMixin
from itsm.component.drf import viewsets as component_viewsets
from itsm.openapi.decorators import catch_openapi_exception
from itsm.service.models import ServiceCatalog
from itsm.service.serializers import ServiceCatalogSerializer


class ServiceCatalogViewSet(ApiGatewayMixin, component_viewsets.ModelViewSet):
    serializer_class = ServiceCatalogSerializer
    queryset = ServiceCatalog.objects.filter(is_deleted=False).order_by(
        "-create_at", "level"
    )

    @custom_apigw_required
    @action(detail=False, methods=["get"])
    def tree_view(self, request):
        """目录树视图"""
        key = request.query_params.get("key", "")
        show_deleted = request.query_params.get("show_deleted") == "true"
        project_key = request.query_params.get(
            "project_key", DEFAULT_PROJECT_PROJECT_KEY
        )
        tree_data = ServiceCatalog.tree_data(request, key, show_deleted, project_key)
        return Response(tree_data)

    @custom_apigw_required
    @catch_openapi_exception
    def list(self, request, *args, **kwargs):
        return Response()

    @custom_apigw_required
    @catch_openapi_exception
    def destroy(self, request, *args, **kwargs):
        return Response()

    @custom_apigw_required
    @catch_openapi_exception
    def update(self, request, *args, **kwargs):
        return Response()

    @custom_apigw_required
    @catch_openapi_exception
    def create(self, request, *args, **kwargs):
        """
        {"parent__id":1,"name":"测试","desc":"","project_key":"0"}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

# -*- coding: utf-8 -*-
from blueapps.account.decorators import login_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.decorators import custom_apigw_required
from itsm.component.drf.mixins import ApiGatewayMixin
from itsm.component.drf import viewsets as component_viewsets
from itsm.openapi.base_service.serializers import OpenApiWorkflowVersionSerializer
from itsm.workflow.models import WorkflowVersion


@method_decorator(login_exempt, name="dispatch")
class WorkflowVersionViewSet(ApiGatewayMixin, component_viewsets.ReadOnlyModelViewSet):
    queryset = WorkflowVersion.objects.all().order_by("-create_at")
    serializer_class = OpenApiWorkflowVersionSerializer

    @custom_apigw_required
    def list(self, request, *args, **kwargs):
        return Response()

    @custom_apigw_required
    def retrieve(self, request, *args, **kwargs):
        return Response()

    @custom_apigw_required
    @action(detail=True, methods=["get"])
    def states(self, request, *args, **kwargs):
        instance = self.get_object()
        states = instance.states.values()
        return Response(list(states))

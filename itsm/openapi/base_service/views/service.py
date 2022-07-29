# -*- coding: utf-8 -*-
from blueapps.account.decorators import login_exempt
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.decorators import custom_apigw_required
from itsm.component.drf import viewsets
from itsm.openapi.base_service.serializers import OpenApiServiceSerializer
from itsm.service.models import Service
from itsm.service.serializers import ServiceConfigSerializer
from itsm.workflow.models import Workflow
from itsm.workflow.validators import WorkflowPipelineValidator


@method_decorator(login_exempt, name="dispatch")
class ServiceViewSet(viewsets.ModelViewSet):
    """服务项视图集合"""

    serializer_class = OpenApiServiceSerializer
    queryset = Service.objects.all()
    permission_free_actions = ["retrieve"]

    @custom_apigw_required
    def list(self, request, *args, **kwargs):
        return Response()

    @custom_apigw_required
    def retrieve(self, request, *args, **kwargs):
        return super(ServiceViewSet, self).retrieve(request, *args, **kwargs)

    @custom_apigw_required
    def update(self, request, *args, **kwargs):
        return super(ServiceViewSet, self).update(request, *args, **kwargs)

    @custom_apigw_required
    def create(self, request, *args, **kwargs):
        return super(ServiceViewSet, self).create(request, *args, **kwargs)

    @custom_apigw_required
    def destroy(self, request, *args, **kwargs):
        return super(ServiceViewSet, self).destroy(request, *args, **kwargs)

    def update_workflow_configs(self, workflow_id, workflow_config):
        workflow = Workflow.objects.filter(id=workflow_id).first()
        workflow.update_workflow_configs(workflow_config)
        return workflow

    @custom_apigw_required
    @action(detail=True, methods=["post"], permission_classes=())
    def deploy(self, request, *args, **kwargs):
        service = self.get_object()
        workflow = Workflow.objects.filter(id=service.workflow.workflow_id).first()
        service.workflow_id = workflow.create_version().id
        service.name = workflow.name
        service.is_valid = True
        service.save()
        return Response({"version_number": service.workflow_id})

    @custom_apigw_required
    @action(detail=True, methods=["post"], permission_classes=())
    def save_configs(self, request, *args, **kwargs):
        """
        {
            "can_ticket_agency": true,
            "display_role": 8,
            "display_type": "display_type",
            "workflow_config": {
                "is_auto_approve": true,
                "is_revocable": true,
                "revoke_config": {
                    "type": 1,
                    "state": 0
                },
                "notify": [
                    {
                        "name": "企业微信",
                        "type": "WEIXIN"
                    },
                    {
                        "name": "邮件",
                        "type": "EMAIL"
                    },
                    {
                        "name": "SMS短信",
                        "type": "SMS"
                    }
                ],
                "notify_freq": 0,
                "notify_rule": "ONCE",
                "is_supervise_needed": true,
                "supervise_type": "EMPTY",
                "supervisor": "",
                "owners":"",
            }
        }
        """
        service = self.get_object()
        serializer = ServiceConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        configs = serializer.validated_data
        workflow_config = configs["workflow_config"]
        workflow_id = service.workflow.workflow_id
        WorkflowPipelineValidator(Workflow.objects.get(id=workflow_id))()

        with transaction.atomic():
            self.update_workflow_configs(workflow_id, workflow_config)
            configs["workflow_id"] = service.workflow.id
            service.update_service_configs(configs)
        context = self.get_serializer_context()
        return Response(self.serializer_class(instance=service, context=context).data)

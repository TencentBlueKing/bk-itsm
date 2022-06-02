# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from itsm.component.decorators import apigw_required
from itsm.service.models import Service


@apigw_required
@require_GET
def services(request):
    service_list = Service.objects.all().values("id", "name")
    return JsonResponse(
        {
            "result": True,
            "data": [
                {
                    "service_id": service["id"],
                    "service_name": service["name"],
                }
                for service in service_list
            ],
        }
    )


@apigw_required
@require_GET
def service_fields(request):
    try:
        service = Service.objects.get(id=request.GET.get("service_id"))
    except Service.DoesNotExist:
        return JsonResponse({"result": False, "data": [], "message": "服务不存在"})
    fields = service.first_state_fields
    return JsonResponse(
        {
            "result": True,
            "data": [
                {
                    "key": field["key"],
                    "keyDisable": True,
                    "keyType": "input",
                }
                for field in fields
            ],
        }
    )

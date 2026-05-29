# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from itsm.component.decorators import apigw_required
from itsm.component.drf.permissions import IamAuthPermit
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
    # 1) 入参校验：service_id 必填且必须是合法整数，避免无意义查询直接抛 500
    raw_service_id = request.GET.get("service_id")
    if not raw_service_id:
        return JsonResponse(
            {"result": False, "data": [], "message": "service_id 不能为空"}
        )
    try:
        service_id = int(raw_service_id)
    except (TypeError, ValueError):
        return JsonResponse(
            {"result": False, "data": [], "message": "service_id 非法"}
        )

    # 2) 用 first() 而非 get()，与 IDOR 修复一并使用统一"未找到"响应，
    #    避免通过 DoesNotExist/异常体差异区分资源是否存在。
    service = Service.objects.filter(id=service_id).first()
    if not service:
        return JsonResponse({"result": False, "data": [], "message": "服务不存在"})

    # 3) IAM 校验：要求调用者对该 service 拥有 service_view 权限，
    #    防止通过遍历 service_id 任意拉取他人服务字段（IDOR）。
    if not IamAuthPermit().iam_auth(request, ["service_view"], service):
        return JsonResponse(
            {"result": False, "data": [], "message": "服务不存在"}
        )

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

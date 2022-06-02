# -*- coding: utf-8 -*-
from django.http import JsonResponse

from blueapps.account.decorators import login_exempt
from django.views.decorators.http import require_GET

from itsm.monitor.healthz.processor import metric


@require_GET
@login_exempt
def healthz(request):
    data = metric()
    return JsonResponse({"result": True, "data": data, "message": "OK"})


@require_GET
@login_exempt
def ping(request):
    return JsonResponse({"result": True, "data": None, "message": "pong"})

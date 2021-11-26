# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django_prometheus.exports import ExportToDjangoView

from blueapps.account.decorators import login_exempt
from django.views.decorators.http import require_GET


@require_GET
@login_exempt
def healthz(request):
    return JsonResponse({"result": True, "data": None, "message": "OK"})


@require_GET
@login_exempt
def metrics(request):
    return ExportToDjangoView(request)

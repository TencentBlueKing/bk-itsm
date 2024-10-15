# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import functools
import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.module_loading import import_string
from django.views.decorators.http import require_POST

from pipeline.engine.utils import ActionResult

from .handlers.pipeline_engine import PipelineEngineRequestHandler

ENGINE_REQUEST_HANDLERS = {"pipeline_engine": PipelineEngineRequestHandler}


def _ensure_return_json_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, dict):
            return JsonResponse(response)
        if isinstance(response, ActionResult):
            return JsonResponse(
                {"result": response.result, "message": response.message, "data": None})
        return response

    return wrapper


def _check_api_permission(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if getattr(settings, "PIPELINE_ENGINE_ADMIN_API_PERMISSION", None):
            try:
                perm_func = import_string(settings.PIPELINE_ENGINE_ADMIN_API_PERMISSION)
            except ImportError:
                return JsonResponse(
                    {
                        "result": False,
                        "message": "Pipeline engine admin permission function import error.",
                        "data": None,
                    }
                )
            if not perm_func(request, *args, **kwargs):
                return JsonResponse(
                    {
                        "result": False,
                        "message": "You have no permission to call pipeline engine admin api.",
                        "data": None,
                    }
                )
        return func(request, *args, **kwargs)

    return wrapper


@_check_api_permission
def render_index(request, *args, **kwargs):
    return render(request, "eri_admin_index.html",
                  {"BKAPP_CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME})


@require_POST
@_check_api_permission
@_ensure_return_json_response
def task_pause(request, engine_type, instance_id):
    """
    暂停任务
    """
    handler = ENGINE_REQUEST_HANDLERS[engine_type](request, "task_pause", instance_id)
    return handler.execute()


@require_POST
@_check_api_permission
@_ensure_return_json_response
def task_resume(request, engine_type, instance_id):
    handler = ENGINE_REQUEST_HANDLERS[engine_type](request, "task_resume", instance_id)
    return handler.execute()


@require_POST
@_check_api_permission
@_ensure_return_json_response
def task_revoke(request, engine_type, instance_id):
    handler = ENGINE_REQUEST_HANDLERS[engine_type](request, "task_revoke", instance_id)
    return handler.execute()


@require_POST
@_check_api_permission
@_ensure_return_json_response
def node_retry(request, engine_type, instance_id):
    inputs = json.loads(request.body).get("inputs")
    handler = ENGINE_REQUEST_HANDLERS[engine_type](request, "node_retry", instance_id)
    return handler.execute(inputs=inputs)


@require_POST
@_check_api_permission
@_ensure_return_json_response
def node_skip(request, engine_type, instance_id):
    handler = ENGINE_REQUEST_HANDLERS[engine_type](request, "node_skip", instance_id)
    return handler.execute()


@require_POST
@_check_api_permission
@_ensure_return_json_response
def node_callback(request, engine_type, instance_id):
    body = json.loads(request.body)
    data, version = body.get("data"), body.get("version")
    handler = ENGINE_REQUEST_HANDLERS[engine_type](request, "node_callback", instance_id)
    return handler.execute(data=data, version=version)


@require_POST
@_check_api_permission
@_ensure_return_json_response
def node_skip_exg(request, engine_type, instance_id):
    flow_id = json.loads(request.body).get("flow_id")
    handler = ENGINE_REQUEST_HANDLERS[engine_type](request, "node_skip_exg", instance_id)
    return handler.execute(flow_id=flow_id)


@require_POST
@_check_api_permission
@_ensure_return_json_response
def node_skip_cpg(request, engine_type, instance_id):
    body = json.loads(request.body)
    converge_gateway_id = body.get("converge_gateway_id")
    flow_ids = body.get("flow_ids")
    handler = ENGINE_REQUEST_HANDLERS[engine_type](request, "node_skip_cpg", instance_id)
    return handler.execute(flow_ids=flow_ids, converge_gateway_id=converge_gateway_id)


@require_POST
@_check_api_permission
@_ensure_return_json_response
def node_forced_fail(request, engine_type, instance_id):
    handler = ENGINE_REQUEST_HANDLERS[engine_type](request, "node_forced_fail", instance_id)
    return handler.execute()

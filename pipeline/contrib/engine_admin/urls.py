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
from django.urls import path, register_converter
from django.urls.converters import StringConverter

from . import views

API_VERSION = "v1"


class EngineConverter(StringConverter):
    regex = "pipeline_engine"


register_converter(EngineConverter, "engine")


urlpatterns = [
    path("", views.render_index),
    path(f"api/{API_VERSION}/<engine:engine_type>/task_pause/<str:instance_id>/", views.task_pause),
    path(f"api/{API_VERSION}/<engine:engine_type>/task_resume/<str:instance_id>/", views.task_resume),
    path(f"api/{API_VERSION}/<engine:engine_type>/task_revoke/<str:instance_id>/", views.task_revoke),
    path(f"api/{API_VERSION}/<engine:engine_type>/node_retry/<str:instance_id>/", views.node_retry),
    path(f"api/{API_VERSION}/<engine:engine_type>/node_skip/<str:instance_id>/", views.node_skip),
    path(f"api/{API_VERSION}/<engine:engine_type>/node_callback/<str:instance_id>/", views.node_callback),
    path(f"api/{API_VERSION}/<engine:engine_type>/node_skip_exg/<str:instance_id>/", views.node_skip_exg),
    path(f"api/{API_VERSION}/<engine:engine_type>/node_skip_cpg/<str:instance_id>/", views.node_skip_cpg),
    path(f"api/{API_VERSION}/<engine:engine_type>/node_forced_fail/<str:instance_id>/", views.node_forced_fail),
]

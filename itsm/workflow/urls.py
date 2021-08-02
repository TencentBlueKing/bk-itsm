# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from rest_framework.routers import DefaultRouter

from .views import (
    FieldViewSet,
    StateViewSet,
    TableViewSet,
    TemplateFieldViewSet,
    TransitionTemplateViewSet,
    TransitionViewSet,
    TriggerViewSet,
    WorkflowVersionViewSet,
    WorkflowViewSet,
    TaskSchemaViewSet,
    TaskFieldSchemaViewSet,
)
from .views_test import TestViewSet

routers = DefaultRouter(trailing_slash=True)

routers.register(r'templates', WorkflowViewSet, basename="workflow_template")
routers.register(r'versions', WorkflowVersionViewSet, basename="workflow_version")
routers.register(r'states', StateViewSet, basename="state")
routers.register(r'transitions', TransitionViewSet, basename="transition")
routers.register(r'fields', FieldViewSet, basename="field")
routers.register(r'template_fields', TemplateFieldViewSet, basename="template_fields")
routers.register(r'tests', TestViewSet, basename='test')
routers.register(r'transition_template', TransitionTemplateViewSet, basename='transition_template')
routers.register(r'tables', TableViewSet, basename='tables')
routers.register(r'triggers', TriggerViewSet, basename='triggers')
routers.register(r'task_schemas', TaskSchemaViewSet, basename='task_schemas')
routers.register(r'task_field_schemas', TaskFieldSchemaViewSet, basename='task_field_schemas')

urlpatterns = routers.urls

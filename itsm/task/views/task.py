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

import json
from collections import OrderedDict

from django.db import transaction
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from bulk_update.helper import bulk_update

from common.log import logger
from itsm.component.constants import (
    EMPTY_INT,
    JSON_HANDLE_FIELDS,
    EMPTY_LIST,
    SOPS_TEMPLATE_KEY,
    RUNNING,
    ACTION_OPERATE,
    SKIPPED,
    ACTION_SKIP,
)
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.exceptions import CallTaskPipelineError, ComponentCallError
from itsm.task.models import Task, TaskField, TaskLib
from itsm.task.permissions import TaskPermissionValidate
from itsm.task.serializers import (
    TaskSerializer,
    TaskOrderSerializer,
    TaskFieldSerializer,
    TaskFieldBatchUpdateSerializer,
    TaskProceedSerializer,
    TaskFilterSerializer,
    TaskLibSerializer,
    TaskLibListSerializer,
    TaskListSerializer,
    TaskRetrySerializer,
    TaskCreateSerializer,
    TaskLibTasksSerializer,
)


class TaskViewSet(component_viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('create_at')
    filter_fields = {
        "ticket_id": ["exact"],
        "component_type": ["exact", "in"],
        "status": ["exact", "in"],
        "state_id": ["exact", "in"],
        "execute_state_id": ["exact", "in"],
        "task_schema_id": ["exact", "in"],
    }
    ordering_fields = ("order",)
    permission_classes = (TaskPermissionValidate,)

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer

        return TaskSerializer

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None
        query_set = super().get_queryset()
        return query_set

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        # 自定义筛选
        filter_serializer = TaskFilterSerializer(data=self.request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        kwargs = filter_serializer.validated_data
        queryset = Task.objects.get_tasks(queryset, **kwargs)
        return queryset

    @staticmethod
    def create_task(data, username):
        need_start = data.pop("need_start", False)
        serializer = TaskCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            fields = serializer.validated_data.pop("fields", {})
            instance = serializer.save(creator=username)
            instance.create_sub_task(fields=fields, operator=username, data=data)
            instance.do_after_create(fields)
        instance.create_task_pipeline(need_start)  # 放在事务里会在事务未提交时去获取，导致获取不到

        return instance

    def create(self, request, *args, **kwargs):
        try:
            if request.data.get("batch_create", False):
                return self.batch_create(request, *args, **kwargs)

            task = self.create_task(request.data, request.user.username)

            return Response({'task_id': task.id}, status=status.HTTP_201_CREATED)
        except ComponentCallError as error:
            return Response(
                {
                    'result': False,
                    'message': error.message,
                    'data': error.ERROR_CODE,
                    'code': ComponentCallError.ERROR_CODE_INT,
                }
            )

    def perform_destroy(self, instance):
        instance.do_before_delete(operator=self.request.user.username)
        super(TaskViewSet, self).perform_destroy(instance)

    def batch_create(self, request, *args, **kwargs):
        """
        批量创建（从任务库创建）
        """
        data = request.data
        common_info = {
            "ticket_id": data['ticket_id'],
        }

        tasks = []
        for task_data in data['tasks']:
            task_data.update(common_info)
            task = self.create_task(task_data, request.user.username)
            tasks.append(task.id)

        return Response(tasks, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        user = serializer.context.get("request").user
        username = getattr(user, "username", "guest")
        update_info = {"updated_by": username}

        with transaction.atomic():
            if "fields" in serializer.validated_data:
                fields = serializer.validated_data["fields"]

                # 更新任务名称
                if "task_name" in fields:
                    update_info.update(name=fields["task_name"])

                # 更新任务字段
                for key, value in fields.items():
                    task_field = serializer.instance.create_fields.get(key=key)
                    task_field.value = value
                    task_field.save()

                instance = serializer.save(**update_info)
                if instance.component_type == "SOPS":
                    try:
                        instance.update_sops_task(fields=fields["sops_templates"], operator=username)
                    except ComponentCallError as error:
                        return Response(
                            {
                                'result': False,
                                'message': error.message,
                                'data': error.ERROR_CODE,
                                'code': ComponentCallError.ERROR_CODE_INT,
                            }
                        )
            else:
                serializer.save(**update_info)

    @action(detail=True, methods=['get'])
    def fields(self, request, *args, **kwargs):
        instance = self.get_object()
        field_view = TaskFieldViewSet()
        field_view.request = self.request
        task_field_instances = field_view.filter_queryset(instance.all_fields.all())
        return Response(TaskFieldSerializer(task_field_instances, many=True).data)

    @action(detail=False, methods=["post"], url_path="order")
    def set_order(self, request, *args, **kwargs):
        """设置单据任务列表在整个生命周期下的执行顺序
        生命周期: 创建任务->处理任务->总结任务
        """
        serializer = TaskOrderSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        ticket_id = request.data["ticket_id"]
        # 示例数据: [{"task_id": 1, "order": 1}, {"task_id": 2, "order": 2}]
        task_orders = request.data["task_orders"]
        task_id_order_mapping = {i["task_id"]: i["order"] for i in task_orders}
        tasks = Task.objects.filter(ticket_id=ticket_id, id__in=task_id_order_mapping.keys())

        for task in tasks:
            task.order = task_id_order_mapping.get(task.id, EMPTY_INT)

        bulk_update(tasks, update_fields=["order"])
        return Response()

    @action(detail=True, methods=["post"])
    def proceed(self, request, *args, **kwargs):
        """任务操作"""

        task = self.get_object()

        username = request.user.username
        serializer = TaskProceedSerializer(data=request.data, context={'task': task})
        serializer.is_valid(raise_exception=True)

        proceed_action = serializer.validated_data["action"]
        fields = serializer.validated_data["fields"]

        with transaction.atomic():
            # 填充任务处理人并同步到单据中
            if proceed_action == ACTION_OPERATE:
                task.ticket.add_history_task_processors(username)
                task.executor = username
                task.save(update_fields=["executor"])
                try:
                    res = task.activity_callback(proceed_action, fields, username)
                except Exception as e:
                    raise CallTaskPipelineError(_("任务节点回调异常（%s）") % e)
                if not res.result:
                    return Response({'result': False, 'message': res.message})
            else:
                task.confirmer = username
                task.save(update_fields=["confirmer"])
                task.confirm_task(operator=username, fields=fields)

            return Response()

    @action(detail=True, methods=["post"])
    def retry(self, request, *args, **kwargs):
        """重试任务"""

        task = self.get_object()
        username = request.user.username

        serializer = TaskRetrySerializer(data=request.data, context={'task': task})
        serializer.is_valid(raise_exception=True)

        # 覆盖sops_template字段
        sops_templates = serializer.validated_data[SOPS_TEMPLATE_KEY]
        task.create_fields.filter(key=SOPS_TEMPLATE_KEY).update(_value=json.dumps(sops_templates))

        fields = serializer.validated_data["fields"]

        try:
            callback_result = task.activity_callback(ACTION_OPERATE, fields, username, False)
        except Exception as e:
            raise CallTaskPipelineError(_("任务节点回调异常（%s）") % e)

        if not callback_result.result:
            # 回调失败的时候直接抛出异常，记录回调信息
            logger.error(_("任务节点回调异常（%s）"), callback_result.message)
            raise CallTaskPipelineError(_("任务节点回调异常（%s）") % callback_result.message)

        with transaction.atomic():
            task.update_executor_status(username, RUNNING)
        return Response()

    @action(detail=True, methods=["post"])
    def skip(self, request, *args, **kwargs):
        """忽略任务"""

        task = self.get_object()
        username = request.user.username

        try:
            res = task.activity_callback(ACTION_SKIP, [], username, False)
        except Exception as e:
            raise CallTaskPipelineError(_("任务节点回调异常（%s）") % e)

        if not res.result:
            return Response({'result': False, 'message': res.message})

        with transaction.atomic():
            task.update_executor_status(username, SKIPPED)
        return Response()

    @action(detail=True, methods=["get"])
    def get_task_status(self, request, *args, **kwargs):
        """查询标准运维任务状态"""
        return Response(self.get_object().get_task_status())

    @action(detail=False, methods=["get"])
    def sync_task_status(self, request, *args, **kwargs):
        """同步标准运维任务状态"""
        ticket_id = request.query_params.get("ticket_id")
        Task.sync_tasks_status(ticket_id)
        return Response()


class TaskFieldViewSet(component_viewsets.ModelViewSet):
    queryset = TaskField.objects.all()
    serializer_class = TaskFieldSerializer
    pagination_class = None
    filter_fields = {
        "task_id": ["exact"],
        "stage": ["exact", "in"],
    }
    ordering_fields = ("sequence",)

    @action(detail=False, methods=["put"])
    def batch_update(self, request):
        """批量更新任务字段"""
        serializer = TaskFieldBatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        fields = OrderedDict({field["id"]: field for field in serializer.validated_data["fields"]})
        ordering = "FIELD(`id`, {})".format(",".join(["'{}'".format(field_id) for field_id in fields.keys()]))
        task_fields = TaskField.objects.filter(id__in=fields.keys()).extra(
            select={"custom_order": ordering}, order_by=["custom_order"]
        )

        for task_field in task_fields:
            value = fields[task_field.id].get("value")
            task_field._value = json.dumps(value) if task_field.type in JSON_HANDLE_FIELDS else value
            task_field.choice = fields[task_field.id].get("choice", EMPTY_LIST)

        bulk_update(task_fields, update_fields=["_value", "choice"])
        return Response()


class TaskLibViewSet(component_viewsets.ModelViewSet):
    queryset = TaskLib.objects.all()
    serializer_class = TaskLibSerializer
    pagination_class = None
    filter_fields = {
        'service_id': ['exact', 'in'],
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskLibListSerializer

        return TaskLibSerializer

    def get_queryset(self):
        """返回个人任务库"""
        return self.queryset.filter(creator=self.request.user.username)

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            data = {
                "name": request.data["name"],
                "service_id": request.data["service_id"],
                "creator": request.user.username,
            }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            task_id_list = request.data.pop("tasks", [])
            instance.create_lib_tasks(task_id_list)
        return Response({'task_lib_id': instance.id}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            task_id_list = request.data.pop("tasks", [])
            if not task_id_list:
                raise ValidationError(_("任务列表为空"))
            instance.lib_tasks.all().delete()
            instance.create_lib_tasks(task_id_list)

        return Response({'task_lib_id': instance.id}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def tasks(self, request, *args, **kwargs):
        """获取任务库中的任务"""
        task_lib = self.get_object()
        tasks = TaskLibTasksSerializer(instance=task_lib.lib_tasks.all(), many=True)
        return Response(tasks.data)

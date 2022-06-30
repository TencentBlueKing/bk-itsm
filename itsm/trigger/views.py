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

from django.utils.translation import ugettext as _
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from itsm.component.constants import (
    TRIGGER_SIGNAL,
    ACTION_STATUS_CREATED,
    ACTION_STATUS_FAILED,
    EMPTY_STRING,
    EMPTY_INT,
    ResponseCodeStatus,
    DEFAULT_PROJECT_PROJECT_KEY,
)
from itsm.component.dlls.component import ComponentLibrary
from itsm.component.drf import viewsets as component_viewsets
from itsm.trigger.models import Trigger, TriggerRule, ActionSchema, Action
from itsm.trigger.serializers import (
    TriggerSerializer,
    TriggerRuleSerializer,
    ActionSchemaSerializer,
    ActionSerializer,
    ActionDetailSerializer,
)
from .api import import_trigger
from .validators import BulkTriggerRuleValidator
from .permissions import WorkflowTriggerPermit


class ComponentApiViewSet(component_viewsets.APIView):
    def get(self, request, *args, **kwargs):
        """Get registered trigger components"""
        query_codes = [
            code for code in request.query_params.get("code__in", "").split(",") if code
        ]
        ret = []
        for code, component_cls in ComponentLibrary.components.get(
            "trigger", {}
        ).items():
            if getattr(component_cls, "is_sub_class", False) or (
                code not in query_codes and query_codes
            ):
                continue
            component_item = {
                "name": _(component_cls.name),
                "key": code,
                "field_schema": component_cls.get_inputs(),
                "exclude_signal_type": component_cls.exclude_signal_type,
            }
            ret.append(component_item)

        return Response(ret)


class TriggerViewSet(component_viewsets.ModelViewSet):
    queryset = Trigger.objects.all()
    serializer_class = TriggerSerializer
    filter_fields = {
        "name": ["exact", "in", "contains", "icontains"],
        "source_id": ["exact", "in"],
        "source_type": ["exact", "in"],
        "signal": ["exact", "in"],
        "sender": ["exact", "in"],
    }

    permission_classes = (WorkflowTriggerPermit,)
    permission_free_actions = ["list"]

    def get_queryset(self):

        if not self.request.query_params.get("page_size"):
            self.pagination_class = None

        query_set = super(TriggerViewSet, self).get_queryset()
        source_table_id = self.request.query_params.get("source_table_id")
        if source_table_id and source_table_id.isdigit():
            query_set = query_set.filter(
                source_table_id__in=[EMPTY_INT, int(source_table_id)]
            )
        return query_set.filter()

    def list(self, request, *args, **kwargs):

        project_key = self.request.query_params.get(
            "project_key", DEFAULT_PROJECT_PROJECT_KEY
        )

        queryset = self.filter_queryset(
            self.get_queryset().filter(project_key=project_key)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["GET"], detail=False, url_path="signals")
    def trigger_signals(self, request, *args, **kwargs):
        signal_types = request.query_params.get("signal_type", "").split(",")
        signals = [
            {"key": key, "name": value}
            for _type in signal_types
            for key, value in TRIGGER_SIGNAL.get(_type, {}).items()
        ]
        return Response(signals)

    @action(detail=False, methods=["post"])
    def clone(self, request, *args, **kwargs):
        # 除了id, source_id, source_type, 可覆盖引用触发器的属性列表
        can_update_attrs = ["signal", "project_key"]
        can_update_info = dict(
            [
                (attr, request.data[attr])
                for attr in can_update_attrs
                if attr in request.data
            ]
        )

        return Response(
            import_trigger(
                request.data["src_trigger_ids"],
                dst_source_id=request.data["dst_source_id"],
                dst_source_type=request.data["dst_source_type"],
                dst_sender=request.data["dst_sender"],
                **can_update_info
            )
        )

    @action(methods=["POST"], detail=True)
    def create_or_update_rules(self, request, *args, **kwargs):
        def _single_create(action_data):
            serializer = TriggerRuleSerializer(
                data=action_data, context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return serializer.data

        def _single_update(action_data, instance):

            serializer = TriggerRuleSerializer(
                instance,
                data=action_data,
                partial=False,
                context=self.get_serializer_context(),
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, "_prefetched_objects_cache", None):
                # copy from drf
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return serializer.data

        instance = self.get_object()
        BulkTriggerRuleValidator()(request.data)
        rules = []
        with transaction.atomic():
            for _data in request.data:
                _data.update({"trigger_id": instance.id})
                try:
                    rule_instance = TriggerRule.objects.get(id=_data.get("id", 0))
                    rule = _single_update(_data, rule_instance)
                except TriggerRule.DoesNotExist:
                    rule = _single_create(_data)
                rules.append(rule["id"])
        TriggerRule.objects.filter(trigger_id=instance.id).exclude(
            id__in=rules
        ).delete()
        return Response(rules)

    @action(methods=["POST"], detail=True)
    def create_or_update_action_schemas(self, request, *args, **kwargs):
        def _single_create(action_data):
            serializer = ActionSchemaSerializer(
                data=action_data, context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return serializer.data

        def _single_update(action_data, instance):

            serializer = ActionSchemaSerializer(
                instance,
                data=action_data,
                partial=False,
                context=self.get_serializer_context(),
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, "_prefetched_objects_cache", None):
                # copy from drf
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return serializer.data

        schemas = []
        with transaction.atomic():
            for _data in request.data:
                try:
                    instance = ActionSchema.objects.get(id=_data.get("id", 0))
                    schema = _single_update(_data, instance)
                except ActionSchema.DoesNotExist:
                    schema = _single_create(_data)
                schemas.append(schema["id"])
        return Response(schemas)


class TriggerRuleViewSet(component_viewsets.AuthWithoutResourceModelViewSet):
    """
    响应事件的视图
    """

    queryset = TriggerRule.objects.all()
    serializer_class = TriggerRuleSerializer
    filter_fields = {"trigger_id": ["exact", "in"]}

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None
        query_set = super(TriggerRuleViewSet, self).get_queryset()
        return query_set


class ActionSchemaViewSet(component_viewsets.AuthWithoutResourceModelViewSet):
    """
    响应事件配置的视图
    """

    queryset = ActionSchema.objects.all()
    serializer_class = ActionSchemaSerializer
    filter_fields = {"id": ["exact", "in"]}

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None
        query_set = super(ActionSchemaViewSet, self).get_queryset()
        return query_set

    @action(methods=["POST"], detail=False)
    def batch_create(self, request, *args, **kwargs):
        """
        批量创建响应事件
        """

        def _single_create(action_data):
            serializer = self.get_serializer(data=action_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return serializer.data

        schemas = []
        for _data in request.data:
            schemas.append(_single_create(_data)["id"])
        return Response(schemas, status=status.HTTP_201_CREATED)

    @action(methods=["POST"], detail=False)
    def batch_create_or_update(self, request, *args, **kwargs):
        def _single_create(action_data):
            serializer = self.get_serializer(data=action_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return serializer.data

        def _single_update(action_data, instance):

            serializer = self.get_serializer(instance, data=action_data, partial=False)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, "_prefetched_objects_cache", None):
                # copy from drf
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return serializer.data

        schemas = []
        with transaction.atomic():
            for _data in request.data:
                try:
                    instance = self.queryset.get(id=_data.get("id", 0))
                    schema = _single_update(_data, instance)
                except ActionSchema.DoesNotExist:
                    schema = _single_create(_data)
                schemas.append(schema["id"])
        return Response(schemas)


class ActionViewSet(component_viewsets.ModelViewSet):
    """
    响应事件的视图
    """

    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    filter_fields = {
        "id": ["exact", "in"],
        "sender": ["exact", "in"],
        "source_type": ["exact"],
        "source_id": ["exact"],
    }

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None
        query_set = super(ActionViewSet, self).get_queryset()

        return query_set

    def filter_queryset(self, queryset):
        operate_type = self.request.query_params.get("operate_type")
        queryset = super(ActionViewSet, self).filter_queryset(queryset)
        if not operate_type:
            return queryset

        schema_id__in = ActionSchema.objects.filter(
            id__in=queryset.values_list("schema_id", flat=True),
            operate_type=operate_type,
        ).values_list("id", flat=True)
        return queryset.filter(schema_id__in=schema_id__in)

    def get_serializer_class(self):
        """
        获取详情的时候采用详情序列化参数
        """
        if self.action == "retrieve":
            return ActionDetailSerializer
        return super(ActionViewSet, self).get_serializer_class()

    @action(methods=["POST"], detail=True)
    def run(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(status=ACTION_STATUS_CREATED)
        instance = self.get_object()
        instance.params = request.data.get("params", {})
        instance.save()
        instance.execute(operator=request.user.username, need_update_context=True)
        result = False if instance.status == ACTION_STATUS_FAILED else True
        instance.refresh_from_db()
        message = (
            instance.ex_data[0].get("message") if instance.ex_data else EMPTY_STRING
        )
        return Response(
            {
                "result": result,
                "message": message,
                "data": {"action_id": instance.id},
                "code": ResponseCodeStatus.OK,
            }
        )

    @action(methods=["post"], detail=True)
    def params(self, request, *args, **kwargs):
        instance = self.get_object()
        context = request.data.get("context", {})
        return Response(instance.action_params(context))

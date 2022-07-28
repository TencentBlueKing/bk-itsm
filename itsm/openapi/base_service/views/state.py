# -*- coding: utf-8 -*-
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.decorators import custom_apigw_required
from itsm.component.exceptions import ParamError
from itsm.workflow.models import State, TICKET_GLOBAL_VARIABLES, GlobalVariable
from itsm.workflow.serializers import StateSerializer, GlobalVariableSerializer
from itsm.workflow.views import BaseWorkflowElementViewSet
from itsm.workflow import signals


class StateViewSet(BaseWorkflowElementViewSet):
    queryset = State.objects.select_related("workflow").filter(is_deleted=False)
    queryset = queryset.prefetch_related("notify").all()
    serializer_class = StateSerializer
    filter_fields = {
        "id": ["in"],
        "workflow": ["exact", "in"],
        "name": ["exact", "contains", "startswith"],
        "type": ["exact", "in"],
    }

    def perform_destroy(self, instance):
        """删除State的同时需要重连主流程状态"""
        super(StateViewSet, self).perform_destroy(instance)
        signals.state_deleted.send(
            sender=State, flow_id=instance.workflow_id, state_id=instance.id
        )

    def perform_create(self, serializer):
        super(StateViewSet, self).perform_create(serializer)
        state = serializer.instance
        signals.state_created.send(
            sender=State,
            flow_id=state.workflow_id,
            state_id=state.id,
            state_type=state.type,
        )

    @custom_apigw_required
    def list(self, request, *args, **kwargs):
        return super(StateViewSet, self).list(request, *args, **kwargs)

    @custom_apigw_required
    def retrieve(self, request, *args, **kwargs):
        return super(StateViewSet, self).retrieve(request, *args, **kwargs)

    @custom_apigw_required
    def update(self, request, *args, **kwargs):
        return super(StateViewSet, self).update(request, *args, **kwargs)

    @custom_apigw_required
    @action(detail=True, methods=["post"])
    def update_attrs(self, request, *args, **kwargs):
        """
        {"key": "value"}
        """
        instance = self.get_object()
        READ_ONLY_ATTRS = [
            "id",
            "is_delete",
            "workflow_id",
            "type",
            "is_draft",
            "creator",
            "create_at",
            "updated_by",
            "update_at",
            "end_at",
            "fields",
        ]
        attrs = request.data.get("attrs", [])
        for attr in attrs:
            key = attr.get("key")

            if not hasattr(instance, key):
                raise ParamError("修改失败，属性{}不存在".format(key))

            if key in READ_ONLY_ATTRS:
                raise ParamError("{}是只读属性，不允许修改".format(key))
            setattr(instance, key, attr.get("value"))

        with transaction.atomic():
            instance.save()

        ser = self.get_serializer(instance)
        return Response(ser.data)

    @custom_apigw_required
    def create(self, request, *args, **kwargs):
        return super(StateViewSet, self).create(request, *args, **kwargs)

    @custom_apigw_required
    def destroy(self, request, *args, **kwargs):
        return super(StateViewSet, self).destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    @custom_apigw_required
    def variables(self, request, *args, **kwargs):
        state = self.get_object()

        # 默认先把field和全局的变量都获取出来
        resource_type = request.GET.get("resource_type", "both")
        exclude_self = request.GET.get("exclude_self", False)

        valid_inputs = state.get_valid_inputs(
            exclude_self=exclude_self, resource_type=resource_type, scope="state"
        )

        # 非提单节点可引用单据属性（提单节点提交前，尚未创建工单）
        if not state.is_first_state:
            valid_inputs.extend(TICKET_GLOBAL_VARIABLES)

        return Response(valid_inputs)

    @action(detail=True, methods=["get"])
    @custom_apigw_required
    def post_states(self, request, *args, **kwargs):
        """
        当前节点的后置节点
        """
        instance = self.get_object()
        include_self = request.query_params.get("include_self", "false")
        posts = instance.get_post_states(
            contain_auto=request.query_params.get("contain_auto", "false"),
            exclude_states=[instance.id],
        )
        data = self.get_serializer(posts, many=True).data

        if include_self == "true":
            instance_data = self.get_serializer(instance).data
            data.insert(0, instance_data)
        return Response(data)

    @action(detail=True, methods=["get"])
    @custom_apigw_required
    def pre_states(self, request, *args, **kwargs):
        instance = self.get_object()
        pres = instance.get_valid_inputs_states(exclude_states=[instance.id])
        serializer = self.get_serializer(pres, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    @custom_apigw_required
    def sign_variables(self, request, *args, **kwargs):
        """获取会签节点输出变量"""
        state = self.get_object()
        global_variables = GlobalVariable.objects.filter(
            state_id=state.id, is_valid=True
        )
        serializer = GlobalVariableSerializer(global_variables, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    @custom_apigw_required
    def clone(self, request, *args, **kwargs):
        state = self.get_object()
        state = state.clone()
        signals.state_created.send(
            sender=State,
            flow_id=state.workflow_id,
            state_id=state.id,
            state_type=state.type,
        )
        return Response(self.serializer_class(state, many=False).data)

    @action(detail=True, methods=["get"])
    @custom_apigw_required
    def get_approve_states(self, request, *args, **kwargs):
        instance = self.get_object()
        states = instance.get_approve_states()
        return Response(states)

    @action(detail=True, methods=["get"])
    @custom_apigw_required
    def group_variables(self, request, *args, **kwargs):
        state = self.get_object()

        # 默认先把field和全局的变量都获取出来
        resource_type = request.GET.get("resource_type", "both")
        exclude_self = request.GET.get("exclude_self", False)
        data = state.get_valid_inputs_by_group(
            exclude_self=exclude_self, resource_type=resource_type, scope="state"
        )
        return Response(data)

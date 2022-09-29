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

import copy
import json
import os
from wsgiref.util import FileWrapper

from bulk_update.helper import bulk_update
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import StreamingHttpResponse, FileResponse, Http404
from django.utils.encoding import escape_uri_path
from django.utils.translation import ugettext as _
from rest_framework import serializers, status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from business_rules.operators import (
    NumericType,
    StringType,
    DateTimeType,
    TimeType,
    BooleanType,
    SelectMultipleType,
)
from common.log import logger
from itsm.component.constants import (
    DEFAULT_ENGINE_VERSION,
    DISTRIBUTE_TYPE_CHOICES,
    FAULT_SOURCE_CHOICES,
    FIELD_BIZ,
    FLOW_CONDITION_TYPE_CHOICES,
    LAYOUT_CHOICES,
    METHOD_CHOICES,
    NOTIFY_RULE_CHOICES,
    PROCESSOR_CHOICES,
    REGEX_CHOICES,
    SOPS_FIELD_MAP,
    SOURCE_CHOICES,
    START_STATE,
    STATE_TYPE_CHOICES,
    TABLE,
    TYPE_CHOICES,
    VALIDATE_CHOICES,
    STATE_BUTTON,
    TICKET_GLOBAL_VARIABLES,
    TRIGGER_ICON_CHOICE,
    TRIGGER_SOURCE_TYPE,
    TRIGGER_SIGNAL,
    TRIGGER_CATEGORIES,
    EMPTY_INT,
    ONLY_BACKEND_SIGNALS,
    SOURCE_TICKET,
    SOURCE_TASK,
    SOURCE_WORKFLOW,
    PUBLIC_PROJECT_PROJECT_KEY,
)
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.drf.mixins import DynamicListModelMixin
from itsm.component.exceptions import NotAllowedError, ParamError, WorkFlowInvalidError
from itsm.component.utils.basic import create_version_number
from itsm.component.utils.bk_bunch import bunchify
from itsm.component.utils.misc import JsonEncoder
from itsm.iadmin.models import SystemSettings
from itsm.service.models import Service
from itsm.workflow import signals
from itsm.workflow.models import (
    Condition,
    Field,
    State,
    Table,
    TemplateField,
    Transition,
    Trigger,
    Workflow,
    WorkflowVersion,
    GlobalVariable,
    TaskSchema,
    TaskFieldSchema,
)
from itsm.workflow.permissions import (
    BaseWorkflowElementIamAuth,
    WorkflowIamAuth,
    FlowVersionIamAuth,
    VersionDeletePermit,
    TemplateFieldPermissionValidate,
    TaskSchemaPermit,
)
from itsm.workflow.utils import translate_constant_2, get_notify_type_choice
from itsm.workflow.validators import (
    WorkflowPipelineValidator,
    add_fields_from_table_validate,
    related_validate,
    table_remove_fiels_validate,
    template_field_can_destroy,
    template_fields_exists_validate,
    transition_batch_update_validate,
    task_schema_delete_validate,
    state_exists_validate,
)
from .serializers import (
    FieldSerializer,
    StateSerializer,
    TableRetrieveSerializer,
    TableSerializer,
    TemplateFieldFilterSerializer,
    TemplateFieldSerializer,
    TransitionSerializer,
    TransitionTemplateSerializer,
    TriggerSerializer,
    WorkflowSerializer,
    WorkflowVersionSerializer,
    GlobalVariableSerializer,
    TaskSchemaSerializer,
    TaskFieldSchemaSerializer,
)

# 文件存储对象
store = settings.STORE


class PartialUpdateModelMixin(object):
    """支持局部更新"""

    def update(self, request, *args, **kwargs):
        """支持局部更新，通过关键字partial"""

        partial = request.data.get("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return Response(serializer.data)


class BaseWorkflowElementViewSet(component_viewsets.ModelViewSet):
    """
    流程基础元素视图
    """

    permission_classes = (BaseWorkflowElementIamAuth,)


class WorkflowViewSet(
    DynamicListModelMixin, PartialUpdateModelMixin, component_viewsets.AuthModelViewSet
):
    """工作流视图集
    BEP: 这里有意思了，多重集成，哪个update生效了？
    + create
    + update：局部可更新（只读控制）
    + delete：软删除
    + list
    """

    queryset = Workflow.objects.prefetch_related("notify").order_by("-update_at")
    serializer_class = WorkflowSerializer
    filter_fields = {
        "id": ["in"],
        "is_biz_needed": ["exact", "in"],
        "name": ["exact", "contains", "startswith", "icontains"],
        "is_enabled": ["exact", "in"],
        "is_draft": ["exact", "in"],
        "updated_by": ["exact", "contains", "startswith"],
        "flow_type": ["exact", "in"],
    }
    permission_free_actions = ["get_global_choices", "list"]
    permission_classes = (WorkflowIamAuth,)

    def get_queryset(self):
        self.queryset = self.queryset.exclude(flow_type="internal")
        return self.queryset

    def perform_create(self, serializer):
        """创建时补充基础Model中的字段"""
        user = serializer.context.get("request").user
        username = getattr(user, "username", "guest")

        serializer.save(
            creator=username, updated_by=username, engine_version=DEFAULT_ENGINE_VERSION
        )

    def perform_destroy(self, instance):
        """自定义删除前行为"""
        Trigger.objects.filter(
            source_type=SOURCE_WORKFLOW, source_id=instance.id
        ).delete()
        super(WorkflowViewSet, self).perform_destroy(instance)

    @action(detail=False, methods=["get"])
    def get_global_choices(self, request):
        """查询全局选项列表信息"""
        trigger_methods = {
            "int": NumericType.get_display_operators(),
            "bool": BooleanType.get_display_operators(),
            "string": StringType.get_display_operators(),
            "select": StringType.get_display_operators(),
            "radio": StringType.get_display_operators(),
            "text": StringType.get_display_operators(),
            "datetime": DateTimeType.get_display_operators(),
            "time": TimeType.get_display_operators(),
            "multiselect": SelectMultipleType.get_display_operators(),
            "checkbox": SelectMultipleType.get_display_operators(),
            "member": SelectMultipleType.get_display_operators(),
            "members": SelectMultipleType.get_display_operators(),
        }

        notify_type_choice = get_notify_type_choice()

        return Response(
            {
                "field_type": translate_constant_2(TYPE_CHOICES[:-1]),
                "source_type": translate_constant_2(SOURCE_CHOICES),
                "layout_type": translate_constant_2(LAYOUT_CHOICES),
                "validate_type": translate_constant_2(VALIDATE_CHOICES),
                "notify_type": translate_constant_2(notify_type_choice),
                "notify_rule_type": translate_constant_2(NOTIFY_RULE_CHOICES),
                "state_type": translate_constant_2(STATE_TYPE_CHOICES),
                "processor_type": translate_constant_2(PROCESSOR_CHOICES),
                "fault_source": translate_constant_2(FAULT_SOURCE_CHOICES),
                "distribute_type": translate_constant_2(DISTRIBUTE_TYPE_CHOICES),
                "methods": translate_constant_2(METHOD_CHOICES),
                "condition_type": translate_constant_2(FLOW_CONDITION_TYPE_CHOICES),
                "sops_field_map": translate_constant_2(SOPS_FIELD_MAP),
                "trigger_icon": translate_constant_2(TRIGGER_ICON_CHOICE),
                "trigger_source_type": translate_constant_2(TRIGGER_SOURCE_TYPE),
                "trigger_methods": trigger_methods,
                "ticket_variables": TICKET_GLOBAL_VARIABLES,
                "trigger_signals": TRIGGER_SIGNAL,
                "trigger_categories": TRIGGER_CATEGORIES,
                "only_backend_signals": ONLY_BACKEND_SIGNALS,
            }
        )

    @action(detail=False, methods=["get"])
    def get_regex_choice(self, request):
        field_type = request.GET.get("type")
        regex_choice = REGEX_CHOICES.get(field_type, [("EMPTY", "")])
        return Response(
            {
                "regex_choice": [(i[0], _(i[1])) for i in regex_choice],
            }
        )

    @action(detail=True, methods=["get"])
    def variables(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.variables)

    @action(detail=True, methods=["post"])
    def create_accept_transitions(self, request, pk=None):
        """创建主流程流转节点"""
        try:
            instance = self.get_object()
            # 流程是否有效的校验
            WorkflowPipelineValidator(instance)()
        except WorkFlowInvalidError as error:
            logger.exception(error)
            return Response(
                {
                    "result": False,
                    "code": error.code,
                    "data": {"invalid_state_ids": error.invalid_state_ids},
                    "message": str(error),
                }
            )
        return Response()

    @action(detail=True, methods=["post"])
    def deploy(self, request, pk=None):
        """部署流程"""

        name = request.data.get("name", None)
        instance = self.get_object()
        WorkflowPipelineValidator(instance)(if_deploy=True)
        version = instance.create_version(request.user.username, name=name)
        return Response({"id": version.id})

    @action(detail=True, methods=["get"])  # renderer_classes=(JsonFileRenderer,))
    def exports(self, request, pk=None):
        """
        导出流程
        """
        workflow = self.get_object()
        if request.query_params.get("need_validate", True) is True:
            WorkflowPipelineValidator(workflow)()

        data = workflow.tag_data(request.user.username, need_tag_task=True)

        # 统一导入导出格式为列表数据
        response = FileResponse(json.dumps([data], cls=JsonEncoder, indent=2))
        response["Content-Type"] = "application/octet-stream"
        # 中文文件名乱码问题
        response[
            "Content-Disposition"
        ] = "attachment; filename*=UTF-8''bk_itsm_{}_{}.json".format(
            escape_uri_path(workflow.name),
            create_version_number(),
        )

        return response

    @action(detail=True, methods=["post"])
    def imports(self, request, pk=None):
        """
        批量导入流程
        TODO: 当前应该设置detail= False 当前的操作不需要带PK处理
        """

        if pk != str(EMPTY_INT):
            raise NotAllowedError(_("暂不支持当前操作"))

        workflows = []
        try:
            data = json.loads(request.FILES.get("file").read())
        except ValueError:
            raise ParamError(_("文件格式有误，请提供从本系统导出的json文件"))

        for item in data:
            try:
                # 导入的流程默认不启用
                item.update(is_enabled=False)
                workflow = Workflow.restore_tag(item, request.user.username)
                workflows.append(workflow)
            except Exception as e:
                logger.exception("import workflow exception: %s" % e)

        return Response(
            {"success": len(workflows), "failed": len(data) - len(workflows)}
        )

    @action(detail=True, methods=["get"])
    def table(self, request, *args, **kwargs):
        """流程关联的基础模型"""
        workflow = self.get_object()
        if not workflow.table:
            return Response(
                {
                    "message": "success",
                    "code": "OK",
                    "data": {"name": "", "desc": "", "fields": []},
                    "result": True,
                }
            )
        return Response(
            TableRetrieveSerializer(
                workflow.table, context={"is_biz_needed": workflow.is_biz_needed}
            ).data
        )


class StateViewSet(BaseWorkflowElementViewSet):
    """状态视图集
    + create：创建state的同时，需要创建关联字段
    + update：更新关联字段
    + delete：软删除
    + list
    """

    queryset = State.objects.select_related("workflow").filter(is_deleted=False)
    queryset = queryset.prefetch_related("notify").all()
    serializer_class = StateSerializer
    filter_fields = {
        "id": ["in"],
        "workflow": ["exact", "in"],
        "name": ["exact", "contains", "startswith"],
        "type": ["exact", "in"],
    }
    pagination_class = None

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

    @action(detail=True, methods=["get"])
    def variables(self, request, *args, **kwargs):
        state = self.get_object()
        # 默认先把field和全局的变量都获取出来
        resource_type = request.GET.get("resource_type", "both")
        exclude_self = request.GET.get("exclude_self", False)

        valid_inputs = state.get_valid_inputs(
            exclude_self=exclude_self, resource_type=resource_type, scope="state"
        )

        # 如果是下拉框选项的，则允许显示中文名
        new_inputs = []
        for var in valid_inputs:
            if var["type"] in ["SELECT", "MULTISELECT"]:
                new_var = copy.deepcopy(var)
                new_var["key"] = "{}__display".format(var["key"])
                new_var["name"] = "{}_display".format(var["name"])
                new_inputs.append(new_var)

        valid_inputs.extend(new_inputs)

        # 非提单节点可引用单据属性（提单节点提交前，尚未创建工单）
        if not state.is_first_state:
            valid_inputs.extend(TICKET_GLOBAL_VARIABLES)

        return Response(valid_inputs)

    @action(detail=True, methods=["get"])
    def group_variables(self, request, *args, **kwargs):
        state = self.get_object()

        # 默认先把field和全局的变量都获取出来
        resource_type = request.GET.get("resource_type", "both")
        exclude_self = request.GET.get("exclude_self", False)

        valid_inputs = state.get_valid_inputs_by_group(
            exclude_self=exclude_self, resource_type=resource_type, scope="state"
        )

        # 非提单节点可引用单据属性（提单节点提交前，尚未创建工单）
        return Response(valid_inputs)

    @action(detail=True, methods=["get"])
    def sign_variables(self, request, *args, **kwargs):
        """获取会签节点输出变量"""
        state = self.get_object()
        global_variables = GlobalVariable.objects.filter(
            state_id=state.id, is_valid=True
        )
        serializer = GlobalVariableSerializer(global_variables, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def pre_states(self, request, *args, **kwargs):
        instance = self.get_object()
        pres = instance.get_valid_inputs_states(exclude_states=[instance.id])
        serializer = self.get_serializer(pres, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
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

    @action(detail=True, methods=["post"])
    def add_fields_from_table(self, request, *args, **kwargs):
        """从基础模型新增字段"""
        fields = request.data.get("fields", [])
        state = self.get_object()
        add_fields_from_table_validate(fields, state)
        state.add_fields_from_table(fields)
        return Response()

    @action(detail=True, methods=["post"])
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

    @action(detail=True, methods=["post"])
    def set_actions(self, request, *args, **kwargs):
        """设置节点按钮组"""
        state = self.get_object()
        state_actions = request.data
        if not isinstance(state_actions, list):
            raise ParamError(_("参数格式不合法"))

        with transaction.atomic():
            # 重置节点的按钮组
            Trigger.objects.filter(
                state_id=state.id, workflow_id=state.workflow_id, type=STATE_BUTTON
            ).delete()
            trigger_objs = []
            for state_action in state_actions:
                state_action.update(state_id=state.id, workflow_id=state.workflow_id)
                TriggerSerializer(data=state_action).is_valid(raise_exception=True)
                trigger_objs.append(Trigger(**state_action))
            Trigger.objects.bulk_create(trigger_objs)

        return Response()


class TransitionViewSet(BaseWorkflowElementViewSet):
    """流转视图集
    + create
    + update
    + delete：软删除
    + list
    """

    queryset = Transition.objects.select_related("workflow").all()
    serializer_class = TransitionSerializer
    filter_fields = {
        "id": ["in"],
        "workflow": ["exact"],
        "name": ["exact", "contains", "startswith"],
        "from_state": ["exact", "in"],
        "to_state": ["exact", "in"],
        "check_needed": ["exact", "in"],
    }

    def perform_destroy(self, instance):
        # 从开始节点出来的连线只能由一条, 且不能被删除
        if instance.from_state.type == START_STATE:
            raise ValidationError(_("内置连线不能被删除"))

        instance.delete()

    @action(detail=True, methods=["get"])
    def variables(self, request, *args, **kwargs):
        state = self.get_object().from_state
        valid_inputs = state.get_valid_inputs(scope="transition")
        valid_inputs.extend(TICKET_GLOBAL_VARIABLES)

        return Response(valid_inputs)

    @action(detail=False, methods=["post"])
    def batch_update(self, request):
        workflow_id = request.data.get("workflow_id")
        transactions = request.data.get("transitions", [])

        transition_batch_update_validate(workflow_id, transactions)

        for item in transactions:
            Transition.objects.filter(id=item.pop("id", None)).update(**item)
        return Response()


class BaseFieldViewSet(component_viewsets.ModelViewSet):
    @action(detail=True, methods=["get"])
    def download_file(self, request, *args, **kwargs):
        unique_key = request.GET.get("unique_key")
        file_type = request.GET.get("file_type")
        if file_type == "version":
            flow_id = request.GET.get("flow_id")
            try:
                field_object = WorkflowVersion.objects.get(id=flow_id).get_field(
                    kwargs["pk"]
                )
                field_object = bunchify(field_object)
            except Service.DoesNotExist:
                raise serializers.ValidationError(_("提供的流程版本信息错误！"))
        else:
            field_object = self.get_object()

        if field_object.type != "FILE":
            raise serializers.ValidationError(_("当前字段非附件字段，无法下载附件文件！"))
        try:
            files = (
                field_object.choice
                if file_type in ["template", "version"]
                else json.loads(field_object.value)
            )
        except Exception:
            logger.exception("json解析错误")
            raise serializers.ValidationError(_("当前字段解析信息出错，请确认是否已进行数据升级！"))

        file_info = files.get(unique_key)
        if not file_info:
            raise serializers.ValidationError(_("当前字段不存在您需要下载的附件！"))

        system_file_path = SystemSettings.objects.get(key="SYS_FILE_PATH").value
        file_path = os.path.join(system_file_path, file_info["path"])

        if not store.exists(file_path):
            raise serializers.ValidationError(
                _("要下载的文件【{}】不存在, 可能已经被删除，请与管理员确认！").format(file_info["name"])
            )

        response = StreamingHttpResponse(FileWrapper(store.open(file_path, "rb"), 512))
        response["Content-Type"] = "application/octet-stream"
        response["Content-Disposition"] = "attachment; filename* = UTF-8''{}".format(
            escape_uri_path(file_info["name"])
        )
        return response


class FieldViewSet(BaseFieldViewSet):
    """表单字段视图集
        + create
        + update
        + delete：软删除
        + list
        + filter: django_filters

    备注：
        # 配置django_filter作为drf的通用过滤器
        # https://django-filter.readthedocs.io/en/master/

        # refer to django_filters.conf.VERBOSE_LOOKUPS
        # 查询样例：/api/workflow/fields/?key__in=bei_zhu,bei_zhu_2&workflow=4
    """

    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = (BaseWorkflowElementIamAuth,)
    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    filter_fields = {
        "id": ["in"],
        "key": ["exact", "in", "contains", "startswith"],
        "name": ["exact", "contains", "startswith"],
        "type": ["exact", "in"],
        "is_builtin": ["exact"],
        "is_readonly": ["exact"],
        "layout": ["exact", "in"],
        "validate_type": ["exact", "in"],
    }

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None
        query_set = super(FieldViewSet, self).get_queryset()
        return query_set

    def list(self, request, *args, **kwargs):
        """支持根据流程和节点查询字段，关闭分页"""

        workflow_id = self.request.query_params.get("workflow")
        state_id = self.request.query_params.get("state")

        queryset = self.filter_queryset(self.get_queryset())

        if workflow_id:
            workflow = Workflow.objects.get(id=workflow_id)
            if not workflow.is_biz_needed:
                queryset = queryset.exclude(key=FIELD_BIZ)

        if state_id:
            valid_fields = State.objects.fields_of_state(state_id)
            ordering = "FIELD(`id`, {})".format(
                ",".join(["'{}'".format(v) for v in valid_fields])
            )
            queryset = queryset.filter(id__in=valid_fields).extra(
                select={"ordering": ordering}, order_by=["ordering"]
            )

        serializer_data = self.get_serializer(queryset, many=True).data

        # 级联关系的梳理
        be_relied = {}
        for field_info in serializer_data:
            cur_field_key = field_info["key"]
            for field_key in field_info["related_fields"].get("rely_on", []):
                if field_key not in be_relied:
                    be_relied[field_key] = [cur_field_key]
                else:
                    be_relied[field_key].append(cur_field_key)
        for field in serializer_data:
            if field["key"] in be_relied:
                field["related_fields"]["be_relied"] = be_relied[field["key"]]

        return Response(serializer_data)

    def perform_destroy(self, instance):
        """
        自动从State的fields中移除该字段
        """
        with transaction.atomic():
            if (
                instance.key == "bk_biz_id"
                and instance.id == instance.workflow.first_state.id
            ):
                instance.workflow.is_biz_needed = False
                instance.workflow.save()
            if instance.source != TABLE:
                related_validate(instance)
            if instance.state:
                instance.state.fields.remove(instance.id)
                instance.state.save()
            super(FieldViewSet, self).perform_destroy(instance)

    @action(detail=True, methods=["post"])
    def update_layout(self, request, *args, **kwargs):
        field_object = self.get_object()
        for key in [
            "layout",
            "show_conditions",
            "show_type",
            "validate_type",
            "default",
            "regex_config",
        ]:
            setattr(field_object, key, request.data.get(key, ""))
        field_object.save()
        return Response()


class TemplateFieldViewSet(component_viewsets.ModelViewSet):
    """公共字段视图集
    + create
    + update
    + delete：软删除
    + list
    + filter: django_filters
    """

    queryset = TemplateField.objects.all()
    serializer_class = TemplateFieldSerializer
    # permission_classes = (IamAuthWithoutResourcePermit,)
    permission_classes = (TemplateFieldPermissionValidate,)
    filter_fields = {
        "id": ["in"],
        "key": ["exact", "in", "contains", "startswith"],
        "name": ["exact", "contains", "startswith", "icontains"],
        "updated_by": ["exact", "contains", "startswith", "in"],
        "type": ["exact", "in"],
    }

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None
        query_set = super(TemplateFieldViewSet, self).get_queryset()
        return query_set

    def get_list_queryset(self, request, queryset):
        """
        集中处理 queryset
        """
        if queryset:
            filter_serializer = TemplateFieldFilterSerializer(data=request.query_params)
            filter_serializer.is_valid(raise_exception=True)
            kwargs = filter_serializer.validated_data

            start_time = kwargs.get("update_at__gte")
            end_time = kwargs.get("update_at__lte")
            if start_time and end_time:
                queryset = queryset.filter(update_at__range=(start_time, end_time))
        return queryset

    def list(self, request, *args, **kwargs):
        """列表查询视图
        {
            u'key': [u'TEST'],
            u'name': [u'test'],
            u'update_at__gte': [u'2019-07-17 00:00:00'],
            u'update_at__lte': [u'2019-08-14 00:00:00'],
            u'updated_by': [u'admin'],
            u'type': [u'STRING'],
        }
        """

        queryset = self.filter_queryset(self.get_queryset())

        project_key = self.request.query_params.get(
            "project_key", PUBLIC_PROJECT_PROJECT_KEY
        )

        queryset = queryset.filter(Q(project_key=project_key))

        queryset = self.get_list_queryset(request, queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False)
    def mix_list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        project_key = self.request.query_params.get(
            "project_key", PUBLIC_PROJECT_PROJECT_KEY
        )
        queryset = queryset.filter(
            Q(project_key=project_key) | Q(project_key=PUBLIC_PROJECT_PROJECT_KEY)
        )

        queryset = self.get_list_queryset(request, queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        template_field_can_destroy(instance)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkflowVersionViewSet(
    DynamicListModelMixin, component_viewsets.AuthModelViewSet
):
    """流程版本视图集合"""

    queryset = WorkflowVersion.objects.all().order_by("-create_at")
    serializer_class = WorkflowVersionSerializer
    permission_classes = (FlowVersionIamAuth, VersionDeletePermit)

    filter_fields = {
        "id": ["in"],
        "name": ["exact", "contains", "startswith", "icontains"],
        "version_number": ["exact", "contains", "startswith"],
        "is_enabled": ["exact", "in"],
        "is_draft": ["exact", "in"],
        "updated_by": ["exact", "contains", "startswith"],
        "flow_type": ["exact", "in"],
    }

    def get_queryset(self):
        self.queryset = self.queryset.exclude(flow_type="internal")

        # select * -> select a,b,c: 部分版本字段数据较大，查询IO耗时较大，选择性select
        if self.request.method in permissions.SAFE_METHODS:
            # SELECT
            # `id`, `name`, `desc`, `workflow_id`, `flow_type`, `version_number`, `is_builtin`, `is_enabled`,
            # `is_draft`, `is_revocable`, `updated_by`, `update_at`
            # FROM `workflow_workflowversion`
            return self.queryset.values(*self.serializer_class.Meta.main_fields)

        # select * from
        return self.queryset

    def get_object_include_deleted(self, pk):
        """
        获取可能被删除掉的对象
        """
        try:
            obj = WorkflowVersion._objects.get(id=pk)
        except WorkflowVersion.DoesNotExist:
            raise Http404(
                "No %s matches the given query." % self.queryset.model._meta.object_name
            )
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_destroy(self, instance):
        """自定义删除前行为"""
        Trigger.objects.filter(
            source_type=SOURCE_TICKET, source_id=instance.id
        ).delete()
        super(WorkflowVersionViewSet, self).perform_destroy(instance)

    @action(detail=True, methods=["get"])
    def states(self, request, *args, **kwargs):
        """
        查询节点
        """
        flow = self.get_object_include_deleted(kwargs.get("pk"))
        if flow.engine_version == DEFAULT_ENGINE_VERSION:
            return Response(list(flow.states.values()))

        # old tickets
        axis_dict = {}
        for index, state in enumerate(flow.master):
            x = 200 + 200 * index
            y = 50 + 50 * index
            axis_dict[str(state["id"])] = {"y": y, "x": x}
        states = list(flow.states.values())
        for state in states:
            state.update(axis=axis_dict.get(str(state["id"])))
            if state["type"] == "ROUTER":
                state.update(type="NORMAL")
        return Response(states)

    @action(detail=True, methods=["get"])
    def transitions(self, request, *args, **kwargs):
        """
        查询连线：from_state_id为连线左端点，为空则返回左右连线
        """

        from_state_id = self.request.query_params.get("from_state_id")
        # can't get soft deleted flow version
        flow = self.get_object_include_deleted(pk=kwargs["pk"])
        if flow.engine_version == DEFAULT_ENGINE_VERSION:
            transitions_from = flow.get_transitions_from(from_state_id)
            # 统一接口格式
            return Response({"items": transitions_from})

        # old tickets
        transitions_from = list(flow.transitions.values())
        for t in transitions_from:
            t["from_state"] = t["from_state_id"]
            t["to_state"] = t["to_state_id"]
            if t.get("direction") == "BACK":
                t["axis"] = {"end": "Bottom", "start": "Bottom"}
            else:
                t["axis"] = {"end": "Top", "start": "Right"}
        return Response({"items": transitions_from})

    @action(detail=True, methods=["get"])
    def fields(self, request, *args, **kwargs):
        """
        查询字段：根据ticket状态id获取fields信息
        """

        # can't get soft deleted flow version
        # flow = self.get_object()
        flow = WorkflowVersion._objects.get(id=kwargs["pk"])

        state_id = self.request.query_params.get("state_id")
        fields = flow.get_state_fields(state_id)

        return Response(fields)

    @action(detail=True, methods=["post"])
    def restore(self, request, *args, **kwargs):
        """
        版本还原为模板
        """

        version = self.get_object()
        data = copy.deepcopy(version.__dict__)
        data.update(notify=list(version.notify.values_list("id", flat=True)))
        workflow, _, _ = Workflow.objects.restore(data, request.user.username)
        return Response({"id": workflow.id})

    @action(detail=False, methods=["post"])
    def batch_delete(self, request, *args, **kwargs):
        """批量删除操作"""

        id_list = [i for i in request.data.get("id").split(",") if i.isdigit()]

        will_deleted = self.queryset.filter(id__in=id_list)
        real_deleted = list(will_deleted.values_list("id", flat=True))
        will_deleted.delete()

        return Response(real_deleted)

    @action(detail=True, methods=["post"])
    def transition_lines(self, request, *args, **kwargs):
        """
        两节点之间的流转id信息
        需要指定起始节点和目标节点
        """
        flow = get_object_or_404(self.queryset, **kwargs)
        from_state_id = str(self.request.data.get("from_state_id"))
        to_state_id = str(self.request.data.get("to_state_id"))
        state_exists_validate(from_state_id, to_state_id)
        path = flow.get_transition_path(
            from_state_id=from_state_id, to_state_id=to_state_id
        )
        return Response(path)

    @action(detail=True, methods=["get"])
    def sla_validate(self, request, *args, **kwargs):
        """
        校验是否支持sla
        """

        flow = WorkflowVersion._objects.get(id=kwargs["pk"])
        flow.can_bind_sla()
        return Response({})

    @action(detail=True, methods=["get"])
    def post_state(self, request, *args, **kwargs):
        """
        校验是否支持sla
        """

        flow = WorkflowVersion.objects.get(id=kwargs["pk"])
        from_state_id = int(request.query_params["from_state_id"])

        return Response(flow.post_states(from_state_id))


class TransitionTemplateViewSet(BaseWorkflowElementViewSet):
    """线条模板"""

    serializer_class = TransitionTemplateSerializer
    queryset = Condition.objects.all()
    filter_fields = {
        "workflow": ["exact", "in"],
    }


class TableViewSet(component_viewsets.ModelViewSet):
    """基础模型视图"""

    # permission_classes = (IamAuthWithoutResourcePermit,)
    queryset = Table.objects.filter(is_builtin=True).order_by("-create_at")
    serializer_class = TableSerializer
    filter_fields = {
        "name": ["contains", "icontains"],
        "updated_by": ["contains"],
        "update_at": ["lte", "gte"],
    }
    ordering_fields = "create_at"

    def list(self, request, *args, **kwargs):
        """动态关闭分页"""
        if self.request.query_params.get("page_size") is None:
            self.pagination_class = None

        return super(TableViewSet, self).list(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def add_fields(self, request, *args, **kwargs):
        """添加字段模板"""
        fields = request.data.get("fields", [])
        template_fields_exists_validate(fields)
        table = self.get_object()
        table.add_fields(fields)
        return Response()

    @action(detail=True, methods=["post"])
    def remove_fields(self, request, *args, **kwargs):
        """删除字段模板"""
        fields = request.data.get("fields", [])
        table = self.get_object()
        table_remove_fiels_validate(fields, table)
        table.remove_fields(fields)
        return Response()


class TriggerViewSet(component_viewsets.ModelViewSet):
    """Workflow trigger viewset"""

    queryset = Trigger.objects.all()
    serializer_class = TriggerSerializer
    filter_fields = {"type": ["exact"], "workflow_id": ["exact"], "state_id": ["exact"]}

    def list(self, request, *args, **kwargs):
        """动态关闭分页"""
        if self.request.query_params.get("page_size") is None:
            self.pagination_class = None

        return super(TriggerViewSet, self).list(request, *args, **kwargs)


class TaskSchemaViewSet(DynamicListModelMixin, component_viewsets.ModelViewSet):
    """
    任务模版视图
    """

    queryset = TaskSchema.objects.filter(can_edit=True)
    serializer_class = TaskSchemaSerializer
    filter_fields = {
        "name": ["exact", "in", "contains", "icontains"],
        "component_type": ["exact"],
        "is_draft": ["exact"],
        "can_edit": ["exact"],
    }
    permission_classes = (TaskSchemaPermit,)
    pagination_class = None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # 出于用户使用场景, 任务模块字段排列操作和任务模板更新操作不放在同一个事务
        task_fields = request.data.pop("task_fields", {})
        if task_fields and task_fields.get("task_field_ids"):
            # task_fields正确格式: {"stage": "CREATE", "task_field_ids": [1, 2, 3]}
            if not (
                isinstance(task_fields, dict)
                and isinstance(task_fields["task_field_ids"], list)
            ):
                raise serializers.ValidationError(_("任务字段排序参数不合法，请联系管理员"))

            ordering = "FIELD(`id`, {})".format(
                ",".join(
                    [
                        "'{}'".format(task_field_id)
                        for task_field_id in task_fields["task_field_ids"]
                    ]
                )
            )
            task_fields_schema = TaskFieldSchema.objects.filter(
                task_schema_id=instance.id, stage=task_fields.get("stage")
            ).extra(select={"custom_order": ordering}, order_by=["custom_order"])

            for index, task_field_schema in enumerate(task_fields_schema):
                task_field_schema.sequence = index
            bulk_update(task_fields_schema, update_fields=["sequence"])

        return super(TaskSchemaViewSet, self).update(request, *args, **kwargs)

    @action(methods=["post"], detail=True)
    def clone(self, request, *args, **kwargs):
        """
        复制一个任务模版
        """
        src_instance = self.get_object()
        # 通过前端接口复制的任务模板，直接置为草稿，需要重新保存处理
        new_ids = TaskSchema.objects.clone([src_instance.id], is_draft=True)
        return Response(new_ids)

    def perform_destroy(self, instance):
        task_schema_delete_validate(instance)
        Trigger.objects.filter(source_type=SOURCE_TASK, source_id=instance.id).delete()
        super(TaskSchemaViewSet, self).perform_destroy(instance)

    @action(methods=["get"], detail=True)
    def variables(self, request, *args, **kwargs):
        """
        获取当前任务的参数
        """
        stage = request.query_params.get("stage")
        instance = self.get_object()
        all_variables = instance.get_variables(stage=stage)
        return Response(all_variables)


class TaskFieldSchemaViewSet(BaseFieldViewSet):
    """
    任务模版视图
    """

    queryset = TaskFieldSchema.objects.all().order_by("sequence")

    serializer_class = TaskFieldSchemaSerializer
    # permission_classes = (IamAuthWithoutResourcePermit,)
    filter_fields = {
        "name": ["exact", "in", "contains"],
        "stage": ["exact"],
        "task_schema_id": ["exact"],
    }
    pagination_class = None

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
import operator
from functools import reduce

from django.http import FileResponse
from django.utils.encoding import escape_uri_path
from django.utils.translation import ugettext as _
from django_bulk_update.helper import bulk_update
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.constants import (
    FIRST_ORDER,
    PRIORITY,
    PX_URGENCY,
    PY_IMPACT,
    SERVICE_LIST,
    SLA_MATRIX,
    GENERAL,
    OPEN,
    ORGANIZATION,
    DEFAULT_PROJECT_PROJECT_KEY,
)
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.drf.mixins import DynamicListModelMixin
from itsm.component.exceptions import ParamError, CatalogDeleteError
from itsm.component.exceptions import ServiceNotExist, TableNotExist
from itsm.component.utils.basic import create_version_number
from itsm.component.utils.misc import JsonEncoder
from itsm.service.models import (
    CatalogService,
    DictData,
    Favorite,
    OldSla,
    Service,
    ServiceCatalog,
    ServiceCategory,
    SysDict,
    FavoriteService,
    ServiceSla,
)
from itsm.component.drf import permissions as perm
from itsm.service.serializers import (
    CatalogServiceEditSerializer,
    CatalogServiceSerializer,
    DictDataSerializer,
    FavoriteSerializer,
    ServiceCatalogSerializer,
    ServiceCatalogShortcutSerializer,
    ServiceCategorySerializer,
    ServiceSerializer,
    SlaSerializer,
    SysDictSerializer,
    DictKeySerializer,
    ServiceConfigSerializer,
    ServiceListSerializer,
    ServiceImportSerializer,
)
from itsm.sla.models import PriorityMatrix
from mptt.exceptions import InvalidMove

from itsm.workflow.models import (
    Table,
    State,
    Workflow,
    Field,
    transaction,
    WorkflowVersion,
)
from itsm.workflow.validators import WorkflowPipelineValidator


class FavoriteModelViewSet(component_viewsets.ModelViewSet):
    """用户收藏视图"""

    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()
    pagination_class = None

    filter_fields = {
        "user": ["exact", "in"],
        "service": ["exact", "in"],
    }

    def get_queryset(self):
        """返回个人收藏的数据"""

        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """创建收藏时补充用户信息 """

        user = serializer.context.get("request").user
        serializer.save(user=user)


class CategoryModelViewSet(component_viewsets.ReadOnlyModelViewSet):
    serializer_class = ServiceCategorySerializer

    queryset = ServiceCategory.objects.filter(key__in=SERVICE_LIST).extra(
        select={"ordering": "FIELD(`key`, 'request', 'change', 'event', 'question')"},
        order_by=("ordering",),
    )
    pagination_class = None

    @action(detail=False, methods=["get"])
    def translate_view(self, request):
        """翻译视图"""
        data = dict(ServiceCategory.objects.all().values_list("key", "name"))

        # 对字典进行翻译
        translate_data = {}
        for key, value in data.items():
            translate_data[key] = _(value)

        return Response(translate_data)


class ServiceCatalogViewSet(component_viewsets.ModelViewSet):
    """服务目录视图"""

    serializer_class = ServiceCatalogSerializer
    queryset = ServiceCatalog.objects.filter(is_deleted=False).order_by(
        "-create_at", "level"
    )
    permission_classes = (perm.IamAuthProjectViewPermit,)
    filter_fields = {
        "id": ["exact", "in"],
        "key": ["exact", "in"],
        "level": ["exact", "in"],
        "name": ["exact", "contains", "startswith"],
    }

    def perform_destroy(self, instance):
        """
        如果该目录关联了服务，则无法删除
        """
        if CatalogService.objects.filter(catalog_id=instance.id).exists():
            raise CatalogDeleteError()
        super().perform_destroy(instance)

    def get_queryset(self):
        """BEP: 支持额外过滤参数[parent_key]"""

        parent_key = self.request.query_params.get("parent_key")

        # 根据父节点查询children
        if parent_key:
            queryset = ServiceCatalog.objects.filter(parent__key=parent_key)
        else:
            queryset = super(ServiceCatalogViewSet, self).get_queryset()

        return queryset

    @action(detail=False, methods=["get"])
    def translate_view(self, request):
        """目录树视图
        保留被删除的目录
        """
        data = dict(ServiceCatalog._objects.all().values_list("id", "name"))
        return Response(data)

    @action(detail=False, methods=["get"])
    def tree_view(self, request):
        """目录树视图"""
        key = request.query_params.get("key", "")
        show_deleted = request.query_params.get("show_deleted") == "true"
        project_key = request.query_params.get(
            "project_key", DEFAULT_PROJECT_PROJECT_KEY
        )
        tree_data = ServiceCatalog.tree_data(request, key, show_deleted, project_key)
        return Response(tree_data)

    @action(detail=True, methods=["get"])
    def children(self, request, *args, **kwargs):
        """下一级子目录"""
        obj = self.get_object()
        children = ServiceCatalogShortcutSerializer(obj.get_children(), many=True)
        return Response(children.data)

    @action(detail=True, methods=["post"])
    def move(self, request, *args, **kwargs):
        instance = self.get_object()
        new_order = request.data.get("new_order")
        if set(
            self.queryset.filter(parent=instance.parent).values_list("id", flat=True)
        ).difference(set(new_order)):
            raise serializers.ValidationError(_("当前排序列表参数不正确，清重试！"))
        ordering = "FIELD(`id`, {})".format(
            ",".join(["'{}'".format(v) for v in new_order])
        )

        catalogs = self.queryset.filter(parent=instance.parent).extra(
            select={"ordering": ordering}, order_by=["ordering"]
        )
        for order, obj in enumerate(catalogs):
            obj.order = FIRST_ORDER + order
        bulk_update(catalogs, update_fields=["order"])
        return Response()


class CatalogServiceViewSet(component_viewsets.ModelViewSet):
    """服务与目录的关联视图"""

    serializer_class = CatalogServiceSerializer
    queryset = CatalogService.objects.filter(is_deleted=False)
    permission_classes = ()
    filter_fields = {
        "id": ["exact", "in"],
        "catalog": ["exact", "in"],
        "service": ["exact", "in"],
    }

    @action(detail=False, methods=["get"])
    def get_services(self, request):
        """根据目录id查找服务列表"""

        catalog_id = request.query_params.get("catalog_id")
        name = request.query_params.get("name")
        service_key = request.query_params.get("service_key")
        is_valid = request.query_params.get("is_valid")

        if not catalog_id:
            raise ParamError("请提供合法的目录ID！")

        catalog_ids = ServiceCatalog.get_descendant_ids(catalog_id)
        catalog_services = CatalogService.objects.filter(
            catalog_id__in=catalog_ids
        ).order_by("order")
        if not catalog_services.exists():
            return Response([])
        service_ids = catalog_services.values_list("service_id", flat=True)
        query_params = dict(pk__in=service_ids)
        if is_valid is not None:
            query_params.update({"is_valid": is_valid})
        services = Service.objects.filter(**query_params).order_by("-update_at")

        # 支持额外过滤选项
        if name:
            services = services.filter(name__icontains=name)
        # 全局视图不过滤
        if service_key and service_key != "globalview":
            services = services.filter(key=service_key)

        services = services
        context = self.get_serializer_context()
        if request.query_params.get("page", "") and request.query_params.get(
            "page_size", ""
        ):
            page = self.paginate_queryset(services)
            serializer = ServiceSerializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = ServiceSerializer(services, many=True, context=context)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_services(self, request):
        """添加服务到目录"""

        serializer = CatalogServiceEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for service_id in serializer.validated_data.get("services"):
            CatalogService.objects.get_or_create(
                catalog_id=serializer.validated_data.get("catalog_id"),
                service_id=service_id,
            )

        return Response()

    @action(detail=False, methods=["post"])
    def remove_services(self, request):
        """从目录移除服务"""

        serializer = CatalogServiceEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        CatalogService.objects.filter(
            catalog_id=serializer.validated_data.get("catalog_id"),
            service_id__in=serializer.validated_data.get("services"),
        ).delete()

        return Response()

    @action(detail=True, methods=["post"])
    def move(self, request, *args, **kwargs):
        instance = self.get_object()
        new_order = request.data.get("new_order")
        catalog_service = CatalogService.objects.filter(catalog_id=instance.catalog_id)
        if set(catalog_service.values_list("service_id", flat=True)).difference(
            set(new_order)
        ):
            raise serializers.ValidationError(_("当前排序列表参数不正确，清重试！"))
        ordering = "FIELD(`service_id`, {})".format(
            ",".join(["'{}'".format(v) for v in new_order])
        )

        catalog_services = catalog_service.extra(
            select={"ordering": ordering}, order_by=["ordering"]
        )
        for order, obj in enumerate(catalog_services):
            obj.order = FIRST_ORDER + order
        bulk_update(catalog_services, update_fields=["order"])
        return Response()


class SlaViewSet(component_viewsets.ModelViewSet):
    """SLA视图集合"""

    serializer_class = SlaSerializer
    queryset = OldSla.objects.all()
    pagination_class = None
    permission_classes = (perm.IsAdmin,)

    @action(detail=False, methods=["get"])
    def get_level_choice(self, request, *args, **kwargs):
        return Response(
            [
                {"key": choice[0], "name": _(choice[1])}
                for choice in OldSla.level_choices
            ]
        )


class ServiceViewSet(component_viewsets.AuthModelViewSet):
    """服务项视图集合"""

    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = component_viewsets.AuthModelViewSet.permission_classes
    permission_free_actions = ["retrieve"]

    ordering_fields = ("name", "create_at", "update_at")
    ordering = ("-create_at",)

    filter_fields = {
        "is_valid": ["exact"],
        "name": ["exact", "contains", "startswith", "icontains"],
        "key": ["exact", "in"],
    }

    @staticmethod
    def perform_validate(serializer):
        """服务操作动作校验"""
        # 选择挂载SLA协议, 但不满足先决条件
        if "sla" in serializer.validated_data:
            flow_id = serializer.validated_data["workflow"]
            flow = WorkflowVersion.objects.get(id=flow_id)
            flow.can_bind_sla()

    def perform_create(self, serializer):
        self.perform_validate(serializer)
        super().perform_create(serializer)

    def perform_update(self, serializer):
        self.perform_validate(serializer)
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        # 先删除关联的SLA配置
        # TODO 删除服务在运行的SLA任务的处理方案
        # 删除相关的服务绑定
        CatalogService.objects.filter(service_id=instance.id).delete()
        ServiceSla.objects.filter(service_id=instance.id).delete()

        super().perform_destroy(instance)

    def get_queryset(self):
        """BEP: 支持额外过滤参数[no_classified]"""

        no_classified = self.request.query_params.get("no_classified")

        # 未分类的
        if no_classified:
            return Service.objects.exclude(
                id__in=CatalogService.objects.values_list("service", flat=True)
            )

        return super(ServiceViewSet, self).get_queryset().filter()

    def list(self, request, *args, **kwargs):
        project_key = request.query_params.get(
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

    @action(detail=False, methods=["get"], permission_classes=())
    def all(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        serializer_class = ServiceListSerializer
        queryset = Service.objects.filter(
            display_type__in=[OPEN, GENERAL, ORGANIZATION], is_valid=True
        ).values("id", "key", "name")
        conditions = Service.permission_filter(request.user.username)
        queryset = queryset.filter(reduce(operator.or_, conditions))
        serializer = serializer_class(queryset, many=True, context=context)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def batch_delete(self, request, *args, **kwargs):
        """批量删除操作
        TODO: 负责人校验
        """

        id_list = [i for i in request.data.get("id").split(",") if i.isdigit()]

        will_deleted = self.queryset.filter(id__in=id_list)
        real_deleted = list(will_deleted.values_list("id", flat=True))
        will_deleted.delete()

        # 关联删除服务SLA任务
        ServiceSla.objects.filter(service_id__in=id_list).delete()

        return Response(real_deleted)

    @action(detail=True, methods=["post"], permission_classes=())
    def operate_favorite(self, request, *args, **kwargs):
        service = self.get_object()
        favorite = request.data.get("favorite")
        if favorite:
            service.add_favorite(request.user.username)
        else:
            service.delete_favorite(request.user.username)
        return Response()

    @action(detail=False, methods=["get"], permission_classes=())
    def get_favorite_service(self, request, *args, **kwargs):
        favorite_service = FavoriteService.objects.filter(
            user=request.user.username
        ).values_list("service_id")
        service_ids = {service[0] for service in favorite_service}
        services = Service.objects.filter(id__in=service_ids)
        context = self.get_serializer_context()
        serializer = ServiceSerializer(services, many=True, context=context)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=())
    def import_from_template(self, request, *args, **kwargs):
        """
        从基础模型导入
        """
        table_id = request.data.get("table_id")
        if table_id is None:
            raise ParamError("table_id 不能为空")
        table = Table.objects.get(id=table_id)
        if not table:
            raise TableNotExist()
        service = self.get_object()
        with transaction.atomic():
            self.copy_fields_from_table(table, service)

        return Response()

    @action(detail=True, methods=["post"], permission_classes=())
    def import_from_service(self, request, *args, **kwargs):
        service = self.get_object()

        service_id = request.data.get("service_id")
        if service_id is None:
            raise ParamError("service_id 不能为空")
        from_service = Service.objects.get(id=service_id)
        if from_service is None:
            raise ServiceNotExist("未找到相对应的服务, service_id={}".format(service_id))
        with transaction.atomic():
            self.copy_fields_from_service(from_service, service)

        return Response()

    @action(detail=True, methods=["post"], permission_classes=())
    def source(self, request, *args, **kwargs):
        service = self.get_object()
        source = request.data.get("source", None)
        if source not in ["custom", "service", "template"]:
            raise ParamError("source 的值非法 ")
        with transaction.atomic():
            service.source = source
            service.save()

        return Response()

    def copy_fields_from_table(self, table, to_service):

        field_ids = []
        state = self.get_state_by_service(to_service)
        old_fields = state.fields
        for field in table.tag_data()["fields"]:
            field.pop("id")
            field.pop("project_key", None)
            field.pop("flow_type")
            field["workflow_id"] = to_service.workflow.workflow_id
            field["source"] = "TABLE"
            field_instance = Field.objects.create(**field)
            if field["key"] != "current_status":
                field_ids.append(field_instance.id)

        state.fields = field_ids
        state.save()

        Field.objects.filter(id__in=old_fields).delete()

    def copy_fields_from_service(self, from_service, to_service):
        field_ids = []
        state = self.get_state_by_service(to_service)
        from_service_fields = from_service.workflow.get_first_state_fields()

        old_fields = state.fields

        for field in from_service_fields:
            workflow_id = to_service.workflow.workflow_id
            if field["key"] == "bk_biz_id":
                workflow = Workflow.objects.get(id=workflow_id)
                workflow.is_biz_needed = True
                workflow.save()

            field.pop("id")
            field.pop("project_key", None)
            field["workflow_id"] = to_service.workflow.workflow_id
            field["state_id"] = state.id
            field.pop("api_info", None)
            field_ids.append(Field.objects.create(**field).id)

        state.fields = field_ids
        state.save()

        Field.objects.filter(id__in=old_fields).delete()

    @action(detail=True, methods=["post"])
    def sla_validate(self, request, *args, **kwargs):
        service = self.get_object()
        service.sla_validate()
        return Response()

    @action(detail=True, methods=["post"], permission_classes=())
    def save_configs(self, request, *args, **kwargs):
        """
        {
            "can_ticket_agency": true,
            "display_role": 8,
            "display_type": "display_type",
            "workflow_config": {
                "is_auto_approve": true,
                "is_revocable": true,
                "revoke_config": {
                    "type": 1,
                    "state": 0
                },
                "notify": [
                    {
                        "name": "企业微信",
                        "type": "WEIXIN"
                    },
                    {
                        "name": "邮件",
                        "type": "EMAIL"
                    },
                    {
                        "name": "SMS短信",
                        "type": "SMS"
                    }
                ],
                "notify_freq": 0,
                "notify_rule": "ONCE",
                "is_supervise_needed": true,
                "supervise_type": "EMPTY",
                "supervisor": "",
                "owners":"",
            }
        }
        """
        service = self.get_object()
        serializer = ServiceConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        configs = serializer.validated_data
        workflow_config = configs["workflow_config"]
        workflow_id = service.workflow.workflow_id
        WorkflowPipelineValidator(Workflow.objects.get(id=workflow_id))()

        with transaction.atomic():
            workflow = self.update_workflow_configs(workflow_id, workflow_config)
            configs["workflow_id"] = workflow.create_version().id
            service.update_service_configs(configs)
        context = self.get_serializer_context()
        return Response(self.serializer_class(instance=service, context=context).data)

    def update_workflow_configs(self, workflow_id, workflow_config):
        workflow = Workflow.objects.filter(id=workflow_id).first()
        workflow.update_workflow_configs(workflow_config)
        return workflow

    def get_state_by_service(self, service):
        """
        根据服务ID获取绑定的流程,从该流程的state顺序中获取提单的state
        """
        state_id = service.workflow.first_state["id"]
        state = State.objects.get(id=state_id)
        return state

    @action(detail=True, methods=["get"], permission_classes=())
    def export(self, request, *args, **kwargs):
        instance = self.get_object()
        # 统一导入导出格式为列表数据
        data = instance.tag_data()
        response = FileResponse(json.dumps(data, cls=JsonEncoder, indent=2))
        response["Content-Type"] = "application/octet-stream"
        # 中文文件名乱码问题
        response[
            "Content-Disposition"
        ] = "attachment; filename*=UTF-8''bk_itsm_{}_{}.json".format(
            escape_uri_path(instance.name),
            create_version_number(),
        )

        return response

    @action(detail=True, methods=["post"], permission_classes=())
    def clone(self, request, *args, **kwargs):
        instance = self.get_object()
        tag_data = instance.tag_data()
        service = Service.objects.clone(tag_data, request.user.username)
        service.bind_catalog(instance.catalog_id, instance.project_key)
        return Response(
            self.serializer_class(service, context=self.get_serializer_context()).data
        )

    @action(detail=False, methods=["post"])
    def imports(self, request, *args, **kwargs):
        data = json.loads(request.FILES.get("file").read())
        project_key = request.data.get("project_key", data.get("project_key"))
        data["project_key"] = project_key
        if isinstance(data, list):
            raise ParamError(_("2.5.9 版本之前的流程无法导入，请转换后在看，详情请看github"))
        ServiceImportSerializer(data=data).is_valid(raise_exception=True)
        catalog_id = request.data.get("catalog_id")
        service = Service.objects.clone(
            data, request.user.username, catalog_id=catalog_id
        )
        return Response(
            self.serializer_class(service, context=self.get_serializer_context()).data
        )


class SysDictViewSet(DynamicListModelMixin, component_viewsets.ModelViewSet):
    """数据字典视图集合"""

    serializer_class = SysDictSerializer
    queryset = SysDict.objects.filter(is_show=True).order_by("-is_builtin", "create_at")
    # permission_classes = (perm.IamAuthWithoutResourcePermit,)

    filter_fields = {
        "id": ["exact", "in"],
        "key": ["exact", "in", "contains", "startswith"],
        "name": ["exact", "contains", "startswith", "icontains"],
        "is_enabled": ["exact"],
    }

    @action(detail=False, methods=["post"])
    def batch_delete(self, request, *args, **kwargs):
        """批量删除操作"""

        id_list = [i for i in request.data.get("id").split(",") if i.isdigit()]

        will_deleted = self.queryset.filter(id__in=id_list)
        real_deleted = list(will_deleted.values_list("id", flat=True))
        will_deleted.delete()

        return Response(real_deleted)

    @action(detail=False, methods=["get"])
    def get_data_by_key(self, request, *args, **kwargs):
        """获取字典数据，支持两种视图：tree/list"""
        serializer = DictKeySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        kwargs = serializer.validated_data
        key = kwargs["key"]
        # request.query_params.get('service') 区分单据操作/流程线条创建
        if key in SLA_MATRIX and kwargs.get("service"):
            datas = PriorityMatrix.objects.get_dict_datas(kwargs.get("service"), key)
            return Response([data for data in datas if data["is_enabled"] is True])

        return Response(
            SysDict.get_data_by_key(
                key,
                kwargs.get("view_type"),
            )
        )


class SysDictDataViewSet(component_viewsets.ModelViewSet):
    """字典数据视图集合"""

    serializer_class = DictDataSerializer
    queryset = DictData.objects.all()
    # permission_classes = (perm.IamAuthWithoutResourcePermit,)

    filter_fields = {
        "id": ["exact", "in"],
        "dict_table": ["exact", "in"],
        "dict_table__key": ["exact"],
        "key": ["exact", "in", "contains", "startswith"],
        "name": ["exact", "contains", "startswith"],
    }
    ordering_fields = "order"

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None

        return super(SysDictDataViewSet, self).get_queryset()

    def perform_create(self, serializer):
        """捕捉级联数据的存储异常：如指定错误的父级"""
        try:
            super(SysDictDataViewSet, self).perform_create(serializer)
        except InvalidMove as e:
            raise ParamError(str(e))

    def perform_update(self, serializer):
        """更新时补充基础Model中的字段"""
        try:
            super(SysDictDataViewSet, self).perform_update(serializer)
        except InvalidMove as e:
            raise ParamError(str(e))

    def perform_destroy(self, instance):
        """删除时校验"""

        # 特殊类型的数据字段删除限制校验
        if instance.dict_table.key == PRIORITY:
            if PriorityMatrix.objects.filter(priority=instance.key).exists():
                raise serializers.ValidationError(
                    _("[{}] 已经被绑定，请先到优先级管理中解绑".format(instance.name))
                )
        elif instance.dict_table.key in [PX_URGENCY, PY_IMPACT]:
            tables = [
                "{}_{}".format(x, instance.dict_table.key)
                for x in ServiceCategory.get_service_keys(True)
            ]
            if DictData.objects.filter(
                dict_table__key__in=tables, key=instance.key
            ).exists():
                raise serializers.ValidationError(
                    _("[{}] 已经被勾选绑定，请先到优先级管理中解绑".format(instance.name))
                )

        instance.delete()

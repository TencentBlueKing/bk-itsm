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
from django.db import transaction
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from rest_framework.decorators import action
from rest_framework.response import Response

from blueapps.account.decorators import login_exempt

from itsm.component.decorators import custom_apigw_required
from itsm.component.utils.basic import dotted_name
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.drf.mixins import ApiGatewayMixin
from itsm.component.exceptions import ServicePartialError, ServiceInsertError
from itsm.component.exceptions import ObjectNotExist
from itsm.openapi.decorators import catch_openapi_exception
from itsm.openapi.service.serializers import (
    ServiceRetrieveSerializer,
    ServiceSerializer,
)
from itsm.service.models import CatalogService, Service, ServiceCatalog
from itsm.service.serializers import ServiceImportSerializer
from itsm.workflow.models import Workflow, WorkflowVersion
from itsm.component.constants import role, DEFAULT_PROJECT_PROJECT_KEY
from itsm.role.models import UserRole


@method_decorator(login_exempt, name="dispatch")
class ServiceViewSet(ApiGatewayMixin, component_viewsets.AuthModelViewSet):
    """
    服务项视图集合
    """

    queryset = Service.objects.filter(is_valid=True)
    serializer_class = ServiceSerializer
    permission_free_actions = (
        "get_services",
        "get_service_detail",
        "get_service_catalogs",
    )

    @action(detail=False, methods=["get"], serializer_class=ServiceSerializer)
    @catch_openapi_exception
    @custom_apigw_required
    def get_services(self, request):
        """
        服务项列表
        """
        queryset = self.queryset.all()

        catalog_id = request.query_params.get("catalog_id")
        if catalog_id:
            queryset = queryset.filter(
                id__in=CatalogService.objects.filter(catalog_id=catalog_id).values_list(
                    "service", flat=True
                )
            )

        service_type = request.query_params.get("service_type")
        if service_type:
            queryset = queryset.filter(key=service_type)

        display_type = request.query_params.get("display_type")
        if display_type:
            queryset = queryset.filter(display_type=display_type)

        display_role = request.query_params.get("display_role")
        if display_role:
            queryset = queryset.filter(display_role__contains=dotted_name(display_role))

        return Response(self.serializer_class(queryset, many=True).data)

    @action(detail=False, methods=["get"], serializer_class=ServiceRetrieveSerializer)
    @catch_openapi_exception
    @custom_apigw_required
    def get_service_detail(self, request):
        """
        服务项详情
        """
        try:
            service = self.queryset.get(pk=request.query_params.get("service_id"))
        except Service.DoesNotExist:
            return Response(
                {
                    "result": False,
                    "code": ObjectNotExist.ERROR_CODE_INT,
                    "data": None,
                    "message": ObjectNotExist.MESSAGE,
                }
            )

        return Response(self.serializer_class(service).data)

    @action(detail=False, methods=["get"])
    @catch_openapi_exception
    @custom_apigw_required
    def get_service_catalogs(self, request):
        """
        服务目录
        """

        project_key = request.query_params.get(
            "project_key", DEFAULT_PROJECT_PROJECT_KEY
        )

        has_service = request.query_params.get("has_service")
        service_key = request.query_params.get("service_key")
        name = request.query_params.get("name")

        # 返回绑定服务项或者根据service_key过滤
        if has_service == "true" or service_key:
            return Response(
                ServiceCatalog.open_api_tree_data(
                    service_key=service_key, project_key=project_key
                )
            )

        if name:
            nodes = ServiceCatalog.objects.filter(
                name=name, is_deleted=False, project_key=project_key
            )
            return Response([ServiceCatalog.open_api_subtree(node) for node in nodes])

        roots = ServiceCatalog.objects.filter(
            level=0, is_deleted=False, project_key=project_key
        )
        return Response([ServiceCatalog.open_api_subtree(root) for root in roots])

    @action(detail=False, methods=["get"])
    @catch_openapi_exception
    @custom_apigw_required
    def get_service_roles(self, request):
        """
        服务目录
        """

        service_id = request.query_params.get("service_id")
        ticket_creator = request.query_params.get("ticket_creator")
        try:
            show_first_state = bool(int(request.query_params.get("all", 0)))
        except Exception:
            show_first_state = False

        workflow = self.queryset.get(id=service_id).workflow
        # 获取第一个提单节点的id
        first_state = workflow.first_state
        # 根据提单节点 通过路径 乡下搜索，获得正确的state顺序
        states = workflow.post_states(first_state["id"])

        # 全量数据下，将提单节点插入第一个
        if show_first_state:
            states.insert(0, first_state)

        states_roles = []
        for state in states:
            if state["type"] in ["START", "END"]:
                continue

            use_creator = state["processors_type"] in [
                role.STARTER_LEADER,
                role.STARTER,
            ]
            members = ticket_creator if use_creator else state["processors"]
            if not members:
                processors = ""
            else:
                processors = ",".join(
                    UserRole.get_users_by_type(-1, state["processors_type"], members)
                )
            states_roles.append(
                {
                    "id": state["id"],
                    "name": state["name"],
                    "processors": processors,
                    "processors_type": state["processors_type"],
                    "sign_type": "and" if state["is_multi"] else "or",
                }
            )

        return Response(states_roles)

    @action(detail=False, methods=["post"])
    @catch_openapi_exception
    @custom_apigw_required
    def insert_service(self, requests):
        """
        插入或新服务和流程
        :param requests:
        :return:
        """
        services = requests.data.get("services", [])
        flows = requests.data.get("flows", [])
        for new_flow in flows:
            Workflow.objects.restore(data=new_flow)
        if services:
            insert_result = Service.objects.insert_services(services)
            if not insert_result.get("result"):
                raise ServicePartialError(insert_result.get("message"))
        return Response()

    @action(detail=False, methods=["post"])
    @catch_openapi_exception
    @custom_apigw_required
    def import_service(self, request):
        ser = ServiceImportSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        service_data = ser.data
        with transaction.atomic():
            workflow_tag_data = service_data.pop("workflow")
            workflow = Workflow.objects.restore(
                workflow_tag_data, request.user.username
            )[0]
            version = workflow.create_version()
            service_data["workflow_id"] = version.id
            if Service.validate_service_name(service_data["name"]):
                raise ServiceInsertError(_("导入失败，服务名称已经存在"))

            catalog_id = service_data.pop("catalog_id", None)
            service = Service.objects.create(**service_data)
            service.bind_catalog(catalog_id, service.project_key)
        return Response(
            self.serializer_class(service, context=self.get_serializer_context()).data
        )

    @action(detail=False, methods=["post"])
    @catch_openapi_exception
    @custom_apigw_required
    def update_service(self, request):
        data = request.data
        ser = ServiceImportSerializer(data=data)
        ser.is_valid(raise_exception=True)
        data = ser.data
        with transaction.atomic():
            service_id = data.pop("id")
            service = Service.objects.get(id=service_id)
            # 删除旧的服务
            Workflow.objects.filter(id=service.workflow.workflow_id).delete()
            WorkflowVersion.objects.filter(id=service.workflow.id).delete()
            # 导入新的服务
            workflow_tag_data = data.pop("workflow")
            workflow = Workflow.objects.restore(
                workflow_tag_data, request.user.username
            )[0]
            version = workflow.create_version()
            data["workflow_id"] = version.id
            if Service.objects.filter(~Q(id=service_id), name=data["name"]).exists():
                raise ServiceInsertError(_("更新失败，服务名称已经存在"))
            catalog_id = data.pop("catalog_id", None)
            Service.objects.filter(id=service_id).update(**data)
            # 重新绑定目录
            service.bind_catalog(catalog_id, service.project_key)
            service.refresh_from_db()
        return Response(
            self.serializer_class(service, context=self.get_serializer_context()).data
        )

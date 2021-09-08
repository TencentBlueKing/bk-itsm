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
import traceback
from functools import wraps

from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from blueapps.account.decorators import login_exempt
from common.log import logger
from common.cipher import AESVerification
from common.redis import Cache
from itsm.component.constants import (
    API,
    QUEUEING,
    RUNNING,
    SUSPEND_OPERATE,
    TERMINATE_OPERATE,
    TRANSITION_OPERATE,
    UNSUSPEND_OPERATE,
    WITHDRAW_OPERATE,
    APPROVE_RESULT,
    INVISIBLE,
    PROCESS_RUNNING,
)
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.drf.mixins import ApiGatewayMixin
from itsm.component.drf.pagination import OpenApiPageNumberPagination
from itsm.component.exceptions import (
    OperateTicketError,
    ParamError,
    ServerError,
    TicketNotFoundError,
)
from itsm.component.utils.drf import format_validation_message
from itsm.openapi.ticket.serializers import (
    TicketCreateSerializer,
    TicketListSerializer,
    TicketLogsSerializer,
    TicketNodeOperateSerializer,
    TicketOperateSerializer,
    TicketProceedSerializer,
    TicketRetrieveSerializer,
    TicketStatusSerializer,
    TicketResultSerializer,
    TicketFilterSerializer,
)
from itsm.openapi.ticket.validators import (
    openapi_operate_validate,
    openapi_suspend_validate,
    openapi_unsuspend_validate,
)
from itsm.service.models import ServiceCatalog, Service
from itsm.ticket.models import Ticket, TicketField, SignTask
from itsm.ticket.serializers import TicketList, TicketSerializer
from itsm.ticket.tasks import start_pipeline
from itsm.ticket.validators import terminate_validate, withdraw_validate


def catch_ticket_operate_exception(view_func):
    """单据处理接口的公共异常捕捉"""

    # @wraps(view_func, assigned=available_attrs(view_func))
    @wraps(view_func)
    def __wrapper(self, request, *args, **kwargs):
        try:
            return view_func(self, request, *args, **kwargs)
        except Ticket.DoesNotExist:
            return Response(
                {
                    "result": False,
                    "code": TicketNotFoundError.ERROR_CODE_INT,
                    "data": None,
                    "message": TicketNotFoundError.MESSAGE,
                }
            )
        except ServerError as e:
            # 捕捉drf序列化检验的自定义错误
            return Response(
                {
                    "result": False,
                    "code": e.code_int,
                    "data": None,
                    "message": e.message,
                }
            )
        except ValidationError as e:
            # 捕捉drf序列化检验原始错误
            return Response(
                {
                    "result": False,
                    "code": ParamError.ERROR_CODE_INT,
                    "data": None,
                    "message": format_validation_message(e),
                }
            )
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(
                {
                    "result": False,
                    "code": OperateTicketError.ERROR_CODE_INT,
                    "data": None,
                    "message": _("接口异常，请检查请求参数: {}").format(e),
                }
            )

    return __wrapper


@method_decorator(login_exempt, name="dispatch")
class TicketViewSet(ApiGatewayMixin, component_viewsets.ModelViewSet):
    """
    工单视图
    """

    queryset = Ticket.objects.filter(is_deleted=False, is_draft=False)
    serializer_class = TicketSerializer
    pagination_class = OpenApiPageNumberPagination

    def custom_filter_queryset(self, request, username):
        """构造查询queryset"""
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.exists():
            filter_serializer = TicketFilterSerializer(data=request.query_params)
            filter_serializer.is_valid(raise_exception=True)
            kwargs = filter_serializer.validated_data
            queryset = Ticket.objects.get_tickets(username, queryset, **kwargs)
        return queryset

    @action(detail=False, methods=["get"], serializer_class=TicketStatusSerializer)
    def get_ticket_status(self, request):
        """
        单据状态，支持根据单据sn查询
        """

        try:
            ticket = self.queryset.get(sn=request.query_params.get("sn"))
        except Ticket.DoesNotExist:
            return Response(
                {
                    "result": False,
                    "code": TicketNotFoundError.ERROR_CODE_INT,
                    "data": None,
                    "message": TicketNotFoundError.MESSAGE,
                }
            )

        return Response(self.serializer_class(ticket).data)

    @action(detail=False, methods=["post"], serializer_class=TicketResultSerializer)
    def ticket_approval_result(self, request):
        """
        单据状态，支持根据单据sn查询
        """

        try:
            sn_list = request.data.get("sn")
            tickets = self.queryset.filter(sn__in=sn_list)
            Cache().hdel("callback_error_ticket", *sn_list)
        except Ticket.DoesNotExist:
            return Response(
                {
                    "result": False,
                    "code": TicketNotFoundError.ERROR_CODE_INT,
                    "data": None,
                    "message": TicketNotFoundError.MESSAGE,
                }
            )

        return Response(self.serializer_class(tickets, many=True).data)

    @action(detail=False, methods=["post"], serializer_class=TicketListSerializer)
    def get_tickets(self, request):
        """
        获取单据列表
        """

        queryset = self.queryset
        sns = request.data.get("sns", [])
        creator = request.data.get("creator", "")
        create_at__lte = request.data.get("create_at__lte", "")
        create_at__gte = request.data.get("create_at__gte", "")
        end_at__lte = request.data.get("end_at__lte", "")
        end_at__gte = request.data.get("end_at__gte", "")
        username = request.data.get("username", "")
        service_id__in = request.data.get("service_id__in", [])
        bk_biz_id__in = request.data.get("bk_biz_id__in", [])

        if sns:
            queryset = queryset.filter(sn__in=sns)
        if creator:
            queryset = queryset.filter(creator=creator)
        if create_at__lte:
            queryset = queryset.filter(create_at__lte=create_at__lte)
        if create_at__gte:
            queryset = queryset.filter(create_at__gte=create_at__gte)
        if service_id__in:
            queryset = queryset.filter(service_id__in=service_id__in)
        if end_at__lte:
            queryset = queryset.filter(end_at__lte=end_at__lte)
        if end_at__gte:
            queryset = queryset.filter(end_at__gte=end_at__gte)
        if bk_biz_id__in:
            queryset = queryset.filter(bk_biz_id__in=bk_biz_id__in)

        if username:
            role_filter = Ticket.objects.build_todo_role_filter(username)
            queryset = queryset.filter(current_status=PROCESS_RUNNING).filter(
                role_filter
            )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], serializer_class=TicketRetrieveSerializer)
    def get_ticket_info(self, request):
        """
        获取单据详情
        """

        try:
            ticket = self.queryset.get(sn=request.query_params.get("sn"))
        except Ticket.DoesNotExist:
            return Response(
                {
                    "result": False,
                    "code": TicketNotFoundError.ERROR_CODE_INT,
                    "data": None,
                    "message": TicketNotFoundError.MESSAGE,
                }
            )

        return Response(self.serializer_class(ticket).data)

    @action(detail=False, methods=["get"], serializer_class=TicketLogsSerializer)
    def get_ticket_logs(self, request):
        """
        获取单据日志
        """

        try:
            ticket = self.queryset.get(sn=request.query_params.get("sn"))
        except Ticket.DoesNotExist:
            return Response(
                {
                    "result": False,
                    "code": TicketNotFoundError.ERROR_CODE_INT,
                    "data": None,
                    "message": TicketNotFoundError.MESSAGE,
                }
            )

        return Response(self.serializer_class(ticket).data)

    @action(detail=False, methods=["post"])
    @catch_ticket_operate_exception
    def create_ticket(self, request):
        """
        创建单据
        service_id: 服务id
        fields: 提单节点字段信息
        """
        # 创建单据
        data = copy.deepcopy(request.data)
        fast_approval = data.pop("fast_approval", False)
        if fast_approval:
            data["catalog_id"] = ServiceCatalog.objects.get(
                key="approve_service_catalog"
            ).id
            data["service_id"] = Service.objects.get(
                name="内置审批服务", display_type=INVISIBLE
            ).id
            data["service_type"] = "request"
        serializer = TicketCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.do_after_create(
            data["fields"], request.data.get("from_ticket_id", None)
        )
        start_pipeline.apply_async([instance])
        return Response(
            {"sn": instance.sn, "id": instance.id, "ticket_url": instance.pc_ticket_url}
        )

    @action(detail=False, methods=["post"])
    @catch_ticket_operate_exception
    def operate_node(self, request):
        """
        处理单据节点（提交、认领、派单、转单、终止）
        """
        sn = request.data.get("sn")
        state_id = request.data.get("state_id")
        action_type = request.data.get("action_type")
        operator = request.data.get("operator")

        ticket = Ticket.objects.get(sn=sn)
        openapi_operate_validate(operator, ticket, state_id, action_type)

        if action_type == TRANSITION_OPERATE:
            # 重点参数校验：处理人/单据字段
            serializer = TicketProceedSerializer(
                data=request.data,
                context={"ticket": ticket, "state_id": state_id, "request": request},
            )
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            ticket.node_status.filter(state_id=state_id).update(status=QUEUEING)
            res = ticket.activity_callback(
                state_id, data["operator"], data["fields"], API
            )
            if not res.result:
                logger.warning(
                    "callback error， current state id %s, error message: %s， field params %s"
                    % (state_id, res.message, data["fields"])
                )
                ticket.node_status.filter(state_id=state_id).update(status=RUNNING)
                raise OperateTicketError(res.message)

        elif action_type == TERMINATE_OPERATE:
            # 重点参数校验：处理人/单据字段 --- 这一段看起来是无效的才对
            action_message = request.data.get("action_message")
            terminate_validate(operator, ticket, state_id, action_message)

            ticket.terminate(
                state_id,
                terminate_message=action_message,
                operator=operator,
                source=API,
            )
        else:
            # 重点参数校验：action_type/processors_type/processors
            serializer = TicketNodeOperateSerializer(
                request=request, ticket=ticket, operator=operator
            )
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            operator = data.pop("operator")
            current_node = data.pop("current_node")
            current_node.set_next_action(operator, **data)

        return Response()

    @action(detail=False, methods=["post"])
    @catch_ticket_operate_exception
    def operate_ticket(self, request):
        """
        处理单据（挂起、恢复、撤销）
        """
        sn = request.data.get("sn")
        operator = request.data.get("operator")
        action_type = request.data.get("action_type")
        ticket = Ticket.objects.get(sn=sn)

        if action_type not in [
            WITHDRAW_OPERATE,
            TERMINATE_OPERATE,
            SUSPEND_OPERATE,
            UNSUSPEND_OPERATE,
        ]:
            # 非单据的操作类型，直接返回操作失败
            return Response(
                {
                    "result": False,
                    "code": OperateTicketError.ERROR_CODE_INT,
                    "data": None,
                    "message": "{}，不支持的操作类型: {}".format(
                        OperateTicketError.MESSAGE, action_type
                    ),
                }
            )

        if action_type == WITHDRAW_OPERATE:
            withdraw_validate(operator, ticket)
        else:
            openapi_operate_validate(operator, ticket)

        if action_type == SUSPEND_OPERATE:
            openapi_suspend_validate(ticket)
        elif action_type == UNSUSPEND_OPERATE:
            openapi_unsuspend_validate(ticket)

        serializer = TicketOperateSerializer(
            data=request.data, context={"ticket": ticket}
        )
        serializer.is_valid(raise_exception=True)
        operator = serializer.validated_data["operator"]
        action_message = serializer.validated_data["action_message"]

        # dispatch action
        if action_type == SUSPEND_OPERATE:
            ticket.suspend(action_message, operator)
        elif action_type == UNSUSPEND_OPERATE:
            ticket.unsuspend(operator)
        elif action_type == WITHDRAW_OPERATE:
            ticket.withdraw(operator, source=API)
        elif action_type == TERMINATE_OPERATE:
            ticket.close(close_status="TERMINATED", operator=operator)

        return Response()

    @action(detail=False, methods=["post"])
    @catch_ticket_operate_exception
    def proceed_approval(self, request):
        # 审批节点的处理
        ticket_id = request.data.get("process_inst_id")
        state_id = request.data.get("activity")
        ticket = self.queryset.get(sn=ticket_id)

        node_fields = TicketField.objects.filter(state_id=state_id, ticket_id=ticket.id)
        fields = []
        remarked = False
        for field in node_fields:
            if field.meta.get("code") == APPROVE_RESULT:
                fields.append(
                    {
                        "id": field.id,
                        "key": field.key,
                        "type": field.type,
                        "choice": field.choice,
                        "value": request.data.get("submit_action"),
                    }
                )
            else:
                if not remarked:
                    fields.append(
                        {
                            "id": field.id,
                            "key": field.key,
                            "type": field.type,
                            "choice": field.choice,
                            "value": request.data.get("submit_opinion"),
                        }
                    )
                    remarked = True

        logger.info("proceed_approval request fields is {}".format(fields))
        node_status = ticket.node_status.get(state_id=state_id)
        SignTask.objects.update_or_create(
            status_id=node_status.id,
            processor=request.data.get("handler"),
            defaults={
                "status": "RUNNING",
            },
        )
        res = ticket.activity_callback(
            state_id, request.data.get("handler"), fields, API
        )
        if not res.result:
            logger.warning(
                "callback error， current state id %s, error message: %s"
                % (state_id, res.message)
            )
            ticket.node_status.filter(state_id=state_id).update(status=RUNNING)
            raise OperateTicketError(res.message)
        return Response()

    @action(detail=False, methods=["get"])
    @catch_ticket_operate_exception
    def get_tickets_by_user(self, request):
        # 初始化serializer的上下文
        username = request.query_params.get("user", None)
        if username is None:
            raise ParamError("user 为必填项")
        queryset = self.custom_filter_queryset(request, username)
        page = self.paginate_queryset(queryset)
        if page is not None:
            data = TicketList(
                page, username, token=request.query_params.get("token", "")
            ).to_client_representation()
            return self.get_paginated_response(data)

        # BEP: get_serializer instead of serializer class directly
        data = TicketList(
            queryset, username=username, token=request.query_params.get("token", "")
        ).to_client_representation()
        return Response(data)

    @action(detail=False, methods=["post"], url_path="token/verify")
    @catch_ticket_operate_exception
    def verify(self, request):
        token = request.data.get("token", "")
        message = settings.APP_CODE + "_" + settings.SECRET_KEY
        return Response(
            {
                "is_passed": AESVerification.verify(
                    message, bytes(token, encoding="utf-8")
                )
            }
        )

    @action(detail=False, methods=["get"])
    @catch_ticket_operate_exception
    def callback_failed_ticket(self, request):
        return Response(Cache().hkeys("callback_error_ticket"))

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
from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
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
from itsm.component.decorators import custom_apigw_required
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.drf.mixins import ApiGatewayMixin
from itsm.component.drf.pagination import OpenApiPageNumberPagination
from itsm.component.exceptions import (
    OperateTicketError,
    ParamError,
    TicketNotFoundError,
    CreateTicketError,
)
from itsm.openapi.decorators import catch_openapi_exception
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
    ProceedApprovalSerializer,
    CommentSerializer,
    DynamicFieldSerializer,
    TicketComplexLogsSerializer,
    TicketApproveSerializer,
)
from itsm.openapi.ticket.utils import edit_ticket_field
from itsm.openapi.ticket.validators import (
    openapi_operate_validate,
    openapi_suspend_validate,
    openapi_unsuspend_validate,
)
from itsm.service.models import ServiceCatalog, Service
from itsm.ticket.models import (
    Ticket,
    TicketField,
    SignTask,
    TicketComment,
    Status,
)
from itsm.ticket.serializers import TicketList, TicketSerializer
from itsm.ticket.tasks import start_pipeline
from itsm.ticket.validators import (
    terminate_validate,
    withdraw_validate,
)


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
    @custom_apigw_required
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
    @custom_apigw_required
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
    @custom_apigw_required
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
        current_status__in = request.data.get("current_status__in", [])
        tag = request.data.get("tag", None)
        project_key = request.data.get("project_key", None)

        if project_key:
            queryset = queryset.filter(project_key=project_key)
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
        if current_status__in:
            queryset = queryset.filter(current_status__in=current_status__in)
        if tag:
            queryset = queryset.filter(tag=tag)

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

    @action(detail=False, methods=["post"])
    @custom_apigw_required
    def edit_field(self, request, *args, **kwargs):
        """
        单个修改字段值
        """

        fields = request.data.get("fields")
        sn = request.data.get("sn")
        operator = request.data.get("operator")
        with transaction.atomic():
            for field in fields:
                logger.info(
                    "edit_field-> start update field， key={}, sn={}".format(
                        field.get("key"), sn
                    )
                )
                edit_ticket_field(field, sn=sn, username=operator)

        return Response()

    @action(detail=False, methods=["get"], serializer_class=TicketRetrieveSerializer)
    @custom_apigw_required
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

    @action(detail=False, methods=["get"])
    @custom_apigw_required
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

        show_type = request.query_params.get("show_type", "simple")
        serializer_class = TicketLogsSerializer
        if show_type == "complex":
            serializer_class = TicketComplexLogsSerializer

        return Response(serializer_class(ticket).data)

    @action(detail=False, methods=["post"], serializer_class=TicketApproveSerializer)
    @catch_openapi_exception
    @custom_apigw_required
    def approve(self, request):

        ser = TicketApproveSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        sn = request.data.get("sn")
        state_id = request.data.get("state_id")
        approver = request.data.get("approver")
        approve_action = request.data.get("action")
        remark = request.data.get("remark")
        ticket = Ticket.objects.get(sn=sn)
        # 3.判断当前节点是否是RUNNING状态，否则通知
        current_status = Status.objects.get(state_id=state_id, ticket_id=ticket.id)
        if current_status.status != "RUNNING":
            raise OperateTicketError("单据审批失败，单据当前状态非RUNNING")

        node_status = ticket.node_status.get(state_id=state_id)

        if node_status.type != "APPROVAL":
            raise OperateTicketError("单据审批失败，目标节点{}不是审批节点".format(node_status.name))

        if not node_status.can_sign_state_operate(approver):
            raise OperateTicketError("单据审批失败，{}不是当前节点的审批人，无法审批".format(approver))

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
                        "value": approve_action,
                    }
                )
            else:
                if remarked:
                    break
                # 如果审批通过同时该字段是可选的，说明目标字段是审批通过备注
                if approve_action == "true" and field.validate_type == "OPTION":
                    fields.append(
                        {
                            "id": field.id,
                            "key": field.key,
                            "type": field.type,
                            "choice": field.choice,
                            "value": remark,
                        }
                    )
                    remarked = True
                # 如果审批通过同时该字段是可选的，说明目标字段是审批拒绝备注
                if approve_action == "false" and field.validate_type == "REQUIRE":
                    fields.append(
                        {
                            "id": field.id,
                            "key": field.key,
                            "type": field.type,
                            "choice": field.choice,
                            "value": remark,
                        }
                    )
                    remarked = True

        logger.info("approve request fields is {}".format(fields))

        SignTask.objects.update_or_create(
            status_id=node_status.id,
            processor=approver,
            defaults={
                "status": "RUNNING",
            },
        )
        res = ticket.activity_callback(state_id, approver, fields, API)
        if not res.result:
            logger.warning(
                "callback error， current state id %s, error message: %s"
                % (state_id, res.message)
            )
            ticket.node_status.filter(state_id=state_id).update(status=RUNNING)
            raise OperateTicketError(
                "单据操作失败，callback error, message={}".format(res.message)
            )

        return Response()

    @action(detail=False, methods=["post"])
    @catch_openapi_exception
    @custom_apigw_required
    def create_ticket(self, request):
        """
        创建单据
        service_id: 服务id
        fields: 提单节点字段信息
        """
        # 创建单据
        data = copy.deepcopy(request.data)
        logger.info("[openapi][create_ticket]-> 正在开始创建单据, request_data={}".format(data))
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

        dynamic_fields = data.get("dynamic_fields", [])

        if dynamic_fields:
            ser = DynamicFieldSerializer(data=dynamic_fields, many=True)
            ser.is_valid(raise_exception=True)
            dynamic_fields = ser.data

        try:
            # 创建额外的全局字段
            instance.create_dynamic_fields(dynamic_fields)
            instance.do_after_create(
                data["fields"], request.data.get("from_ticket_id", None)
            )
            start_pipeline.apply_async([instance])
        except Exception as e:
            logger.exception(
                "[openapi][create_ticket]-> 单据创建失败， 错误原因 error={}".format(e)
            )
            instance.delete()
            # 删除单据字段
            keys = [field["key"] for field in dynamic_fields]
            TicketField.objects.filter(ticket_id=instance.id, key__in=keys).delete()
            raise CreateTicketError()

        logger.info(
            "[openapi][create_ticket]-> 单据创建成功，sn={}, request_data={}".format(
                instance.sn, data
            )
        )

        return Response(
            {"sn": instance.sn, "id": instance.id, "ticket_url": instance.pc_ticket_url}
        )

    @action(detail=False, methods=["post"])
    @catch_openapi_exception
    @custom_apigw_required
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
    @catch_openapi_exception
    @custom_apigw_required
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
    @catch_openapi_exception
    def proceed_approval(self, request):
        # 审批节点的处理
        serializer = ProceedApprovalSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        ticket_id = serializer.validated_data["process_inst_id"]
        state_id = serializer.validated_data["activity"]
        try:
            ticket = Ticket.objects.get(sn=ticket_id)
        except Exception:
            raise ValidationError("process_inst_id = {} 对应的单据不存在！".format(ticket_id))
        try:
            node_fields = TicketField.objects.filter(
                state_id=state_id, ticket_id=ticket.id
            )
        except Exception:
            raise ValidationError(
                "activity = {}, process_inst_id = {} 对应的表单字段不存在！".format(
                    state_id, ticket_id
                )
            )
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
                        "value": serializer.validated_data["submit_action"],
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
                            "value": serializer.validated_data["submit_opinion"],
                        }
                    )
                    remarked = True

        logger.info("proceed_approval request fields is {}".format(fields))
        node_status = ticket.node_status.get(state_id=state_id)
        SignTask.objects.update_or_create(
            status_id=node_status.id,
            processor=serializer.validated_data["handler"],
            defaults={
                "status": "RUNNING",
            },
        )
        res = ticket.activity_callback(
            state_id, serializer.validated_data["handler"], fields, API
        )
        if not res.result:
            logger.warning(
                "callback error， current state id %s, error message: %s"
                % (state_id, res.message)
            )
            ticket.node_status.filter(state_id=state_id).update(status=RUNNING)
            raise OperateTicketError(res.message)
        return Response()

    @action(detail=False, methods=["post"])
    @catch_openapi_exception
    def proceed_fast_approval(self, request):
        """
        处理快速审批请求
        """
        if settings.RUN_VER == "ieod":
            from platform_config.ieod.bkchat.utils import proceed_fast_approval
        else:
            from platform_config.open.bkchat.utils import proceed_fast_approval
        return proceed_fast_approval(request)

    @action(detail=False, methods=["get"])
    @catch_openapi_exception
    @custom_apigw_required
    def get_tickets_by_user(self, request):
        # 初始化serializer的上下文
        username = (
            request.query_params.get("username")
            if request.query_params.get("username", None)
            else request.query_params.get("user", None)
        )
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
    @catch_openapi_exception
    @custom_apigw_required
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

    @action(
        detail=False,
        methods=["post"],
    )
    @catch_openapi_exception
    @custom_apigw_required
    def comment(self, request, *args, **kwargs):
        """新增评论"""
        ser = CommentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.data
        ticket_comment = TicketComment.objects.get(ticket_id=data["ticket_id"])
        ticket_comment.stars = data["stars"]
        ticket_comment.comments = data["comments"]
        ticket_comment.source = "API"
        ticket_comment.save()
        ticket_comment.creator = data["operator"]
        return Response()

    @action(detail=False, methods=["get"])
    @catch_openapi_exception
    @custom_apigw_required
    def callback_failed_ticket(self, request):
        return Response(Cache().hkeys("callback_error_ticket"))

    @action(detail=False, methods=["post"])
    @catch_openapi_exception
    @custom_apigw_required
    def add_follower(self, request, *args, **kwargs):
        """关注or取关"""
        sn = request.data.get("sn")
        users = request.data.get("users").split(",")
        try:
            ticket = Ticket.objects.get(sn=sn)
        except Ticket.DoesNotExist:
            raise ParamError("sn[{}]对应的单据不存在！".format(sn))
        attention = request.data.get("attention")
        with transaction.atomic():
            if attention:
                for user in users:
                    ticket.add_follower(user)
            else:
                for user in users:
                    ticket.delete_follower(user)
        return Response()

    @action(detail=False, methods=["get"])
    @catch_openapi_exception
    @custom_apigw_required
    def get_approver(self, request, *args, **kwargs):
        """
        获取某个节点的处理人
        """
        sn = request.query_params.get("sn")
        state_id = request.query_params.get("state_id")
        try:
            ticket = Ticket.objects.get(sn=sn)
        except Ticket.DoesNotExist:
            raise ParamError("sn[{}]对应的单据不存在！".format(sn))

        status = Status.objects.get(ticket_id=ticket.id, state_id=state_id)
        sign_tasks = SignTask.objects.filter(status_id=status.id)
        processors = [task.processor for task in sign_tasks]
        return Response({"approver": ",".join(processors)})

    @action(detail=False, methods=["get"])
    @catch_openapi_exception
    @custom_apigw_required
    def get_approve_node_result(self, request, *args, **kwargs):
        """
        获取审批节点详情
        return {
            "节点名称"
            "审批人",
            "审批结果"，
            "审批备注"
        }
        """
        sn = request.query_params.get("sn")
        state_id = request.query_params.get("state_id")

        try:
            ticket = Ticket.objects.get(sn=sn)
        except Ticket.DoesNotExist:
            raise ParamError("sn[{}]对应的单据不存在！".format(sn))

        try:
            status = Status.objects.get(ticket_id=ticket.id, state_id=state_id)
        except Exception:
            raise ParamError("sn[{}], state[{}] 未查到对应的节点状态".format(sn, state_id))

        if status.status != "FINISHED":
            raise ParamError("sn[{}], state[{}] 当前节点状态为非结束状态".format(sn, state_id))

        approve_result = False
        approve_remark = ""

        # ticket_fields 字段是排好序的，所以第一个一定是选项
        for field in status.ticket_fields:
            if field.type == "RADIO" and field.value == "true":
                approve_result = True
            if (
                approve_result
                and field.type == "TEXT"
                and field.validate_type == "OPTION"
            ):
                approve_remark = field.value
            if (
                not approve_result
                and field.type == "TEXT"
                and field.validate_type == "REQUIRE"
            ):
                approve_remark = field.value
        data = {
            "name": status.name,
            "processed_user": status.processed_user,
            "approve_result": approve_result,
            "approve_remark": approve_remark,
        }

        return Response(data)

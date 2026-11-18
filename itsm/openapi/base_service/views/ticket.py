# -*- coding: utf-8 -*-
import copy
from django.db import transaction

from blueapps.account.decorators import login_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.response import Response

from common.log import logger
from itsm.component.decorators import custom_apigw_required
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.drf.mixins import ApiGatewayMixin
from itsm.component.exceptions import CreateTicketError
from itsm.openapi.base_service.serializers import TicketCreateSerializer
from itsm.ticket.serializers import TicketSerializer, Ticket
from itsm.ticket.tasks import start_ticket
from itsm.ticket.utils import safe_after_commit


@method_decorator(login_exempt, name="dispatch")
class TicketViewSet(ApiGatewayMixin, component_viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.filter(is_deleted=False, is_draft=False)
    serializer_class = TicketSerializer

    @custom_apigw_required
    def list(self, request, *args, **kwargs):
        return Response()

    @custom_apigw_required
    def retrieve(self, request, *args, **kwargs):
        return Response()

    @custom_apigw_required
    @action(detail=False, methods=["post"])
    def create_ticket_with_version(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        logger.info(
            "[openapi][create_ticket_with_version]-> 开始创建单据， data={}".format(
                data
            )
        )
        serializer = TicketCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        fields_payload = data["fields"]
        from_ticket_id = request.data.get("from_ticket_id", None)
        username = request.user.username
        try:
            with transaction.atomic():
                instance = serializer.save()
                instance.prepare_initial_fields(
                    fields_payload, operator=username
                )
        except Exception as e:
            logger.exception(
                "[openapi][create_ticket_with_version]-> 单据创建失败， 错误原因 error={}".format(
                    e
                )
            )
            raise CreateTicketError()

        # 单据与附件归属已提交：初始化流程和投递 pipeline 按顺序执行，
        # 失败只记录告警，不改变建单结果（响应体保持不变）。
        transaction.on_commit(
            lambda: safe_after_commit(
                instance,
                "start_ticket",
                lambda: start_ticket(
                    instance, fields_payload, from_ticket_id, username
                ),
            )
        )

        logger.info(
            "[openapi][create_ticket_with_version]-> 单据创建成功，sn={}, request_data={}".format(
                instance.sn, data
            )
        )
        return Response(
            {"sn": instance.sn, "id": instance.id, "ticket_url": instance.pc_ticket_url}
        )

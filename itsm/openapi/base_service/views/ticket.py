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
from itsm.ticket.tasks import start_pipeline


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
        with transaction.atomic():
            instance = serializer.save()
            instance.prepare_initial_fields(
                data["fields"], operator=request.user.username
            )
        try:
            # 创建额外的全局字段
            transaction.on_commit(
                lambda: instance.do_after_create(
                    data["fields"],
                    request.data.get("from_ticket_id", None),
                    operator=request.user.username,
                    fields_prepared=True,
                )
            )
            transaction.on_commit(lambda: start_pipeline.apply_async([instance]))
        except Exception as e:
            logger.exception(
                "[openapi][create_ticket_with_version]-> 单据创建失败， 错误原因 error={}".format(
                    e
                )
            )
            # Keep the committed ticket and its attachment ownership on startup failure.
            raise CreateTicketError()

        logger.info(
            "[openapi][create_ticket_with_version]-> 单据创建成功，sn={}, request_data={}".format(
                instance.sn, data
            )
        )
        return Response(
            {"sn": instance.sn, "id": instance.id, "ticket_url": instance.pc_ticket_url}
        )

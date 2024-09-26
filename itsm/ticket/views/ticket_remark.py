# -*- coding: utf-8 -*-
from django.http import Http404
from django.utils.translation import ugettext as _
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.drf.viewsets import ModelViewSet
from itsm.component.exceptions import ValidateError
from itsm.ticket.models import TicketRemark, Ticket
from itsm.ticket.permissions import RemarkPermissionValidate
from itsm.ticket.serializers import TicketRemarkSerializer


class TicketRemarkModelViewSet(ModelViewSet):
    queryset = TicketRemark.objects.filter(is_deleted=False).order_by(
        "-create_at", "level"
    )
    serializer_class = TicketRemarkSerializer
    permission_classes = (RemarkPermissionValidate,)

    def list(self, request, *args, **kwargs):
        # 后面这个接口要重构一部分
        ticket_id = request.query_params.get("ticket_id", "")
        if not ticket_id:
            raise ValidateError(_("ticket_id 不能为空"))
        show_type = request.query_params.get("show_type", "PUBLIC")

        ticket = Ticket.objects.get(id=ticket_id)
        history_operators = ticket.updated_by.split(",")

        remark_type = ["ROOT", show_type]

        if show_type == "ALL":
            remark_type = ["ROOT", "INSIDE", "PUBLIC"]

        if not (
            request.user.username in history_operators
            or ticket.can_operate(request.user.username)
        ):
            remark_type = ["ROOT", "PUBLIC"]

        queryset = self.get_queryset().filter(
            remark_type__in=remark_type, ticket_id=ticket_id
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            """兼容父级评论删除情况"""
            return Response([])
    
    @action(detail=False, methods=["get"])
    def tree_view(self, request):
        """评论视图"""
        ticket_id = request.query_params.get("ticket_id", "")
        show_type = request.query_params.get("show_type", "PUBLIC")
        tree_data = TicketRemark.root_subtree(ticket_id=ticket_id, show_type=show_type)
        return Response(tree_data)

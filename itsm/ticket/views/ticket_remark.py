# -*- coding: utf-8 -*-
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.drf import viewsets as component_viewsets
from itsm.ticket.models import TicketRemark
from itsm.ticket.serializers import TicketRemarkSerializer


class ModelViewSet(component_viewsets.ModelViewSet):
    """按需改造DRF默认的ModelViewSet类"""

    def perform_create(self, serializer):
        """创建时补充基础Model中的字段"""
        user = serializer.context.get("request").user
        username = getattr(user, "username", "guest")
        return serializer.save(creator=username, updated_by=username)

    def perform_update(self, serializer):
        """更新时补充基础Model中的字段"""
        user = serializer.context.get("request").user
        username = getattr(user, "username", "guest")
        serializer.save(updated_by=username)


class TicketRemarkModelViewSet(ModelViewSet):
    queryset = TicketRemark.objects.filter(is_deleted=False).order_by(
        "-create_at", "level"
    )
    serializer_class = TicketRemarkSerializer

    def list(self, request, *args, **kwargs):
        ticket_id = request.query_params.get("ticket_id", "")
        show_type = request.query_params.get("show_type", "PUBLIC")

        # 对于历史单据，自动init
        TicketRemark.init_root_node(ticket_id)

        queryset = self.get_queryset().filter(
            remark_type__in=["ROOT", show_type], ticket_id=ticket_id
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def tree_view(self, request):
        """评论视图"""
        ticket_id = request.query_params.get("ticket_id", "")
        show_type = request.query_params.get("show_type", "PUBLIC")
        tree_data = TicketRemark.root_subtree(ticket_id=ticket_id, show_type=show_type)
        return Response(tree_data)

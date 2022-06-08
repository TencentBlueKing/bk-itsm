# -*- coding: utf-8 -*-
from rest_framework.response import Response

from itsm.component.decorators import custom_apigw_required
from itsm.component.drf.viewsets import ReadOnlyModelViewSet
from itsm.iadmin.contants import ORGANIZATION_KEY, SWITCH_OFF
from itsm.iadmin.models import SystemSettings
from itsm.role.models import RoleType
from itsm.role.serializers import RoleTypeSerializer


class RoleTypeModelViewSet(ReadOnlyModelViewSet):
    """角色类型视图集合"""

    serializer_class = RoleTypeSerializer
    queryset = RoleType.objects.all()
    pagination_class = None

    filter_fields = {
        "is_display": ["exact", "in"],
        "is_processor": ["exact", "in"],
        "type": ["exact", "in"],
        "name": ["exact", "contains", "startswith"],
    }

    def get_queryset(self):
        queryset = super(RoleTypeModelViewSet, self).get_queryset()
        if SystemSettings.objects.get(key=ORGANIZATION_KEY).value == SWITCH_OFF:
            return queryset.exclude(type="ORGANIZATION")
        return queryset

    @custom_apigw_required
    def list(self, request, *args, **kwargs):
        return super(RoleTypeModelViewSet, self).list(request, *args, **kwargs)

    @custom_apigw_required
    def retrieve(self, request, *args, **kwargs):
        return Response()

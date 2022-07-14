# -*- coding: utf-8 -*-

from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import ugettext as _

from itsm.component.constants import START_STATE, TICKET_GLOBAL_VARIABLES

from itsm.component.decorators import custom_apigw_required
from itsm.component.drf import viewsets
from itsm.component.drf.exception import ValidationError
from itsm.workflow.models import Transition
from itsm.workflow.serializers import TransitionSerializer
from itsm.workflow.validators import transition_batch_update_validate


class TransitionViewSet(viewsets.ModelViewSet):
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

    @custom_apigw_required
    def list(self, request, *args, **kwargs):
        return super(TransitionViewSet, self).list(request, *args, **kwargs)

    @custom_apigw_required
    def retrieve(self, request, *args, **kwargs):
        return super(TransitionViewSet, self).retrieve(request, *args, **kwargs)

    @custom_apigw_required
    def update(self, request, *args, **kwargs):
        return super(TransitionViewSet, self).update(request, *args, **kwargs)

    @custom_apigw_required
    def create(self, request, *args, **kwargs):
        return super(TransitionViewSet, self).create(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    @custom_apigw_required
    def variables(self, request, *args, **kwargs):
        state = self.get_object().from_state
        valid_inputs = state.get_valid_inputs(scope="transition")
        valid_inputs.extend(TICKET_GLOBAL_VARIABLES)

        return Response(valid_inputs)

    @action(detail=False, methods=["post"])
    @custom_apigw_required
    def batch_update(self, request):
        workflow_id = request.data.get("workflow_id")
        transactions = request.data.get("transitions", [])

        transition_batch_update_validate(workflow_id, transactions)

        for item in transactions:
            Transition.objects.filter(id=item.pop("id", None)).update(**item)
        return Response()

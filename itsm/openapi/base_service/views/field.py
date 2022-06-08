# -*- coding: utf-8 -*-
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.decorators import custom_apigw_required
from itsm.workflow.models import Field, Workflow, FIELD_BIZ, State, TABLE
from itsm.workflow.serializers import FieldSerializer
from itsm.workflow.validators import related_validate
from itsm.workflow.views import BaseFieldViewSet


class FieldViewSet(BaseFieldViewSet):
    """表单字段视图集"""

    queryset = Field.objects.all()
    serializer_class = FieldSerializer

    filter_fields = {
        "id": ["in"],
        "key": ["exact", "in", "contains", "startswith"],
        "name": ["exact", "contains", "startswith"],
        "type": ["exact", "in"],
        "is_builtin": ["exact"],
        "is_readonly": ["exact"],
        "layout": ["exact", "in"],
        "validate_type": ["exact", "in"],
    }

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None
        query_set = super(FieldViewSet, self).get_queryset()
        return query_set

    @custom_apigw_required
    def retrieve(self, request, *args, **kwargs):
        return super(FieldViewSet, self).retrieve(request, *args, **kwargs)

    @custom_apigw_required
    def update(self, request, *args, **kwargs):
        return super(FieldViewSet, self).update(request, *args, **kwargs)

    @custom_apigw_required
    def create(self, request, *args, **kwargs):
        return super(FieldViewSet, self).create(request, *args, **kwargs)

    @custom_apigw_required
    def destroy(self, request, *args, **kwargs):
        return super(FieldViewSet, self).destroy(request, *args, **kwargs)

    @custom_apigw_required
    def list(self, request, *args, **kwargs):
        """支持根据流程和节点查询字段，关闭分页"""

        workflow_id = self.request.query_params.get("workflow")
        state_id = self.request.query_params.get("state")

        queryset = self.filter_queryset(self.get_queryset())

        if workflow_id:
            workflow = Workflow.objects.get(id=workflow_id)
            if not workflow.is_biz_needed:
                queryset = queryset.exclude(key=FIELD_BIZ)

        if state_id:
            valid_fields = State.objects.fields_of_state(state_id)
            ordering = "FIELD(`id`, {})".format(
                ",".join(["'{}'".format(v) for v in valid_fields])
            )
            queryset = queryset.filter(id__in=valid_fields).extra(
                select={"ordering": ordering}, order_by=["ordering"]
            )

        serializer_data = self.get_serializer(queryset, many=True).data

        # 级联关系的梳理
        be_relied = {}
        for field_info in serializer_data:
            cur_field_key = field_info["key"]
            for field_key in field_info["related_fields"].get("rely_on", []):
                if field_key not in be_relied:
                    be_relied[field_key] = [cur_field_key]
                else:
                    be_relied[field_key].append(cur_field_key)
        for field in serializer_data:
            if field["key"] in be_relied:
                field["related_fields"]["be_relied"] = be_relied[field["key"]]

        return Response(serializer_data)

    def perform_destroy(self, instance):
        """
        自动从State的fields中移除该字段
        """
        with transaction.atomic():
            if (
                instance.key == "bk_biz_id"
                and instance.id == instance.workflow.first_state.id
            ):
                instance.workflow.is_biz_needed = False
                instance.workflow.save()
            if instance.source != TABLE:
                related_validate(instance)
            if instance.state:
                instance.state.fields.remove(instance.id)
                instance.state.save()
            super(FieldViewSet, self).perform_destroy(instance)

    @action(detail=True, methods=["post"])
    @custom_apigw_required
    def update_layout(self, request, *args, **kwargs):
        field_object = self.get_object()
        for key in [
            "layout",
            "show_conditions",
            "show_type",
            "validate_type",
            "default",
            "regex_config",
        ]:
            setattr(field_object, key, request.data.get(key, ""))
        field_object.save()
        return Response()

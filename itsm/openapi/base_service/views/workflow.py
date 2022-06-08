# -*- coding: utf-8 -*-
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import ugettext as _

from business_rules.operators import *  # noqa
from itsm.component.constants import *  # noqa
from itsm.component.decorators import custom_apigw_required
from itsm.component.drf import viewsets
from itsm.workflow.models import Workflow
from itsm.workflow.serializers import WorkflowSerializer
from itsm.workflow.utils import translate_constant_2


class WorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = WorkflowSerializer
    queryset = Workflow.objects.prefetch_related("notify").order_by("-update_at")

    @custom_apigw_required
    def list(self, request, *args, **kwargs):
        return Response()

    @custom_apigw_required
    def retrieve(self, request, *args, **kwargs):
        return super(WorkflowViewSet, self).retrieve(request, *args, **kwargs)

    @custom_apigw_required
    def update(self, request, *args, **kwargs):
        return super(WorkflowViewSet, self).update(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    @custom_apigw_required
    def get_global_choices(self, request):
        """查询全局选项列表信息"""
        trigger_methods = {
            "int": NumericType.get_display_operators(),
            "bool": BooleanType.get_display_operators(),
            "string": StringType.get_display_operators(),
            "select": StringType.get_display_operators(),
            "radio": StringType.get_display_operators(),
            "text": StringType.get_display_operators(),
            "datetime": DateTimeType.get_display_operators(),
            "time": TimeType.get_display_operators(),
            "multiselect": SelectMultipleType.get_display_operators(),
            "checkbox": SelectMultipleType.get_display_operators(),
            "member": SelectMultipleType.get_display_operators(),
            "members": SelectMultipleType.get_display_operators(),
        }

        return Response(
            {
                "field_type": translate_constant_2(TYPE_CHOICES[:-1]),
                "source_type": translate_constant_2(SOURCE_CHOICES),
                "layout_type": translate_constant_2(LAYOUT_CHOICES),
                "validate_type": translate_constant_2(VALIDATE_CHOICES),
                "notify_type": translate_constant_2(NOTIFY_TYPE_CHOICES),
                "notify_rule_type": translate_constant_2(NOTIFY_RULE_CHOICES),
                "state_type": translate_constant_2(STATE_TYPE_CHOICES),
                "processor_type": translate_constant_2(PROCESSOR_CHOICES),
                "fault_source": translate_constant_2(FAULT_SOURCE_CHOICES),
                "distribute_type": translate_constant_2(DISTRIBUTE_TYPE_CHOICES),
                "methods": translate_constant_2(METHOD_CHOICES),
                "condition_type": translate_constant_2(FLOW_CONDITION_TYPE_CHOICES),
                "sops_field_map": translate_constant_2(SOPS_FIELD_MAP),
                "trigger_icon": translate_constant_2(TRIGGER_ICON_CHOICE),
                "trigger_source_type": translate_constant_2(TRIGGER_SOURCE_TYPE),
                "trigger_methods": trigger_methods,
                "ticket_variables": TICKET_GLOBAL_VARIABLES,
                "trigger_signals": TRIGGER_SIGNAL,
                "trigger_categories": TRIGGER_CATEGORIES,
                "only_backend_signals": ONLY_BACKEND_SIGNALS,
            }
        )

    @action(detail=False, methods=["get"])
    @custom_apigw_required
    def get_regex_choice(self, request):
        field_type = request.GET.get("type")
        regex_choice = REGEX_CHOICES.get(field_type, [("EMPTY", "")])
        return Response(
            {
                "regex_choice": [(i[0], _(i[1])) for i in regex_choice],
            }
        )

    @action(detail=True, methods=["get"])
    @custom_apigw_required
    def variables(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.variables)

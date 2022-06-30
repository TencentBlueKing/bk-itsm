# -*- coding: utf-8 -*-
from itsm.component.constants import FIELD_STATUS
from itsm.component.exceptions import WorkFlowError
from itsm.workflow.models import State, Transition, TemplateField, FIELD_BIZ, Field


class WorkflowInitHandler:
    def __init__(self, instance, workflow_meta):
        self.instance = instance
        self.workflow_meta = workflow_meta

    def init_workflow(self):
        states = self.workflow_meta.get("states", [])
        transitions = self.workflow_meta.get("transitions", [])

        if self.instance.table:
            ordering = "FIELD(`id`, %s)" % ",".join(
                [str(field_id) for field_id in self.instance.table.fields_order]
            )
            fields = TemplateField.objects.filter(
                id__in=self.instance.table.fields_order, is_builtin=True
            )

            if not self.instance.is_biz_needed:
                fields.exclude(key=FIELD_BIZ)

            fields = fields.extra(select={"ordering": ordering}, order_by=("ordering",))

            try:
                Field.objects.create_table_fields(self.instance, fields)
            except BaseException as error:
                self.instance.delete()
                raise WorkFlowError("create table field error:%s" % str(error))

        states_map = {}
        for state in states:
            old_state_id = state.pop("id")
            state["workflow_id"] = self.instance.pk
            state_obj = State.objects.create(**state)
            if state_obj.type == "NORMAL" and state_obj.is_builtin:
                # 初始化初始阶段的默认字段
                state_obj.fields = list(
                    self.instance.fields.filter(is_builtin=True)
                    .exclude(key=FIELD_STATUS)
                    .values_list("id", flat=True)
                )
                state_obj.save()

            states_map[int(old_state_id)] = state_obj.id

        for transition in transitions:
            Transition.objects.create_forward_transition(
                self.instance.pk,
                states_map[transition["from_state"]],
                states_map[transition["to_state"]],
                True,
                "",
            )

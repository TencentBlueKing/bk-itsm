# -*- coding: utf-8 -*-
import copy

from itsm.component.constants import FIELD_TITLE
from itsm.component.drf.exception import ValidationError
from itsm.openapi.ticket.validators import edit_field_validate
from itsm.ticket.models import Ticket, FIELD_PX_URGENCY, FIELD_PY_IMPACT
from itsm.ticket.serializers import FieldSerializer, TicketEventLog


def edit_ticket_field(field, sn, username):

    form_data = []

    def edit_field_tracker(field_instance, old):
        """基础字段修改日志记录"""

        new_data = copy.deepcopy(FieldSerializer(field_instance).data)
        old_field_instance = copy.deepcopy(field_instance)
        old_field_instance._value = old
        old_data = copy.deepcopy(FieldSerializer(old_field_instance).data)
        old_data.update({"value_status": "before"})
        new_data.update({"value_status": "after"})
        form_data.extend([old_data, new_data])

    try:
        ticket = Ticket.objects.get(sn=sn)
    except Exception:
        raise ValidationError("ticket_id = {} 对应的单据不存在！".format(sn))

    # 如果ticket当前状态为：已完成/已终止/已撤销，则无法修改字段
    if ticket.current_status in ["FINISHED", "TERMINATED", "REVOKED"]:
        raise ValidationError(
            "current_status = {} 当前状态不可修改字段！".format(ticket.current_status)
        )

    validate_data, field_obj = edit_field_validate(
        ticket, field, service=ticket.service_type
    )

    field_value = validate_data["value"]

    update_data = {"_value": field_value}
    if validate_data.get("choice"):
        update_data.update(choice=validate_data["choice"])

    old_value = field_obj.value

    ticket.fields.filter(key=field_obj.key).update(**update_data)

    field_obj.refresh_from_db()

    # 公共字段修改记录
    edit_field_tracker(field_obj, old_value)

    # 修改了紧急程度或影响范围，重新计算优先级
    if field_obj.key in [FIELD_PX_URGENCY, FIELD_PY_IMPACT]:
        impact = urgency = None
        if field_obj.key == FIELD_PX_URGENCY:
            urgency = field_value
        elif field_obj.key == FIELD_PY_IMPACT:
            impact = field_value

        priority_data = ticket.update_priority(urgency, impact)
        if priority_data:
            # 存在优先级修改记录的时候才进行跟踪
            edit_field_tracker(priority_data["instance"], priority_data["old_value"])

        ticket.refresh_sla_task()

    # 修改了title，同步修改工单title
    if field_obj.key == FIELD_TITLE:
        ticket.title = field_value
        ticket.save()

    TicketEventLog.objects.create_log(
        ticket,
        0,
        username,
        "EDIT_FIELD",
        message="{operator} 修改字段【{detail_message}】.",
        detail_message=field_obj.name,
        fields=form_data,
        to_state_id=0,
    )

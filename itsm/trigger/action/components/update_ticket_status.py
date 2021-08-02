# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from django import forms
from django.utils.translation import ugettext as _

from itsm.component.constants import FIELD_STATUS
from itsm.component.dlls.component import BaseComponentForm
from itsm.ticket.models import Ticket
from itsm.ticket_status.models import TicketStatus
from itsm.trigger.action.core.component import BaseComponent


__register_ignore__ = False


def get_ticket_status_names():
    """Get all ticket status display name"""
    status_names = TicketStatus.objects.get_overall_status_names(exclude_keys=["SUSPENDED"])
    return [(key, name) for key, name in status_names.items()]


class UpdateTicketStatus(BaseComponent):
    name = _("更新单据状态")
    code = "update_ticket_status"
    is_async = False
    is_sub_class = True

    class Form(BaseComponentForm):
        ticket_status_name = forms.ChoiceField(label=_("单据状态"), required=True, choices=get_ticket_status_names)

        def clean(self):
            """Form data clean"""
            cleaned_data = super().clean()
            return cleaned_data

    def _execute(self):
        ticket_id = self.context["ticket_id"]
        ticket_status_key = self.data.get_one_of_inputs("ticket_status_name")
        ticket = Ticket.objects.get(id=ticket_id)

        # Whether follow status transit rule
        from_status = TicketStatus.objects.get(service_type=ticket.service_type, key=ticket.current_status)
        to_status_infos = from_status.from_transits.values("to_status__key", "to_status__name")

        for to_status_info in to_status_infos:
            if to_status_info['to_status__key'] == ticket_status_key:

                # Update status from ticket
                ticket.current_status = ticket_status_key
                ticket.save(update_fields=['current_status'])

                # Update status from field
                ticket.fields.filter(key=FIELD_STATUS).update(_value=ticket_status_key)
                return True

        self.data.set_outputs('message', _('工单状态无法更新为%s, 不满足状态流转规则, 请联系管理员! ' % ticket_status_key))
        return False

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

from django.utils.translation import ugettext as _

from itsm.component.constants import MASTER_SLAVE
from itsm.trigger.action.core.component import BaseComponent
from itsm.trigger.action.core import BaseForm, StringField
from itsm.ticket.models import Ticket, TicketToTicket
from itsm.ticket.tasks import clone_pipeline

__register_ignore__ = False


class UnbindTicketForms(BaseForm):
    desc = StringField(name=_("解绑说明"), field_type="text", required=False)

    slave_tickets = StringField(
        name=_("解绑的子单"),
        field_type="text",
        required=False,
        display=False,
        default={"ref_type": "reference", "value": "slave_tickets"},
    )


class UnbindTicketsComponent(BaseComponent):
    name = _("解绑母子单")
    code = "unbind_parent_child_tickets"
    is_async = False
    form_class = UnbindTicketForms

    def _execute(self):
        """
        解除母子单关联关系
        """
        try:
            master_ticket = Ticket.objects.get(sn=self.context.get("ticket_sn"))
        except Ticket.DoesNotExist:
            self.data.set_outputs("message", _("对应的单据【%s】不存在") % self.context.get("ticket_sn"))
            return False
        slave_tickets = [
            item.from_ticket
            for item in TicketToTicket.objects.filter(related_type=MASTER_SLAVE, to_ticket=master_ticket)
        ]
        if not slave_tickets:
            self.data.set_outputs("message", _("当前的单据【%s】不存在母子关联单") % self.context.get("ticket_sn"))
            return False
        TicketToTicket.objects.filter(related_type=MASTER_SLAVE, to_ticket=master_ticket).update(
            related_status="RUNNING"
        )
        slave_tickets_sn = []
        for slave_ticket in slave_tickets:
            clone_pipeline.apply_async(args=(slave_ticket, master_ticket))
            slave_tickets_sn.append(slave_ticket.sn)
        self.data.set_outputs("slave_tickets", slave_tickets_sn)
        self.data.set_outputs("slave_tickets__display", ",".join(slave_tickets_sn))
        return True

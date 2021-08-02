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

from itsm.component.constants import FIELD_STATUS
from itsm.trigger.action.core.component import BaseComponent
from itsm.trigger.action.core import SelectField
from itsm.trigger.action.core import BaseForm
from itsm.ticket_status.models import TicketStatus
from itsm.ticket.models import Ticket

__register_ignore__ = False


def get_ticket_status_names():
    """Get all ticket status display name"""
    status_names = TicketStatus.objects.get_overall_status_names(exclude_keys=["SUSPENDED"])
    return [{"key": key, "name": name} for key, name in status_names.items()]


class TicketStatusForms(BaseForm):
    """
    发送通知的输入数据格式
    """

    dst_status = SelectField(name=_("工单状态"), choice=get_ticket_status_names)


class ModifyTicketStatusComponent(BaseComponent):
    name = _("修改工单状态")
    code = "modify_ticket_status"
    is_async = False
    form_class = TicketStatusForms

    def _execute(self):
        """
        修改对应单据的工单状态
        """
        try:
            dst_ticket = Ticket.objects.get(sn=self.context["ticket_sn"])
        except Ticket.DoesNotExist:
            self.data.set_outputs("message", "当前工单不存在")
            return False

        dst_status = self.data.get_one_of_inputs("dst_status")
        print("dst_status is {}".format(dst_status))
        # Whether follow status transit rule
        from_status = TicketStatus.objects.get(service_type=dst_ticket.service_type, key=dst_ticket.current_status)
        all_status_info = from_status.from_transits.values("to_status__key", "to_status__name")

        for to_status_info in all_status_info:
            if to_status_info['to_status__key'] == dst_status:

                # Update status from ticket
                dst_ticket.current_status = dst_status
                dst_ticket.save(update_fields=['current_status'])

                # Update status from field
                dst_ticket.fields.filter(key=FIELD_STATUS).update(_value=dst_status)
                return True

        # TODO 更新错误信息
        self.data.set_outputs('message', _('工单状态无法更新为%s, 不满足状态流转规则, 请联系管理员! ' % dst_status))
        return False

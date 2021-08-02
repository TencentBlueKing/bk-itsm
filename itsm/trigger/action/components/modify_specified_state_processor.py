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

from itsm.component.constants import FLOW_STATES, TASK_SIGNAL
from itsm.trigger.action.core.component import BaseComponent
from itsm.trigger.action.core import MemberField, BaseForm, MultiSelectField

from itsm.ticket.models import Status, Ticket

__register_ignore__ = False


class ProcessorForms(BaseForm):
    """
    发送通知的输入数据格式
    """

    states = MultiSelectField(
        name=_("指定节点"),
        use_variable=False,
        source_type="RPC",
        source_uri=FLOW_STATES,
        is_tips=True,
        tips="在触发后，指定的节点为当前节点，则当前动作会生效",
    )
    processors = MemberField(name=_("处理人"), convert_to_users=False)


class ModifySpecifiedStateProcessorComponent(BaseComponent):
    name = _("修改指定节点处理人")
    code = "modify_specified_state_processor"
    is_async = False
    form_class = ProcessorForms
    exclude_signal_type = [TASK_SIGNAL]

    def _execute(self):
        """
        修改节点对应的处理人
        """
        try:
            ticket = Ticket.objects.get(sn=self.context.get("ticket_sn"))
        except Ticket.DoesNotExist:
            self.data.set_outputs("message", "对应的单据不存在")
            return False

        states = self.data.get_one_of_inputs("states", [])

        all_status = Status.objects.filter(ticket=ticket, status__in=Status.CAN_OPERATE_STATUS, state_id__in=states)

        processors = self.data.get_one_of_inputs("processors")
        if not processors:
            self.data.set_outputs("message", "设置处理人为空")
            return False

        all_status.update(processors_type=processors['member_type'], processors=processors["members"])
        self.data.set_outputs("states__display", ",".join(set(all_status.values_list("name", flat=True))))
        ticket.set_current_processors()

        return True

    def update_context(self):
        """
        手动操作的时候更新context
        """
        try:
            dst_state = Status.objects.get(id=self.context.get("dst_state"))
        except Status.DoesNotExist:
            return self.context
        self.context.update(dst_state.ticket.get_output_fields(return_format='dict'))
        self.validate_inputs()
        return self.context

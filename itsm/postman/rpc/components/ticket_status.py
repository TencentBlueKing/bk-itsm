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

from collections import OrderedDict, defaultdict

from django.utils.translation import ugettext as _

from itsm.component.constants import STATUS, SERVICE_CATEGORY
from itsm.component.dlls.component import BaseComponentForm
from itsm.postman.rpc.core.component import BaseComponent
from itsm.ticket.models import Ticket
from itsm.ticket_status.models import TicketStatus
from itsm.ticket_status.serializers import TicketStatusOptionSerializer


class GetTicketStatus(BaseComponent):
    name = _("工单状态")
    code = STATUS

    class Form(BaseComponentForm):
        def clean(self):
            """数据清理"""
            cleaned_data = super().clean()

            ticket_id = self.data.get("ticket_id")
            if ticket_id:
                ticket = Ticket.objects.get(id=ticket_id)
                cleaned_data.update(current_status=ticket.current_status,
                                    service_type=ticket.service_type)

            return cleaned_data

    def handle(self):
        if "service_type" in self.form_data:
            ticket_status = TicketStatus.objects.get(
                key=self.form_data["current_status"], service_type=self.form_data["service_type"]
            )
            payload = TicketStatusOptionSerializer(ticket_status.to_status, many=True).data
        else:
            payload = []
            ticket_status_dict = OrderedDict()
            # 获取所有非结束的工单状态
            ticket_statuses = TicketStatus.objects.filter(is_over=False).order_by("order")

            # 将相同key的单据状态合并
            for ticket_status in ticket_statuses:
                other_info = {
                    "name": ticket_status.name,
                    "service_type": ticket_status.service_type,
                }
                if ticket_status.key not in ticket_status_dict:
                    ticket_status_dict[ticket_status.key] = {
                        "key": ticket_status.key,
                        "other_info_list": [other_info],
                    }
                else:
                    ticket_status_dict[ticket_status.key]["other_info_list"].append(other_info)

            for key, info in ticket_status_dict.items():
                name_dict = defaultdict(set)
                for other_info in info["other_info_list"]:
                    name_dict[other_info["name"]].add(other_info["service_type"])

                name_list = [
                    "%s(%s)" % (name, self.get_service_type_display_name(service_types))
                    for name, service_types in name_dict.items()
                ]
                payload.append(
                    {"key": key, "name": ",".join(name_list), }
                )

        self.response.payload = payload

    @staticmethod
    def get_service_type_display_name(service_types):
        """友好显示服务类型"""
        if len(set(SERVICE_CATEGORY.keys()).difference(service_types)):
            return ",".join(_(SERVICE_CATEGORY[service_type]) for service_type in service_types)
        else:
            return _("所有服务类型")

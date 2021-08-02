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

from rest_framework import serializers

from itsm.role.models import UserRole
from itsm.ticket.models import Ticket, TicketEventLog
from itsm.workflow.models import State


class OperationalDataTicketSerializer(serializers.ModelSerializer):
    """运营数据单据序列化类"""

    class Meta:
        model = Ticket
        fields = "__all__"

    def to_representation(self, instance):
        from itsm.workflow.serializers import StateSerializer
        from itsm.ticket.serializers import FieldSerializer

        data = super(OperationalDataTicketSerializer, self).to_representation(instance)
        fields = FieldSerializer(instance.fields, many=True).data
        states_data = StateSerializer(
            State.objects.filter(id__in=[state["id"] for state in instance.flow.master]), many=True,
        ).data
        for state in states_data:
            log = (
                TicketEventLog.objects.filter(ticket_id=instance.id, from_state_id=state["id"], is_valid=True)
                .exclude(message__in=["流程开始", "单据流程结束"])
                .reverse()
                .first()
            )
            state.update(
                {
                    "valid_processor": log.operator if log else "",
                    "operate_at": log.operate_at.strftime("%Y-%m-%d %H:%M:%S") if log else None,
                    "processors": UserRole.get_users_by_type(
                        bk_biz_id=instance.bk_biz_id,
                        user_type=state["processors_type"],
                        users=state["processors"],
                        ticket=instance,
                    ),
                    "followers": UserRole.get_users_by_type(
                        bk_biz_id=instance.bk_biz_id,
                        user_type=state["followers_type"],
                        users=state["followers"],
                        ticket=instance,
                    ),
                }
            )

        current_processors = ",".join(instance.real_current_processors)
        current_assignors = ",".join(instance.real_assignors)
        supervisors = ",".join(instance.real_supervisors)

        for key in ["catalog_id", "service_id", "flow_id"]:
            data.pop(key)

        data.update(
            {
                "service": data.pop("service_type"),
                "states": states_data,
                "fields": fields,
                "current_processors": current_processors,
                "current_assignor": current_assignors,
                "supervisor": supervisors,
                "workflow_id": instance.flow.workflow_id,
            }
        )
        return data

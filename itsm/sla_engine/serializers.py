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

from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from itsm.sla_engine.constants import RUNNING

from .models import SlaTask


class SlaTaskSerializer(serializers.ModelSerializer):
    """工单任务序列化"""

    class Meta:
        model = SlaTask
        fields = (
            "ticket_id",
            "name",
            "start_node_id",
            "end_node_id",
            "deadline",
            "begin_at",
            "end_at",
            "sla_status",
            "task_status",
            "reply_cost",
            "replied_at",
            "is_replied",
            "protocol_name",
            "cost_time",
            "start_node_name",
            "end_node_name",
            "reply_deadline",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # data["reply_cost"] = seconds_format(data["reply_cost"]) if data["is_replied"] else 0
        data["reply_cost"] = [
            int(getattr(relativedelta(seconds=data["reply_cost"] or 0), attr))
            for attr in ["years", "months", "days", "hours", "minutes", "seconds"]
        ]
        if instance.task_status == RUNNING:
            current_cost = instance.get_cost_time()
            data["cost_time"] = current_cost
        else:
            current_cost = data["cost_time"]
        data["resovle_cost"] = [
            int(getattr(relativedelta(seconds=current_cost), attr))
            for attr in ["years", "months", "days", "hours", "minutes", "seconds"]
        ]

        return data

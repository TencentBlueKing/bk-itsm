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

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from rest_framework import serializers

from rest_framework.fields import empty
from itsm.component.utils.client_backend_query import get_bk_users
from itsm.ticket.models import TicketEventLog, Status
from itsm.ticket.utils import translate

BkUser = get_user_model()


class EventSerializer(serializers.ModelSerializer):
    """单据事件日志序列化"""

    form_data = serializers.JSONField(read_only=True)

    class Meta:
        model = TicketEventLog
        fields = (
            'id',
            'ticket',
            'type',
            'operator',
            'operate_at',
            'deal_time',
            'processors_type',
            'processors',
            'message',
            'detail_message',
            'action',
            'from_state_name',
            'ticket_id',
            'form_data',
            'from_state_id',
        )

    def __init__(self, instance=None, data=empty, **kwargs):
        super(EventSerializer, self).__init__(instance, data, **kwargs)
        # 针对批量获取的内容，可以在init的时候进行处理，避免每个数据的序列化都要去拉取接口
        self.related_users = self.get_related_users()

    def get_related_users(self):
        """
        获取到所有相关的用户，避免多次访问API接口
        :return:
        """

        logs = (
            [self.instance] if isinstance(self.instance,
                                          TicketEventLog) else [] if self.instance is None else self.instance
        )

        all_related_users = [inst.operator for inst in logs if inst.operator]
        return get_bk_users(format='dict', users=list(set(all_related_users)))

    def to_representation(self, instance):
        data = super(EventSerializer, self).to_representation(instance)
        data['message'] = translate(instance.message, data, related_operators=self.related_users)
        data['operator'] = self.related_users.get(instance.operator)
        form_data = []
        origin_form_data = data['form_data'].values() if isinstance(data['form_data'], dict) else data['form_data']
        for item in origin_form_data:
            if not item.get('show_result'):
                continue
            value_status = item.get("value_status")
            if value_status:
                item.update({"name": _("{}(修改前)" if value_status == 'before' else "{}(修改后)").format(item['name'])})
            form_data.append(item)
        data['form_data'] = form_data
        node_status = Status.objects.filter(ticket_id=instance.ticket_id, state_id=instance.from_state_id).first()
        data['from_state_type'] = getattr(node_status, "type", "")
        return data

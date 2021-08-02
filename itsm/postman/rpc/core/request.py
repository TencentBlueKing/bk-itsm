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

import json

from mako.template import Template

from common.log import logger
from itsm.postman.constants import TICKET_CONTEXT_KEY, TRIGGER_SOURCE
from itsm.ticket.models import Ticket, TicketGlobalVariable
from itsm.trigger.models import Trigger


class CompRequest(object):
    """
    Request class for Component
    """

    def __init__(self, data, method="RPC"):
        self.data = data
        self.kwargs = {}
        self.query_params = {}
        self.method = method

    @classmethod
    def parse_params(cls, params):
        params_context = {"params_%s" % key: value for key, value in params.items()}
        rpc_source = params.get("rpc_source")
        # 判断是否包括单据上下文
        if TICKET_CONTEXT_KEY in params:
            ticket_id = params["ticket_id"]
            ticket = Ticket.objects.get(id=ticket_id)

            params_context.update(
                {
                    "params_%s" % field['key']: field['_value']
                    for field in ticket.fields.filter(_value__isnull=False).exclude(_value="").values("key", "_value")
                }
            )
            params_context.update(
                {
                    "params_%s" % item["key"]: item["value"]
                    for item in TicketGlobalVariable.objects.filter(ticket_id=ticket_id).values("key", "value")
                }
            )

        template = params.get("meta", {})
        try:
            query_params = json.loads(Template(json.dumps(template)).render(**params_context))
        except Exception as e:
            logger.warning("Template text=%s, context=%s, error=%s" % (template, params, e))
            return False, []

        if rpc_source == TRIGGER_SOURCE:
            # 触发器默认增加两个参数
            try:
                trigger = Trigger.objects.get(id=params.get("rpc_source_id"))
            except Trigger.DoesNotExist:
                return False, []
            query_params.update({"trigger_source_id": trigger.source_id, "trigger_source_type": trigger.source_type})
        return True, query_params

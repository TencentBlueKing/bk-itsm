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

__author__ = u"蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

from django.core.cache import cache
from itsm.component.constants import PREFIX_KEY
from .models import WorkflowVersion


def get_first_state(flow):
    """获取第一个节点的接口"""
    cache_key = "%sfirst_state_%s" % (PREFIX_KEY, flow.id)
    first_state = cache.get(cache_key)
    if not first_state:
        first_state = flow.first_state
        cache.set(cache_key, first_state, 30)
    return first_state


def get_ticket_flow(flow_id):
    """获取单据的flow"""
    cache_key = "%sversion_flow_%s" % (PREFIX_KEY, flow_id)
    flow = cache.get(cache_key)
    if not flow:
        flow = WorkflowVersion._objects.get(id=flow_id)
        cache.set(cache_key, flow, 30)
    return flow

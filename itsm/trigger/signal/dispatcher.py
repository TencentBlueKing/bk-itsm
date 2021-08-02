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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

from django.dispatch.dispatcher import (
    NO_RECEIVERS,
    Signal,
)


class TriggerSignal(Signal):
    def send(self, signal_name, sender, source_type, source_id, **named):
        """Send the signal"""

        if not self.receivers or self.sender_receivers_cache.get(sender) is NO_RECEIVERS:
            return []

        # 通过sender，可以获取到对应的触发器
        sender_condition = dict(
            signal=signal_name,
            source_type=named.get("rule_source_type", 'workflow_version'),
            source_id=named.get("rule_source_id"),
        )
        if sender:
            sender_condition['sender'] = sender

        return [
            (
                receiver,
                receiver(signal=self, sender=sender_condition, source_type=source_type, source_id=source_id, **named),
            )
            for receiver in self._live_receivers(sender)
        ]

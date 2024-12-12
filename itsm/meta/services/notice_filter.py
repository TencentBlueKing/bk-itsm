# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C)2024 THL A29 Limited, a Tencent company.  All rights reserved.

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
from itsm.meta.services.context import ContextService


class NoticeFilterService:
    @staticmethod
    def notice_receiver_filter(receivers):
        """通知名单过滤"""
        if not receivers:
            return receivers

        receiver_type = "list"
        if isinstance(receivers, str):
            receiver_type = "str"
            receivers = receivers.strip().split(",")

        notice_blacklist = ContextService.get_context_value_list("notice_blacklist")
        filtered_receivers = [i for i in receivers if i not in notice_blacklist]
        return (
            filtered_receivers
            if receiver_type == "list"
            else ",".join(filtered_receivers)
        )

    @staticmethod
    def get_service_approval_blacklist():
        """获取审批服务黑名单"""
        return ContextService.get_context_value_list("service_approval_blacklist")


notice_filter_service = NoticeFilterService()

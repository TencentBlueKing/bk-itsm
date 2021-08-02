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

from collections import defaultdict

from itsm.component.db import managers


class Manager(managers.Manager):
    """支持软删除"""

    pass


class TicketStatusManager(Manager):
    """单据状态表级操作"""

    def status_of_service_type(self, service_type):
        """指定服务类型下所有工单状态"""
        return self.filter(service_type=service_type)

    def get_status_choice(self, service_type):
        """指定服务类型下所有工单状态选项"""
        return list(self.status_of_service_type(service_type).values("key", "name"))

    def get_is_over_statuses(self):
        """获取各个服务类型下的结束状态"""
        ret = defaultdict(list)
        is_over_statuses = self.filter(is_over=True)

        for status in is_over_statuses:
            ret[status.service_type].append(status.key)

        return ret

    def get_overall_status_names(self, exclude_keys=None):
        """
        :param exclude_keys: 排除指定单据状态key
        """
        if exclude_keys is None:
            exclude_keys = []

        status_info = list(self.exclude(key__in=exclude_keys).order_by("order").values("key", "name"))
        no_repeat_names = {}
        # 在保证顺序的前提下, 对列表元素去重
        for info in status_info:
            if info["key"] not in no_repeat_names:
                no_repeat_names[info["key"]] = info["name"]
        return no_repeat_names


class TicketStatusConfigManager(Manager):
    """单据状态配置"""

    pass


class StatusTransitManager(Manager):
    """状态转换规则"""

    pass

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


from itsm.component.constants import PX_URGENCY, PY_IMPACT, SERVICE_LIST
from itsm.component.db import managers


class Manager(managers.Manager):
    """支持软删除"""

    pass


class SlaManager(managers.Manager):
    """Sla管理器"""

    pass


class PriorityMatrixManager(managers.Manager):
    """PriorityMatrix管理器"""

    def get_priority(self, service_type, urgency, impact):
        """获取优先级"""
        return self.get(service_type=service_type, urgency=urgency, impact=impact).priority

    def init_matrix(self):
        """初始化优先级矩阵"""

        from itsm.service.models import SysDict

        def simple_get_priority(urgency, impact):
            """简单计算优先级"""
            val = urgency * impact

            if val < 4:
                return 1
            elif val < 7:
                return 2
            else:
                return 3

        if self.exists():
            print("skip init matrix")
            return

        services = []
        for service in SERVICE_LIST:
            for px_urgency in SysDict.get_data_by_key(PX_URGENCY, "list"):
                for py_impact in SysDict.get_data_by_key(PY_IMPACT, "list"):
                    urgency = int(px_urgency["key"])
                    impact = int(py_impact["key"])
                    services.append(
                        self.model(
                            service_type=service,
                            urgency=urgency,
                            impact=impact,
                            priority=simple_get_priority(urgency, impact),
                        )
                    )

        self.bulk_create(services)

    def get_dict_datas(self, service_type, key):
        """获取指定服务类型下 影响范围/紧急程度的数据字典
        :param: service_type 服务类型
        :param: key PY_IMPACT/PX_URGENCY
        """

        from itsm.service.models import SysDict

        enabled_key = "%s_%s" % (service_type.upper(), key)
        enabled_keys = SysDict.get_data_by_key(enabled_key, "sets")
        dict_datas = SysDict.get_data_by_key(key)

        for dict_data in dict_datas:
            if dict_data["key"] in enabled_keys:
                dict_data["is_enabled"] = True
            else:
                dict_data["is_enabled"] = False

        return dict_datas

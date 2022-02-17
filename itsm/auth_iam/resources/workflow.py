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

from django.db.models import Q

# from iam import PathEqDjangoQuerySetConverter
from itsm.auth_iam.resources import ItsmResourceProvider
from itsm.workflow.models import Workflow
from .basic import ItsmResourceListResult as ListResult


def flow_path_value_hook(value):
    # get id in "/project,id/"
    return value[1:-1].split(",")[1]


class WorkFlowResourceProvider(ItsmResourceProvider):
    queryset = Workflow.objects.filter(is_builtin=False)

    def list_instance(self, filter, page, **options):
        """
        flow 上层资源为 project
        """
        queryset = []
        with_path = False

        if not (filter.parent or filter.search or filter.resource_type_chain):
            queryset = self.queryset
        elif filter.parent:
            parent_id = filter.parent["id"]
            if parent_id:
                queryset = self.queryset
                # todo: add project
                # queryset = Workflow.objects.filter(project_id=str(parent_id))
        elif filter.search and filter.resource_type_chain:
            # 返回结果需要带上资源拓扑路径信息
            with_path = True

            project_keywords = filter.search.get("project", [])
            flow_keywords = filter.search.get("flow", [])

            project_filter = Q()
            flow_filter = Q()

            for keyword in project_keywords:
                project_filter |= Q(name__icontains=keyword)

            for keyword in flow_keywords:
                flow_filter |= Q(name__icontains=keyword)

            queryset = self.queryset
            # todo: add project
            # project_ids = Project.objects.filter(project_filter).values_list("id", flat=True)
            # queryset = Workflow.objects.filter(project_id__in=list(project_ids)).filter(flow_filter)

        count = queryset.count()
        results = [
            {"id": str(flow.id), "display_name": flow.name}
            for flow in queryset[page.slice_from : page.slice_to]
        ]

        if with_path:
            results = [
                {
                    "id": str(flow.id),
                    "display_name": flow.name,
                    "path": [
                        [
                            {
                                "type": "project",
                                "id": 0,
                                "display_name": flow.project.name,
                            }
                        ]
                    ],
                }
                for flow in queryset[page.slice_from : page.slice_to]
            ]

        return ListResult(results=results, count=count)

    def fetch_instance_info(self, filter, **options):
        """
        flow 没有定义属性，只处理 filter 中的 ids 字段
        """
        ids = []
        if filter.ids:
            ids = [int(i) for i in filter.ids]

        results = [
            {
                "id": str(flow.id),
                "display_name": flow.name,
                "_bk_iam_approver_": self.get_bk_iam_approver(flow.creator),
            }
            for flow in Workflow.objects.filter(id__in=ids)
        ]
        return ListResult(results=results)

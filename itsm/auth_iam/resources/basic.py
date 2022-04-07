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

from django.core.cache import cache

import settings
from iam.resource.provider import ResourceProvider, ListResult
from iam.contrib.django.dispatcher.exceptions import InvalidPageException
from itsm.component.constants.iam import IAM_SEARCH_INSTANCE_CACHE_TIME


class ItsmResourceListResult(ListResult):
    def __init__(self, results, count=0):
        self.with_path = False
        self.count = count or len(results)
        super(ItsmResourceListResult, self).__init__(results, self.count)


class ItsmResourceProvider(ResourceProvider):
    queryset = None

    def filter_queryset(self, filter):

        if filter.keyword:
            queryset = self.queryset.filter(name__icontains=filter.keyword)

        return queryset

    def get_bk_iam_approver(self, creator):
        if creator in ["system", None]:
            return list(settings.INIT_SUPERUSER)
        return creator.split(",")

    @staticmethod
    def pre_search_instance(filter, page, **options):
        if page.limit == 0 or page.limit > 1000:
            raise InvalidPageException("limit in page too large")

    def list_attr(self, **options):
        return ItsmResourceListResult(results=[])

    def list_attr_value(self, filter, page, **options):
        return ItsmResourceListResult(results=[])

    def list_instance(self, filter, **options):
        return ItsmResourceListResult(results=[])

    def search_instance(self, filter, page, **options):
        """
        所有资源统一默认的内容
        """

        keyword = filter.keyword
        keyword_cache_key = "%s_%s" % (self.queryset.model._meta.model_name, keyword)

        results = cache.get(keyword_cache_key)
        if results is None:
            queryset = self.filter_queryset(filter)
            results = [
                {"id": str(instance.id), "display_name": instance.name}
                for instance in queryset[page.slice_from : page.slice_to]
            ]

            cache.set(keyword_cache_key, results, IAM_SEARCH_INSTANCE_CACHE_TIME)

        return ListResult(results=results, count=len(results))

    def fetch_instance_info(self, filter, **options):
        return ItsmResourceListResult(results=[])

    def list_instance_by_policy(self, filter, page, **options):
        return ItsmResourceListResult(results=[])

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

from rest_framework import filters


class OrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        orderings = self.get_ordering(request, queryset, view)

        if orderings:
            custom_ordering = self.get_custom_ordering(request, view, orderings)
            return queryset.extra(select=custom_ordering, order_by=orderings)

        return queryset

    @staticmethod
    def get_ordering_class(view):
        return getattr(view, 'ordering_class', None)

    def get_custom_ordering(self, request, view, orderings):
        custom_ordering = {}
        ordering_class = self.get_ordering_class(view)

        # viewset whether to define ordering class
        if ordering_class:
            for index, order_name in enumerate(orderings):
                reverse = order_name.startswith('-')
                order_func = getattr(ordering_class, order_name.lstrip('-'), None)

                # ordering class whether to define order method, Note: method name cannot be the same as field name
                if order_func:
                    custom_order = order_func(reverse, request)
                    custom_order_name = order_name.lstrip('-')
                    custom_ordering.update(**{custom_order_name: custom_order})
                    orderings[index] = custom_order_name

        return custom_ordering

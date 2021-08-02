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

from collections import OrderedDict

import six
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination, _positive_int
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
        自定义分页格式，综合页码和url
    """

    page_size_query_param = 'page_size'
    max_page_size = 10000

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ('page', self.page.number),
                    ('total_page', self.page.paginator.num_pages),
                    ('count', self.page.paginator.count),
                    ('next', self.get_next_link()),
                    ('previous', self.get_previous_link()),
                    ('items', data),
                ]
            )
        )

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ('page', self.page.number),
                ('total_page', self.page.paginator.num_pages),
                ('count', self.page.paginator.count),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('items', data),
            ]
        )


class OpenApiPageNumberPagination(CustomPageNumberPagination):
    """
    兼容post 与 get 分页
    """

    def get_page_size(self, request):

        page_size = 10
        if self.page_size_query_param in request.query_params:
            page_size = request.query_params.get(self.page_size_query_param, 10)
        elif request.method == "POST":
            page_size = request.data.get(self.page_size_query_param, 10)
            
        if self.page_size_query_param:
            try:
                return _positive_int(
                    page_size,
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = 1
        if self.page_query_param in request.query_params:
            page_number = request.query_params.get(self.page_query_param, 1)
        elif request.method == "POST":
            page_number = request.data.get(self.page_query_param, 1)

        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

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


#: List containing string constant that are used to represent headers that can
#: be ignored in the required_header function
IGNORE_HEADERS = (
    "HTTP_ACCEPT_ENCODING",  # We want content to be uncompressed so
    # we remove the Accept-Encoding from
    # original request
    "HTTP_HOST",
    "HTTP_REMOTE_USER",
)


def required_header(header):
    """Function that verify if the header parameter is a essential header

    :param header:  A string represented a header
    :returns:       A boolean value that represent if the header is required
    """
    if header in IGNORE_HEADERS:
        return False

    if header.startswith("HTTP_") or header == "CONTENT_TYPE":
        return True

    return False


def normalize_request_headers(request):
    """Function used to transform header, replacing 'HTTP_' to ''
    and replace '_' to '-'
    :param request:  A HttpRequest that will be transformed
    :returns:        A dictionary with the normalized headers
    """
    norm_headers = {}
    for header, value in request.META.items():
        if required_header(header):
            norm_header = header.replace("HTTP_", "").title().replace("_", "-")
            norm_headers[norm_header] = value

    return norm_headers

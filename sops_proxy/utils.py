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
from wsgiref.util import is_hop_by_hop

from django.http import HttpResponse, StreamingHttpResponse

#: Default number of bytes that are going to be read in a file lecture
from revproxy.utils import should_stream, cookie_from_string

from common.log import logger

DEFAULT_AMT = 2 ** 16

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


def set_response_headers(response, response_headers):
    # check for Django 3.2 headers interface
    # https://code.djangoproject.com/ticket/31789
    # check and set pointer before loop to improve efficiency
    if hasattr(response, "headers"):
        headers = response.headers
    else:
        headers = response

    for header, value in response_headers.items():
        if is_hop_by_hop(header) or header.lower() == "set-cookie":
            continue

        headers[header] = value

    if hasattr(response, "headers"):
        logger.debug("Response headers: %s", response.headers)
    else:
        logger.debug("Response headers: %s", getattr(response, "_headers"))


def get_django_response(proxy_response, strict_cookies=False):
    """This method is used to create an appropriate response based on the
    Content-Length of the proxy_response. If the content is bigger than
    MIN_STREAMING_LENGTH, which is found on utils.py,
    than django.http.StreamingHttpResponse will be created,
    else a django.http.HTTPResponse will be created instead

    :param proxy_response: An Instance of urllib3.response.HTTPResponse that
                           will create an appropriate response
    :param strict_cookies: Whether to only accept RFC-compliant cookies
    :returns: Returns an appropriate response based on the proxy_response
              content-length
    """
    status = proxy_response.status
    headers = proxy_response.headers

    logger.debug("Proxy response headers: %s", headers)

    content_type = headers.get("Content-Type")

    logger.debug("Content-Type: %s", content_type)

    if should_stream(proxy_response):
        logger.info("Content-Length is bigger than %s", DEFAULT_AMT)
        response = StreamingHttpResponse(
            proxy_response.stream(DEFAULT_AMT), status=status, content_type=content_type
        )
    else:
        content = proxy_response.data or b""
        response = HttpResponse(content, status=status, content_type=content_type)

    logger.info("Normalizing response headers")
    set_response_headers(response, headers)

    # logger.debug('Response headers: %s', getattr(response, '_headers'))

    cookies = proxy_response.headers.getlist("set-cookie")
    logger.info("Checking for invalid cookies")
    for cookie_string in cookies:
        cookie_dict = cookie_from_string(cookie_string, strict_cookies=strict_cookies)
        # if cookie is invalid cookie_dict will be None
        if cookie_dict:
            response.set_cookie(**cookie_dict)

    logger.debug("Response cookies: %s", response.cookies)

    return response

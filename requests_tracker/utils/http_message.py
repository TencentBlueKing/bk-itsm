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

# requests_tracker.utils.http_message
# ===================================

import json
from urllib.parse import urlsplit

from django.template.loader import get_template


def render_request_message(prepared_request, private_words=None):
    if private_words is None:
        private_words = []
    try:
        tmpl = get_template('requests_tracker/request.tmpl')
        message = tmpl.render({'prep': prepared_request, 'host': urlsplit(prepared_request.url).netloc, })

        # 敏感词处理
        for pw in private_words:
            message = message.replace(pw, "******")

        return message
    except BaseException:
        return ""


def render_response_message(response):
    try:
        json.loads(response.text)
        return response.text
    except ValueError:
        tmpl = get_template('requests_tracker/response.tmpl')
        return tmpl.render({'response': response})
    except BaseException:
        return response.text if response else ""

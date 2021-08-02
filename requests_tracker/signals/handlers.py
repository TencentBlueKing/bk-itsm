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

# requests_tracker.signals.handlers
# =================================

import logging
from urllib.parse import urlsplit, urlunsplit

from django.conf import settings

from itsm.component.constants import INNER_API_INSTANCE_ID, INNER_STATE_ID, INNER_TICKET_ID
from requests_tracker.filtering import filters
from requests_tracker.models import Record
from requests_tracker.utils.http_message import render_request_message, render_response_message


logger = logging.getLogger(__name__)


def get_url(prep):
    _ = urlsplit(prep.url)
    return urlunsplit((_.scheme, _.netloc, _.path, '', ''))


def response_handler(sender, uid, prep, resp, duration, **kwargs):
    """handle `requests_tracker.signals.response` signal"""

    if not filters.rt_filter(prep, **kwargs):
        return

    try:
        Record.objects.create(
            uid=uid,
            url=get_url(prep),
            api_uid=kwargs.get('api_uid', ''),
            operator=kwargs.get('operator', ''),
            state_id=kwargs.get(INNER_STATE_ID, 0),
            ticket_id=kwargs.get(INNER_TICKET_ID, 0),
            api_instance_id=kwargs.get(INNER_API_INSTANCE_ID, 0),
            method=prep.method,
            request_message=render_request_message(prep, [settings.SECRET_KEY]),
            status_code=resp.status_code,
            response_message=render_response_message(resp)[0 : 2048 * 8],
            remark=resp.reason,
            duration=duration,
            request_host=resp.raw._original_response.peer,
        )
    except Exception as e:
        logger.warning("save response record error: %s" % str(e))
        return


def request_failed_handler(sender, uid, prep, exception, duration, **kwargs):
    """handle `requests_tracker.signals.request_failed` signal"""

    if not filters.rt_filter(prep, **kwargs):
        return

    try:
        Record.objects.create(
            uid=uid,
            url=get_url(prep),
            api_uid=kwargs.get('api_uid', ''),
            operator=kwargs.get('operator', ''),
            state_id=kwargs.get(INNER_STATE_ID, 0),
            ticket_id=kwargs.get(INNER_TICKET_ID, 0),
            api_instance_id=kwargs.get(INNER_API_INSTANCE_ID, 0),
            method=prep.method,
            request_message=render_request_message(prep),
            remark=exception.__class__.__name__,
            response_message=exception.message,
            duration=duration,
        )
    except Exception as e:
        logger.warning("save failed response record error: %s" % str(e))
        return

    raise exception

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

from django.dispatch import Signal
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import ugettext as _

from itsm.component.utils.local import local


class AccessorSignal(Signal):
    allowed_receiver = 'itsm.component.request_middlewares.RequestProvider'

    def __init__(self, providing_args=None):
        Signal.__init__(self, providing_args)

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        receiver_name = '.'.join([receiver.__class__.__module__, receiver.__class__.__name__])
        if receiver_name != self.allowed_receiver:
            raise Exception(_("%s is not allowed to connect") % receiver_name)
        if not self.receivers:
            Signal.connect(self, receiver, sender, weak, dispatch_uid)


request_accessor = AccessorSignal()


class RequestProvider(MiddlewareMixin):
    """
    @summary: request事件接收者
    """

    def __init__(self):
        request_accessor.connect(self)

    def process_request(self, request):
        local.current_request = request
        return None

    def process_response(self, request, response):
        if hasattr(local, 'current_request'):
            assert request is local.current_request
            del local.current_request

        return response

    def __call__(self, **kwargs):
        if not hasattr(local, 'current_request'):
            raise Exception(_("get_request can't be called in a new thread."))
        return local.current_request


def get_request():
    if hasattr(local, 'current_request'):
        return local.current_request
    else:
        raise Exception(_("get_request: current thread hasn't request."))


def get_x_request_id():
    x_request_id = ''
    http_request = get_request()
    if hasattr(http_request, 'META'):
        meta = http_request.META
        x_request_id = meta.get('HTTP_X_REQUEST_ID', '') if isinstance(meta, dict) else ''
    return x_request_id

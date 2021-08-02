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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

# ESB封装类，拷贝自`数据平台`，修改自
# https://github.com/LLK/django-request-provider/blob/master/request_provider/signals.py
# 
# 建议进一步考察TODO项，涉及线程安全问题
# 
# since each thread has its own greenlet we can just use those as identifiers
# for the context.  If greenlets are not available we fall back to the
# current thread ident depending on where it is.

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from _thread import get_ident
    except ImportError:
        from _thread import get_ident

from django.dispatch import Signal
from django.utils.translation import ugettext as _


class UnauthorizedSignalReceiver(Exception):
    pass


class SingleHandlerSignal(Signal):
    """
    与 RequestProvider 中间件搭配使用
    """

    allowed_receiver = 'itsm.component.middlewares.RequestProvider'

    def __init__(self, providing_args=None):
        Signal.__init__(self, providing_args)
        self.bind_times = 0

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        # TODO 拷贝过来时的缺陷记录：
        # 一般情况下中间件只会被初始化一次，在不明情况下，中间件会在用户请求后，再初始化一次
        # 目前先姑且认定这种情况的初始化属于异常情况不进行信号绑定
        if self.bind_times >= 1:
            return

        receiver_name = '.'.join([receiver.__class__.__module__, receiver.__class__.__name__])
        if receiver_name != self.allowed_receiver:
            raise UnauthorizedSignalReceiver(_("%s is not allowed to connect") % receiver_name)
        Signal.connect(self, receiver, sender, weak, dispatch_uid)
        self.bind_times += 1


request_accessor = SingleHandlerSignal()


class RequestProvider(object):
    """
    与 AccessorSignal 搭建使用，request 事件接收者
    """

    def __init__(self):
        self._request_pool = {}
        request_accessor.connect(self)

    def process_request(self, request, **kwargs):
        # TODO 通过请求池解决线程安全问题？
        self._request_pool[get_ident()] = request
        return None

    def process_response(self, request, response):
        # TODO 这里线程安全吗？
        assert request is self._request_pool.pop(get_ident())
        return response

    def __call__(self, *args, **kwargs):
        # TODO 仅对信号反馈？
        from_signal = kwargs.get('from_signal', False)
        if from_signal:
            return self.get_request(**kwargs)
        else:
            return None

    def get_request(self, **kwargs):
        # 取线程标识？
        sender = kwargs.get("sender")
        if sender is None:
            sender = get_ident()
        if sender not in self._request_pool:
            raise UnauthorizedSignalReceiver(_("get_request can't be called in a new thread."))
        return self._request_pool[sender]


def get_x_request_id():
    x_request_id = ''
    http_request = get_request()
    if hasattr(http_request, 'META'):
        meta = http_request.META
        x_request_id = meta.get('HTTP_X_REQUEST_ID', '') if isinstance(meta, dict) else ''
    return x_request_id


def get_request():
    return request_accessor.send(get_ident(), from_signal=True)[0][1]

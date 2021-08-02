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

import logging
import traceback

from .models import Signal

logger = logging.getLogger(__name__)


def set_valve_function(func):
    global __valve_function
    if __valve_function is not None:
        raise Exception("valve function can only be set once.")
    if not callable(func):
        raise Exception("valve function must be a callable object")

    __valve_function = func


def send(signal_mod, signal_name, **kwargs):
    if not __valve_function or not __valve_function():
        try:
            return getattr(signal_mod, signal_name).send(**kwargs)
        except Exception:
            raise
    else:
        Signal.objects.dump(signal_mod.__path__, signal_name, kwargs)
        return None


def open_valve(signal_mod):
    signal_list = Signal.objects.filter(
        module_path=signal_mod.__path__).order_by("id")
    response = []
    for signal in signal_list:
        try:
            response.append(
                getattr(
                    signal_mod,
                    signal.name).send(
                    **signal.kwargs))
            signal.delete()
        except Exception as e:
            logger.error('signal(%s - %s) resend failed: %s' %
                         (signal.module_path, signal.name, traceback.format_exc(e)))
    return response


def unload_valve_function():
    global __valve_function
    __valve_function = None


def valve_function():
    return __valve_function


__valve_function = None

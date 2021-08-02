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

import sys
from collections import namedtuple


PY2 = sys.version_info[0] == 2

# Taken from https://github.com/HypothesisWorks/hypothesis/pull/625/files#diff-e84a85b835af44101e1986c47ba39630R264
if PY2:
    FullArgSpec = namedtuple('FullArgSpec', 'args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations')

    def getfullargspec(func):
        import inspect
        args, varargs, varkw, defaults = inspect.getargspec(func)
        return FullArgSpec(args, varargs, varkw, defaults, [], None, {})
else:
    from inspect import getfullargspec

    if sys.version_info[:2] == (3, 5):
        # silence deprecation warnings on Python 3.5
        # (un-deprecated in 3.6 to allow single-source 2/3 code like this)
        def silence_warnings(func):
            import warnings
            import functools

            @functools.wraps(func)
            def inner(*args, **kwargs):
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    return func(*args, **kwargs)
            return inner

        getfullargspec = silence_warnings(getfullargspec)

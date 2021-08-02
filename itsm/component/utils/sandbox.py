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

# import requests
from RestrictedPython import compile_restricted, safe_globals, safe_builtins, utility_builtins  # noqa
from RestrictedPython.Guards import guarded_iter_unpack_sequence  # noqa
from RestrictedPython.Eval import default_guarded_getiter, default_guarded_getitem, default_guarded_getattr  # noqa
from RestrictedPython._compat import IS_CPYTHON  # noqa


def map_data(source_code, data, key='response'):
    '''
        bk.http->map_data

        response = {'result': True, 'data': {'a': 1, 'b': 2, 'c': 3}}
        source_code = """
        def map(response):
            return [{'id': k, 'name': v} for k, v in response['data'].items()]
        result = map(response)
        """
        source_code = """
        result = [{'id': k, 'name': v} for k, v in response['data'].items()]
        """
    '''

    if not (source_code and IS_CPYTHON):
        return data

    # limited_globals = safe_globals.copy()
    # limited_globals.update(
    #     {
    #         '_getitem_': default_guarded_getitem,
    #         '_getiter_': default_guarded_getiter,
    #         '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
    #     }
    # )
    import json

    available_attrs = {
        '_getitem_': default_guarded_getitem,
        '_getiter_': default_guarded_getiter,
        '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
        'enumerate': enumerate,
        'json': json,
        # 'requests': requests,
    }

    limited_globals = {'__builtins__': {**safe_builtins, **utility_builtins}, **available_attrs}

    try:
        byte_code = compile_restricted(
            source_code,
            '<inline>',
            'exec',
            # policy=None
        )
        limited_locals = {key: data}
        exec(byte_code, limited_globals, limited_locals)
        return limited_locals.get(key, data)
    except SyntaxError:
        return data

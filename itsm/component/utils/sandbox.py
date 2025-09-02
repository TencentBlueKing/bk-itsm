# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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
import json

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

    available_attrs = {
        '_getitem_': default_guarded_getitem,
        '_getiter_': default_guarded_getiter,
        '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
        'enumerate': enumerate,
        # 最小暴露 JSON
        'json_loads': json_loads,
    }

    # 安全：删除 utility_builtins 中的 'string'
    utility = dict(utility_builtins)
    utility.pop('string', None)

    limited_globals = {'__builtins__': {**safe_builtins, **utility}, **available_attrs}

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


def json_loads(s):
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # 如果无法解析，直接返回原值
        return s

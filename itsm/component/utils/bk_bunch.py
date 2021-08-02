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


# 重写两个函数，兼容py3

from .bunch import Bunch as BaseBunch


class Bunch(BaseBunch):
    pass


def bunchify(x):
    """ Recursively transforms a dictionary into a Bunch via copy.

        >>> b = bunchify({'urmom': {'sez': {'what': 'what'}}})
        >>> b.urmom.sez.what
        'what'

        bunchify can handle intermediary dicts, lists and tuples (as well as
        their subclasses), but ymmv on custom datatypes.

        >>> b = bunchify({ 'lol': ('cats', {'hah':'i win again'}),
        ...         'hello': [{'french':'salut', 'german':'hallo'}] })
        >>> b.hello[0].french
        'salut'
        >>> b.lol[1].hah
        'i win again'

        nb. As dicts are not hashable, they cannot be nested in sets/frozensets.
    """
    if isinstance(x, dict):
        return Bunch((k, bunchify(v)) for k, v in x.items())
    elif isinstance(x, (list, tuple)):
        return type(x)(bunchify(v) for v in x)
    else:
        return x


def unbunchify(x):
    """ Recursively converts a Bunch into a dictionary.

        >>> b = Bunch(foo=Bunch(lol=True), hello=42, ponies='are pretty!')
        >>> unbunchify(b)
        {'ponies': 'are pretty!', 'foo': {'lol': True}, 'hello': 42}

        unbunchify will handle intermediary dicts, lists and tuples (as well as
        their subclasses), but ymmv on custom datatypes.

        >>> b = Bunch(foo=['bar', Bunch(lol=True)], hello=42,
        ...         ponies=('are pretty!', Bunch(lies='are trouble!')))
        >>> unbunchify(b) #doctest: +NORMALIZE_WHITESPACE
        {'ponies': ('are pretty!', {'lies': 'are trouble!'}),
         'foo': ['bar', {'lol': True}], 'hello': 42}

        nb. As dicts are not hashable, they cannot be nested in sets/frozensets.
    """
    if isinstance(x, dict):
        return dict((k, unbunchify(v)) for k, v in x.items())
    elif isinstance(x, (list, tuple)):
        return type(x)(unbunchify(v) for v in x)
    else:
        return x


def get_data_by_key(key, data):
    """
    根据指定的可以获取到对应属性的值
    """
    data = bunchify(data)
    get_dst_attr_bunch = 'dst_attr_bunch = data.%s' % key
    exec(get_dst_attr_bunch)
    return unbunchify(locals()["dst_attr_bunch"])

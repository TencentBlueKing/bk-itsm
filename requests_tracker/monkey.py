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

# """
# requests_tracker.monkey
# =======================
# """

from django.utils.translation import ugettext_lazy as _


__all__ = [
    'patch_all',
    'patch_module',
]

targets = {
    'requests.sessions': None,
}


def patch_module(name, items=None):
    """
    The codes below comes from gevent.monkey.patch_module()
    """
    rt_module = __import__('requests_tracker.' + name)
    target_module = __import__(name)
    for i, submodule in enumerate(name.split('.')):
        rt_module = getattr(rt_module, submodule)
        if i:
            target_module = getattr(target_module, submodule)
    items = items or getattr(rt_module, '__implements__', None)
    if items is None:
        items = getattr(rt_module, '__implements__', None)
        if items is None:
            raise AttributeError(
                _('%r does not have __implements__') %
                rt_module)
    for attr in items:
        setattr(target_module, attr, getattr(rt_module, attr))
    return target_module


def patch_all():
    for module, items in targets.items():
        patch_module(module, items=items)

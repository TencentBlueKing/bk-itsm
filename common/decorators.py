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


# 
# @summary: 装饰器
# @usage：
#           >>> from common.decorators import escape_exempt, escape_script, escape_url
#           >>> @escape_exempt()
#           >>> @escape_script()
#           >>> @escape_url()
#           >>> def test_func(request):
#           >>>     pass
# 

# from django.utils.decorators import available_attrs


try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.


# ===============================================================================
# 转义装饰器
# ===============================================================================
def escape_exempt(view_func):
    """
    转义豁免，被此装饰器修饰的action可以不进行中间件escape
    """
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.escape_exempt = True
    return wraps(view_func)(wrapped_view)


def escape_texteditor(view_func):
    """
    被此装饰器修饰的action会对GET与POST参数作为富文本编辑内容处理
    """
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.escape_script = True
    return wraps(view_func)(wrapped_view)


def escape_url(view_func):
    """
    被此装饰器修饰的action会对GET与POST参数进行url escape
    """
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.escape_url = True
    return wraps(view_func)(wrapped_view)

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

# http://stackoverflow.com/questions/32877365/scikit-random-forest-regressor-attributeerror
# -thread-object-has-no-attrib
# AttributeError: 'Thread' object has no attribute '_children'
# This probably happens due to a bug in multiprocessing.dummy (see here and here) that existed
# before python 2.7.5 and 3.3.2.
# 
# Solution A - Upgrade Python
# 
# Solution B - Modify dummy
# multiprocessing/dummy/__init__.py, edit the start method within the DummyProcess class as follows
# if hasattr(self._parent, '_children'):  # add this line
#    self._parent._children[self] = None  # indent this existing line
# 
# 
# Solution C - Monkey Patch
# Let's make it available in our namespace:
# from multiprocessing import dummy as __mp_dummy
# 
#  Now we can define a replacement and patch DummyProcess:
# def __DummyProcess_start_patch(self):  # pulled from an updated version of Python
#     assert self._parent is __mp_dummy.current_process()  # modified to avoid further imports
#     self._start_called = True
#     if hasattr(self._parent, '_children'):
#         self._parent._children[self] = None
#     __mp_dummy.threading.Thread.start(self)  # modified to avoid further imports
# __mp_dummy.DummyProcess.start = __DummyProcess_start_patch


from multiprocessing.dummy import Pool as ThreadPool

from django.utils.translation import ugettext as _


# 线程池容量上限
POOL_SIZE = 20


def batch_process(func, args_list, pool_size=POOL_SIZE):
    """
    批量并行执行
    """

    def merge_data(data):
        """
        批量结果统计汇总，返回错误信息
        """
        success_list, fail_list = [], []
        for res in data:
            if res.get("result") is True:
                success_list.append(res.get("data"))
            else:
                fail_list.append(res)

        # [0]-all ok [1]-part ok [-1]-all fail
        result, code = True, 0
        if fail_list:
            result, code = False, 1
            if len(fail_list) == len(data):
                result, code = False, -1

        return {
            "result": result,
            "code": code,
            "data": success_list,
            "fail": fail_list,
            "message": {
                0: _("all success, data list in key success"),
                1: _("part fail, please read detail info in key fail"),
                -1: _("all fail, please read detail info in key fail"),
            }.get(code),
        }

    pool = ThreadPool(pool_size)
    map_data = pool.map(func, args_list)
    pool.close()
    pool.join()

    return merge_data(map_data)

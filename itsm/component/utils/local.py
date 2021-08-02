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


# """Thread-local/Greenlet-local objects
# 
# Thread-local/Greenlet-local objects support the management of
# thread-local/greenlet-local data. If you have data that you want
# to be local to a thread/greenlet, simply create a
# thread-local/greenlet-local object and use its attributes:
# 
#   >>> mydata = Local()
#   >>> mydata.number = 42
#   >>> mydata.number
#   42
#   >>> hasattr(mydata, 'number')
#   True
#   >>> hasattr(mydata, 'username')
#   False
# 
#   Reference :
#   from threading import local
# """


try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from _thread import get_ident
    except ImportError:
        from _thread import get_ident

__all__ = ["local", "Local"]


class Localbase(object):

    __slots__ = ('__storage__', '__ident_func__')

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls, *args, **kwargs)
        object.__setattr__(self, '__storage__', {})
        object.__setattr__(self, '__ident_func__', get_ident)
        return self


class Local(Localbase):
    def __iter__(self):
        ident = self.__ident_func__()
        return iter(list(self.__storage__[ident].items()))

    def __release_local__(self):
        self.__storage__.pop(self.__ident_func__(), None)

    def __getattr__(self, name):
        ident = self.__ident_func__()
        try:
            return self.__storage__[ident][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ('__storage__', '__ident_func__'):
            raise AttributeError("%r object attribute '%s' is read-only" % (self.__class__.__name__, name))

        ident = self.__ident_func__()
        storage = self.__storage__
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}

    def __delattr__(self, name):
        if name in ('__storage__', '__ident_func__'):
            raise AttributeError("%r object attribute '%s' is read-only" % (self.__class__.__name__, name))

        ident = self.__ident_func__()
        try:
            del self.__storage__[ident][name]
            if len(self.__storage__[ident]) == 0:
                self.__release_local__()
        except KeyError:
            raise AttributeError(name)


local = Local()


if __name__ == '__main__':

    def display(id):
        # import time
        local.id = id
        for i in range(3):
            print(get_ident(), local.id, "\n")
            # time.sleep(1)

    def gree(id):
        import gevent

        t = []
        for i in range(10):
            t.append(gevent.spawn(display, "%s-%s" % (id, i)))
        gevent.joinall(t)

    # test one
    # l1 = Local()
    # l2 = Local()
    # l.xxx = 1
    # print l.xxx
    # print l1.xxx
    # print l2.xxx

    # test two
    # import gevent
    # t = []
    # for i in range(10):
    #     g = gevent.spawn(display, i)
    #     t.append(g)
    # gevent.joinall(t)

    # test three
    import threading

    t = []
    for i in range(10):
        t.append(threading.Thread(target=gree, args=(i,)))

    [th.start() for th in t]
    [th.join() for th in t]

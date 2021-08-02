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

import zlib

from django.db import models
from django.utils.translation import ugettext_lazy as _

try:
    import pickle as pickle
except Exception:
    import pickle



class IOField(models.BinaryField):
    def __init__(self, compress_level=6, *args, **kwargs):
        super(IOField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level

    def get_prep_value(self, value):
        value = super(IOField, self).get_prep_value(value)
        return zlib.compress(pickle.dumps(value), self.compress_level)

    def to_python(self, value):
        value = super(IOField, self).to_python(value)
        return pickle.loads(zlib.decompress(value))

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)


class SignalManager(models.Manager):
    def dump(self, module_path, signal_name, kwargs):
        self.create(module_path=module_path, name=signal_name, kwargs=kwargs)


class Signal(models.Model):
    module_path = models.TextField(_("信号模块名"))
    name = models.CharField(_("信号属性名"), max_length=64)
    kwargs = IOField(verbose_name=_("信号参数"))

    objects = SignalManager()

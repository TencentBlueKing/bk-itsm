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

from django.core.files.storage import Storage


class CephStorage(Storage):
    """Ceth文件系统存储类"""

    _storage = None

    @property
    def storage(self):
        from bkstorages.backends.rgw import RGWBoto3Storage

        if self._storage is None:
            self._storage = RGWBoto3Storage()

        return self._storage

    def save(self, name, content, max_length=None):
        """保存文件"""
        return self.storage.save(name, content, max_length)

    def open(self, name, mode="rb"):
        """打开文件"""
        return self.storage.open(name)

    def exists(self, name):
        """是否存在"""
        return self.storage.exists(name)

    def mkdir(self, name):
        """占位"""
        pass


class RepoStorage(Storage):
    _storage = None

    @property
    def storage(self):
        from bkstorages.backends.bkrepo import BKRepoStorage

        if self._storage is None:
            self._storage = BKRepoStorage()
        return self._storage

    def save(self, name, content, max_length=None):
        """保存文件"""
        return self.storage.save(name, content, max_length)

    def open(self, name, mode="rb"):
        """打开文件"""
        return self.storage.open(name)

    def exists(self, name):
        """是否存在"""
        return self.storage.exists(name)

    def mkdir(self, name):
        """占位"""
        pass

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
from django.core.files import File


class CephStorage(Storage):
    """Ceth文件系统存储类"""

    _storage = None

    @property
    def storage(self):
        from bkstorages.backends.rgw import RGWBoto3Storage

        class CustomRGWBoto3Storage(RGWBoto3Storage):
            def save(self, name, content, max_length=None):
                """
                去除validate_file_name(name, allow_relative_path=True) 检查，保证content的可用性
                """
                if name is None:
                    name = content.name

                if not hasattr(content, "chunks"):
                    content = File(content, name)

                name = self.get_available_name(name, max_length=max_length)
                name = self._save(name, content)
                return name

        if self._storage is None:
            self._storage = CustomRGWBoto3Storage()

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

        class CustomBKRepoStorage(BKRepoStorage):
            def save(self, name, content, max_length=None):
                """
                去除validate_file_name(name, allow_relative_path=True) 检查，保证content的可用性
                """
                if name is None:
                    name = content.name

                if not hasattr(content, "chunks"):
                    content = File(content, name)

                name = self.get_available_name(name, max_length=max_length)
                name = self._save(name, content)
                return name

        if self._storage is None:
            self._storage = CustomBKRepoStorage()
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

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
import logging
import os

from django.core.files.storage import Storage, FileSystemStorage
from bkstorages.backends.bkrepo import BKRepoStorage
from bkstorages.backends.rgw import RGWBoto3Storage
from django.core.files import File

logger = logging.getLogger(__name__)


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


class CephStorage(Storage):
    """Ceth文件系统存储类"""

    _storage = None

    @property
    def storage(self):
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


class HybridStorage(Storage):
    """
    混合存储类
    """

    def __init__(self, read_priority=None, write_target='repo', fs_location=None):
        """
         初始化混合存储

         Args:
             write_target: 写入目标，可选 'fs'/'repo'/'both'，默认 'fs'
             fs_location: FileSystemStorage的存储路径，默认为根目录
         """
        # 读取优先级配置
        self.read_priority = read_priority or ['repo', 'fs']
        self._read_priority = None
        self._fs_location = fs_location or "/"
        self.storage = None

        # 写入目标配置
        self.write_target = write_target

        logger.info(f"HybridStorage initialized with write_target: {write_target}, "
                    f"fs_location: {self._fs_location}")

    @property
    def repo_storage(self):
        """获取制品库存储实例"""
        try:
            self.storage = RepoStorage()
            logger.info("RepoStorage initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RepoStorage: {e}")
            self.storage = None
        return self.storage

    @property
    def fs_storage(self):
        """获取文件系统存储实例"""
        self.storage = FileSystemStorage(location=self._fs_location)
        logger.info(f"FileSystemStorage initialized with location: {self._fs_location}")
        return self.storage

    def save(self, name, content, max_length=None):
        if self.write_target == 'both':
            # 同时保存到两个存储
            logger.debug(f"保存文件到 文件系统 和 制品库: {name}")
            # 先写入文件系统
            self.fs_storage.save(name, content, max_length)
            # 重置文件指针再写入制品库
            if hasattr(content, 'seek'):
                content.seek(0)  # 重置指针
            self.repo_storage.save(name, content, max_length)
            
        elif self.write_target == 'repo':
            # 仅写入制品库
            if self.repo_storage is not None:
                logger.debug(f"保存文件到 制品库: {name}")
                self.repo_storage.save(name, content, max_length)
        else:
            # 仅写入文件系统
            logger.debug(f"保存文件到 文件系统: {name}")
            self.fs_storage.save(name, content, max_length)

    def open(self, name, mode="rb"):
        """按照 read_priority 顺序尝试读取"""
        for storage_name in self.read_priority:
            if storage_name == 'repo':
                storage = self.repo_storage
            elif storage_name == 'fs':
                storage = self.fs_storage
            else:
                storage = None
            
            if storage is None:
                continue
            try:
                if storage.exists(name):
                    logger.debug(f"Opening file from {storage_name.upper()}: {name}")
                    return storage.open(name, mode)
            except Exception as e:
                logger.warning(
                    f"Failed to open file from {storage_name.upper()}: {name}, error: {e}")
                continue

        raise FileNotFoundError(f"File not found in any storage: {name}")

    def exists(self, name):
        """检查文件是否存在：按照 read_priority 顺序检查"""
        for storage_name in self.read_priority:
            if storage_name == 'repo':
                storage = self.repo_storage
            elif storage_name == 'fs':
                storage = self.fs_storage
            else:
                storage = None
            if storage is None:
                continue
            if storage.exists(name):
                return True

        return False

    def mkdir(self, name):
        """创建目录"""
        pass

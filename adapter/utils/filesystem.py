"""NFS attachment access restricted to the administrator-configured directory."""

import errno
import os
import stat
from contextlib import contextmanager

from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import File
from django.core.files.storage import FileSystemStorage


class SafeFileSystemStorage(FileSystemStorage):
    """Pin directory descriptors and refuse symlinks below the attachment root."""

    def __init__(self, location=None):
        super().__init__(location=location)
        self.attachment_root = location

    def _root(self):
        root = self.attachment_root
        if not isinstance(root, str) or not root or not os.path.isabs(root):
            raise SuspiciousFileOperation("Configure an absolute attachment directory")
        root = os.path.realpath(root)
        if root == os.path.dirname(root):
            raise SuspiciousFileOperation(
                "The filesystem root cannot store attachments"
            )
        return root

    def relative_name(self, name):
        root = self._root()
        if not isinstance(name, str) or not name:
            raise SuspiciousFileOperation("Invalid attachment path")
        if "\\" in name or any(ord(char) < 32 or ord(char) == 127 for char in name):
            raise SuspiciousFileOperation("Invalid attachment path")
        if any(part in (".", "..") for part in name.split("/")):
            raise SuspiciousFileOperation("Invalid attachment path")
        if os.path.isabs(name):
            # Old metadata may use the configured NFS mount symlink or its
            # canonical path. Only accept descendants of either explicit root.
            for prefix in (os.path.abspath(self.attachment_root), root):
                if os.path.commonpath([prefix, name]) == prefix:
                    name = os.path.relpath(name, prefix)
                    break
            else:
                raise SuspiciousFileOperation("Attachment outside configured directory")
        if any(part in ("", ".", "..") for part in name.split("/")):
            raise SuspiciousFileOperation("Invalid attachment path")
        return name

    def path(self, name):
        return os.path.join(self._root(), self.relative_name(name))

    @contextmanager
    def _parent(self, name):
        parts = self.relative_name(name).split("/")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        descriptor = os.open(self._root(), flags)
        try:
            for part in parts[:-1]:
                child = os.open(part, flags, dir_fd=descriptor)
                os.close(descriptor)
                descriptor = child
            yield descriptor, parts[-1]
        except OSError as error:
            if error.errno in (errno.ELOOP, errno.ENOTDIR):
                raise SuspiciousFileOperation(
                    "Attachment symlinks are not allowed"
                ) from error
            raise
        finally:
            os.close(descriptor)

    def _open(self, name, mode="rb"):
        if mode not in ("r", "rb"):
            raise ValueError("Use save() to write attachments")
        with self._parent(name) as (parent, leaf):
            descriptor = os.open(
                leaf, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent
            )
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            os.close(descriptor)
            raise SuspiciousFileOperation("Attachment must be a regular file")
        return File(os.fdopen(descriptor, mode), name=name)

    def exists(self, name):
        try:
            with self._open(name):
                return True
        except FileNotFoundError:
            return False

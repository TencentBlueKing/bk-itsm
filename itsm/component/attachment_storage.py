"""Resolve the configured attachment backend once per request."""

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from adapter.utils.filesystem import SafeFileSystemStorage
from itsm.iadmin.models import SystemSettings


def get_attachment_storage():
    storage = settings.STORE
    if isinstance(storage, FileSystemStorage):
        # Snapshot the current configuration for this request. Never use the
        # legacy FileSystemStorage(location="/") directly.
        root = SystemSettings.objects.get(key="SYS_FILE_PATH").value
        return SafeFileSystemStorage(location=root)
    return storage

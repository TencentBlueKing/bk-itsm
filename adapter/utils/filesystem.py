"""Compatibility alias for the restricted attachment filesystem storage.

The implementation lives in ``itsm.component.utils.filesystem`` so that it ships
with the SaaS package even when the ``adapter`` directory is replaced during
build/release. Kept only for callers importing the legacy path.
"""

from itsm.component.utils.filesystem import SafeFileSystemStorage  # noqa: F401

__all__ = ["SafeFileSystemStorage"]

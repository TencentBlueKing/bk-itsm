"""Attachment download regressions using real filesystem files and view bodies."""

import ast
import json
import logging
import os
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from wsgiref.util import FileWrapper

import pytest
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.http import HttpResponseForbidden, StreamingHttpResponse
from django.utils.encoding import escape_uri_path

from itsm.component.utils.filesystem import SafeFileSystemStorage
from itsm.attachment.services import authorize_download

ROOT = Path(__file__).resolve().parents[1]


def load_view(relative_path, function_name, store, root=None):
    tree = ast.parse((ROOT / relative_path).read_text())
    node = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == function_name
    )
    node.decorator_list = []
    model = Mock()
    model.objects.get.return_value.value = (
        root if root is not None else getattr(store, "attachment_root", "")
    )
    namespace = {
        "get_attachment_storage": lambda: store,
        "authorize_download": authorize_download,
        "TicketField": type("TicketField", (), {}),
        "SystemSettings": model,
        "SuspiciousFileOperation": SuspiciousFileOperation,
        "HttpResponseForbidden": HttpResponseForbidden,
        "StreamingHttpResponse": StreamingHttpResponse,
        "FileWrapper": FileWrapper,
        "escape_uri_path": escape_uri_path,
        "os": os,
        "time": time,
        "json": json,
        "store": store,
        "_": lambda value: value,
        "serializers": SimpleNamespace(ValidationError=ValueError),
        "Fail": lambda *args: SimpleNamespace(json=lambda: {"error": args}),
        "logger": logging.getLogger("app"),
    }
    exec(
        compile(ast.Module(body=[node], type_ignores=[]), str(relative_path), "exec"),
        namespace,
    )
    return namespace[function_name], namespace


@pytest.fixture
def nfs(tmp_path):
    root = tmp_path / "attachments"
    root.mkdir()
    return SafeFileSystemStorage(location=str(root))


def test_nfs_upload_relative_and_legacy_absolute_download(nfs):
    key = nfs.save("fields/file", ContentFile(b"attachment"))
    for name in (key, nfs.path(key)):
        with nfs.open(name) as uploaded:
            assert uploaded.read() == b"attachment"
    download, _ = load_view("workflow/views.py", "download_file", nfs)
    field = SimpleNamespace(
        type="FILE", choice={"key": {"path": nfs.path(key), "name": "test"}}
    )
    response = download(
        SimpleNamespace(get_object=lambda: field),
        SimpleNamespace(GET={"file_type": "template", "unique_key": "key"}),
    )
    assert b"".join(response.streaming_content) == b"attachment"
    response.close()


@pytest.mark.parametrize(
    "name",
    [
        "../secret",
        "fields/../../secret",
        "/etc/passwd",
        "fields/./file",
        "fields\\file",
        "",
        None,
    ],
)
def test_nfs_rejects_untrusted_paths(nfs, name):
    for operation in (nfs.open, nfs.exists):
        with pytest.raises(SuspiciousFileOperation):
            operation(name)


@pytest.mark.parametrize("root", [None, "", "/", "relative"])
def test_nfs_requires_explicit_safe_root(root):
    with pytest.raises(SuspiciousFileOperation):
        SafeFileSystemStorage(location=root).open("file")


@pytest.mark.parametrize("directory_link", [False, True])
def test_nfs_symlinks_cannot_read_outside(nfs, tmp_path, directory_link):
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = outside / "secret"
    secret.write_bytes(b"private")
    link = Path(nfs.attachment_root) / "link"
    link.symlink_to(outside if directory_link else secret)
    name = "link/secret" if directory_link else "link"
    for operation in (nfs.exists, nfs.open):
        with pytest.raises(SuspiciousFileOperation):
            operation(name)
    assert secret.read_bytes() == b"private"


def test_nfs_prefix_collision_rejected(nfs):
    with pytest.raises(SuspiciousFileOperation):
        nfs.open(nfs.attachment_root + "-other/secret")


def test_nfs_root_mount_symlink_supported(nfs, tmp_path):
    nfs.save("file", ContentFile(b"content"))
    mount = tmp_path / "mount"
    mount.symlink_to(nfs.attachment_root)
    mounted = SafeFileSystemStorage(location=str(mount))
    with mounted.open(str(mount / "file")) as uploaded:
        assert uploaded.read() == b"content"


def test_nfs_symlink_swap_between_exists_and_open_is_blocked(nfs, tmp_path):
    nfs.save("file", ContentFile(b"attachment"))
    assert nfs.exists("file")
    secret = tmp_path / "secret"
    secret.write_bytes(b"private")
    target = Path(nfs.path("file"))
    target.unlink()
    target.symlink_to(secret)
    with pytest.raises(SuspiciousFileOperation):
        nfs.open("file")


def test_nfs_fifo_is_rejected_without_blocking(nfs):
    os.mkfifo(nfs.path("pipe"))
    with pytest.raises(SuspiciousFileOperation):
        nfs.open("pipe")


@pytest.mark.parametrize("filesystem", [False, True])
def test_resolver_snapshots_nfs_root_only_for_filesystem(nfs, filesystem):
    resolver, namespace = load_view(
        "component/attachment_storage.py", "get_attachment_storage", None
    )
    model = Mock()
    model.objects.get.return_value.value = nfs.attachment_root
    configured = nfs if filesystem else Mock()
    namespace.update(
        settings=SimpleNamespace(STORE=configured),
        FileSystemStorage=SafeFileSystemStorage.__bases__[0],
        SafeFileSystemStorage=SafeFileSystemStorage,
        SystemSettings=model,
    )
    resolved = resolver()
    if filesystem:
        assert isinstance(resolved, SafeFileSystemStorage)
        assert resolved.attachment_root == nfs.attachment_root
        model.objects.get.assert_called_once_with(key="SYS_FILE_PATH")
    else:
        assert resolved is configured
        model.objects.get.assert_not_called()


@pytest.mark.parametrize("path", ["../secret", "/etc/passwd", "fields/../../secret"])
def test_workflow_rejects_paths_outside_nfs(nfs, path):
    download, _ = load_view("workflow/views.py", "download_file", nfs)
    field = SimpleNamespace(type="FILE", choice={"key": {"path": path, "name": "test"}})
    with pytest.raises(ValueError, match="非法"):
        download(
            SimpleNamespace(get_object=lambda: field),
            SimpleNamespace(GET={"file_type": "template", "unique_key": "key"}),
        )


@pytest.mark.parametrize("root", ["", "attachments"])
def test_object_storage_keeps_original_prefix_and_key(root):
    store = Mock()
    store.open.return_value = ContentFile(b"attachment")
    download, _ = load_view("workflow/views.py", "download_file", store, root=root)
    field = SimpleNamespace(
        type="FILE", choice={"key": {"path": "fields/abc", "name": "test"}}
    )
    response = download(
        SimpleNamespace(get_object=lambda: field),
        SimpleNamespace(GET={"file_type": "template", "unique_key": "key"}),
    )
    assert b"".join(response.streaming_content) == b"attachment"
    response.close()
    target = os.path.join(root, "fields/abc")
    store.exists.assert_called_once_with(target)
    store.open.assert_called_once_with(target, "rb")


@pytest.mark.parametrize("state_id", ["2", ""])
def test_misc_reads_checked_file_and_keeps_optional_state(nfs, state_id):
    name = "1_{}/key/test".format(state_id)
    nfs.save(name, ContentFile(b"attachment"))
    download, namespace = load_view("misc/views.py", "download", nfs)
    compile_path, _ = load_view("misc/views.py", "compile_file_path", nfs)
    namespace.update(
        compile_file_path=compile_path,
        _check_resource_access=lambda request: (True, ""),
    )
    query = {"ticket_id": "1", "key": "key", "file_name": "test"}
    if state_id:
        query["state_id"] = state_id
    response = download(SimpleNamespace(GET=query))
    assert b"".join(response.streaming_content) == b"attachment"
    response.close()


@pytest.mark.parametrize("parameter", ["ticket_id", "state_id", "key", "file_name"])
def test_misc_rejects_directory_escape(nfs, parameter):
    download, namespace = load_view("misc/views.py", "download", nfs)
    compile_path, _ = load_view("misc/views.py", "compile_file_path", nfs)
    namespace.update(
        compile_file_path=compile_path,
        _check_resource_access=lambda request: (True, ""),
    )
    query = {"ticket_id": "1", "state_id": "2", "key": "key", "file_name": "test"}
    query[parameter] = "../../../../outside"
    assert download(SimpleNamespace(GET=query)).status_code == 403


def test_misc_denied_request_never_contacts_storage():
    store = Mock()
    download, namespace = load_view("misc/views.py", "download", store)
    namespace["_check_resource_access"] = lambda request: (False, "denied")
    assert download(SimpleNamespace(GET={})).status_code == 403
    assert not store.mock_calls


def test_missing_nfs_file_returns_false(nfs):
    assert nfs.exists("missing/file") is False


def test_nfs_read_adapter_rejects_write_mode(nfs):
    with pytest.raises(ValueError):
        nfs.open("file", "wb")


@pytest.mark.parametrize(
    "name", ["fields/a\x00b", "fields//file", "fields/file/", "fields/a\nb"]
)
def test_nfs_rejects_ambiguous_names(nfs, name):
    with pytest.raises(SuspiciousFileOperation):
        nfs.open(name)


def test_nfs_directory_swap_between_exists_and_open_is_blocked(nfs, tmp_path):
    nfs.save("fields/file", ContentFile(b"attachment"))
    assert nfs.exists("fields/file")
    original = Path(nfs.path("fields"))
    original.rename(original.with_name("previous"))
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "file").write_bytes(b"private")
    original.symlink_to(outside)
    with pytest.raises(SuspiciousFileOperation):
        nfs.open("fields/file")


def test_misc_storage_error_degrades_to_missing_file():
    store = Mock()
    store.exists.side_effect = PermissionError(13, "permission denied")
    download, namespace = load_view("misc/views.py", "download", store, root="/tmp/x")
    compile_path, _ = load_view("misc/views.py", "compile_file_path", store, root="/tmp/x")
    namespace.update(
        compile_file_path=compile_path,
        _check_resource_access=lambda request: (True, ""),
    )
    response = download(
        SimpleNamespace(GET={"ticket_id": "1", "key": "key", "file_name": "test"})
    )
    assert response["error"][1] == "NO_SUCH_FILE"


def test_workflow_storage_error_degrades_to_missing_file():
    store = Mock()
    store.exists.side_effect = PermissionError(13, "permission denied")
    download, _ = load_view(
        "workflow/views.py", "download_file", store, root="/tmp/x"
    )
    field = SimpleNamespace(
        type="FILE", choice={"key": {"path": "fields/abc", "name": "test"}}
    )
    with pytest.raises(ValueError, match="不存在"):
        download(
            SimpleNamespace(get_object=lambda: field),
            SimpleNamespace(GET={"file_type": "template", "unique_key": "key"}),
        )

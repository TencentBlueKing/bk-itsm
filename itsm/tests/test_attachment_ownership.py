"""Database-backed tests of registration, atomic binding and download checks."""

import ast
import copy
import json
import logging
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.db import transaction
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from itsm.component.utils.filesystem import SafeFileSystemStorage

from itsm.attachment.models import Attachment, AttachmentRef
from itsm.attachment.services import (
    FILE_PREFIX,
    attachment_ids,
    authorize_download,
    bind_attachments,
    bind_ticket_fields,
)
from itsm.tests.test_attachment_storage import load_view


@pytest.fixture(scope="module", autouse=True)
def schema():
    call_command("migrate", "attachment", verbosity=0)


@pytest.fixture(autouse=True)
def clean_registry():
    Attachment.objects.all().delete()
    yield
    Attachment.objects.all().delete()


def upload(identity="a" * 32, uploader="alice", ticket_id=None):
    return Attachment.objects.create(
        id=identity,
        path="fields/" + FILE_PREFIX + identity,
        uploader=uploader,
        ticket_id=ticket_id,
    )


def value(record):
    return {record.pk: {"name": "file.txt", "path": record.path}}


def test_pending_upload_can_only_be_bound_by_its_uploader():
    record = upload()
    with pytest.raises(PermissionDenied):
        bind_attachments(1, [value(record)], "bob")
    record.refresh_from_db()
    assert record.ticket_id is None
    bind_attachments(1, [json.dumps(value(record))], "alice")
    record.refresh_from_db()
    assert record.ticket_id == 1


def test_binding_is_idempotent_for_same_ticket_but_never_reassigned():
    record = upload()
    bind_attachments(1, [value(record)], "alice")
    bind_attachments(1, [value(record)], "bob")
    with pytest.raises(PermissionDenied):
        bind_attachments(2, [value(record)], "bob")
    record.refresh_from_db()
    assert record.ticket_id == 1


def test_uploader_keeps_recreate_ticket_flow_with_own_upload():
    """重新提单：本人上传的附件可以带到新单，原归属不变。"""
    record = upload()
    bind_attachments(1, [value(record)], "alice")
    bind_attachments(2, [value(record)], "alice")
    record.refresh_from_db()
    assert record.ticket_id == 1
    authorize_download(record.path, ticket_id=1)
    authorize_download(record.path, ticket_id=2)
    with pytest.raises(PermissionDenied):
        authorize_download(record.path, ticket_id=3)
    assert AttachmentRef.objects.filter(
        attachment=record, ticket_id=2
    ).exists()


def test_foreign_upload_cannot_be_carried_into_another_ticket():
    record = upload(ticket_id=1)
    with pytest.raises(PermissionDenied):
        bind_attachments(2, [value(record)], "bob")
    assert not AttachmentRef.objects.exists()


def test_multiple_claims_roll_back_together_on_failure():
    own = upload()
    foreign = upload("b" * 32, "bob")
    with pytest.raises(PermissionDenied):
        bind_attachments(1, [value(own), value(foreign)], "alice")
    own.refresh_from_db()
    assert own.ticket_id is None


def test_outer_field_save_failure_rolls_back_binding():
    record = upload()
    with pytest.raises(RuntimeError):
        with transaction.atomic():
            bind_attachments(1, [value(record)], "alice")
            raise RuntimeError("field save failed")
    record.refresh_from_db()
    assert record.ticket_id is None


@pytest.mark.parametrize("ticket_id", [None, 2, "2"])
def test_bound_attachment_cannot_be_downloaded_by_another_context(ticket_id):
    record = upload(ticket_id=1)
    with pytest.raises(PermissionDenied):
        authorize_download(record.path, ticket_id=ticket_id, allow_unbound=True)


def test_same_ticket_authorization_accepts_integer_and_query_string_id():
    record = upload(ticket_id=1)
    for ticket_id in (1, "1"):
        authorize_download(record.path, ticket_id=ticket_id)


def test_unbound_templates_remain_available_but_ticket_values_require_binding():
    record = upload()
    authorize_download(record.path)
    authorize_download(record.path, ticket_id=1, allow_unbound=True)
    with pytest.raises(PermissionDenied):
        authorize_download(record.path, ticket_id=1)


@pytest.mark.parametrize(
    "alias",
    [
        "fields/{name}",
        "/root/fields/{name}",
        "fields/%5f%5fitsm_attachment_{id}",
        "fields/%255f%255fitsm_attachment_{id}",
        "fields/{name}?download=1",
        "fields/own?other={name}",
    ],
)
def test_path_alias_cannot_fall_back_to_legacy_mode(alias):
    record = upload(ticket_id=1)
    path = alias.format(name=FILE_PREFIX + record.pk, id=record.pk)
    with pytest.raises(PermissionDenied):
        authorize_download(path, ticket_id=2)


def test_missing_new_registry_entry_is_rejected():
    path = "fields/" + FILE_PREFIX + "c" * 32
    with pytest.raises(PermissionDenied):
        authorize_download(path)
    with pytest.raises(PermissionDenied):
        bind_attachments(1, [{"x": {"path": path}}], "alice")


def test_legacy_references_are_not_registered_or_rewritten():
    path = "fields/" + "d" * 32
    authorize_download(path, ticket_id=1)
    bind_attachments(1, [{"x": {"path": path}}], "alice")
    assert not Attachment.objects.exists()


@pytest.mark.parametrize(
    "bad", [None, 123, "fields/__itsm_attachment_broken", "%2525252525252525255f"]
)
def test_malformed_identifiers_are_rejected(bad):
    with pytest.raises(PermissionDenied):
        attachment_ids(bad)


def test_workflow_template_entry_cannot_bypass_ticket_ownership():
    record = upload(ticket_id=1)
    store = Mock()
    download, _ = load_view("workflow/views.py", "download_file", store, root="")
    field = SimpleNamespace(type="FILE", choice=value(record))
    with pytest.raises(PermissionDenied):
        download(
            SimpleNamespace(get_object=lambda: field),
            SimpleNamespace(GET={"unique_key": record.pk, "file_type": "template"}),
        )
    assert not store.mock_calls


def test_ticket_download_checks_owner_before_storage():
    record = upload(ticket_id=1)
    store = Mock()
    download, namespace = load_view(
        "workflow/views.py", "download_file", store, root=""
    )
    field = namespace["TicketField"]()
    field.type, field.ticket_id, field.value = "FILE", 2, json.dumps(value(record))
    with pytest.raises(PermissionDenied):
        download(
            SimpleNamespace(get_object=lambda: field),
            SimpleNamespace(GET={"unique_key": record.pk, "file_type": "ticket"}),
        )
    assert not store.mock_calls
    field.ticket_id = 1
    store.open.return_value = ContentFile(b"attachment")
    response = download(
        SimpleNamespace(get_object=lambda: field),
        SimpleNamespace(GET={"unique_key": record.pk, "file_type": "ticket"}),
    )
    assert b"".join(response.streaming_content) == b"attachment"
    response.close()


def upload_view(storage, root):
    upload_func, namespace = load_view("misc/views.py", "upload", storage, root=root)
    namespace.update(
        FileSystemStorage=FileSystemStorage,
        Attachment=Attachment,
        FILE_PREFIX=FILE_PREFIX,
        uuid=uuid,
        Success=lambda data, **kwargs: SimpleNamespace(json=lambda: data),
    )
    files = Mock()
    files.getlist.return_value = [ContentFile(b"attachment", name="original.txt")]
    request = SimpleNamespace(
        user=SimpleNamespace(is_authenticated=True, username="alice"),
        FILES=files,
        path="/upload/",
    )
    return upload_func, request


def test_upload_registers_saved_nfs_file_and_authenticated_uploader(tmp_path):
    storage = SafeFileSystemStorage(location=str(tmp_path))
    upload_func, request = upload_view(storage, str(tmp_path))
    response = upload_func(request)
    entry = next(iter(response["succeed_files"].values()))
    record = Attachment.objects.get()
    assert record.uploader == "alice" and record.ticket_id is None
    assert record.path == entry["path"]
    assert record.pk in entry["path"]
    with storage.open(entry["path"]) as saved:
        assert saved.read() == b"attachment"
    bind_attachments(1, [response["succeed_files"]], "alice")
    authorize_download(entry["path"], ticket_id=1)


def test_object_storage_upload_keeps_backend_and_prefix():
    storage = Mock()
    upload_func, request = upload_view(storage, "prefix")
    result = upload_func(request)
    record = Attachment.objects.get()
    assert record.path.startswith("prefix/fields/" + FILE_PREFIX)
    assert next(iter(result["succeed_files"].values()))["path"] == record.path
    assert storage.save.call_args.args[0] == record.path


def test_failed_upload_does_not_register_attachment():
    storage = Mock()
    storage.save.side_effect = RuntimeError("storage unavailable")
    upload_func, request = upload_view(storage, "prefix")
    with pytest.raises(RuntimeError):
        upload_func(request)
    assert not Attachment.objects.exists()


def load_method(path, name, namespace):
    source = (Path(__file__).resolve().parents[1] / path).read_text()
    node = next(
        n
        for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.FunctionDef) and n.name == name
    )
    # Preserve @transaction.atomic on production field-write methods.
    exec(compile(ast.Module(body=[node], type_ignores=[]), path, "exec"), namespace)
    return namespace[name]


def load_view_method(path, name, namespace):
    """Load a DRF action without evaluating its route/auth decorators."""
    source = (Path(__file__).resolve().parents[1] / path).read_text()
    node = next(
        n
        for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.FunctionDef) and n.name == name
    )
    node.decorator_list = []
    exec(compile(ast.Module(body=[node], type_ignores=[]), path, "exec"), namespace)
    return namespace[name]


def isolated_safe_after_commit():
    marks = []
    safe = load_method(
        "ticket/utils.py",
        "safe_after_commit",
        {
            "logger": logging.getLogger(__name__),
            "Cache": lambda: SimpleNamespace(hset=lambda *args: marks.append(args)),
            "time": time,
            "START_ERROR_CACHE_KEY": "ticket_start_error",
        },
    )
    return safe, marks


def test_actual_field_update_rolls_back_binding_when_bulk_save_fails():
    record = upload()
    field = SimpleNamespace(type="FILE", key="attachment", value=None)
    ticket = SimpleNamespace(pk=1, fields=Mock())
    ticket.fields.filter.return_value = [field]
    namespace = {
        "transaction": transaction,
        "bind_attachments": bind_attachments,
        "FIELD_PRIORITY": "priority",
        "FIELD_IGNORE_ESCAPE": ["FILE"],
        "datetime": Mock(now=lambda: None),
        "json": json,
        "bulk_update": Mock(side_effect=RuntimeError("database write failed")),
    }
    update = load_method("ticket/models/ticket.py", "fill_state_fields", namespace)
    with pytest.raises(RuntimeError):
        update(
            ticket, [{"key": "attachment", "value": value(record)}], operator="alice"
        )
    record.refresh_from_db()
    assert record.ticket_id is None
    namespace["bulk_update"].side_effect = None
    update(ticket, [{"key": "attachment", "value": value(record)}], operator="alice")
    record.refresh_from_db()
    assert record.ticket_id == 1


def sign_schedule(record, fail_save=False):
    ticket = Mock(pk=1)
    ticket.fields.filter.return_value.values_list.return_value = ["attachment"]
    if fail_save:
        ticket.update_ticket_fields.side_effect = RuntimeError("field write failed")
    service = Mock()
    service.get_key_value.return_value = {}
    service.task_is_finished.return_value = False
    status = SimpleNamespace(state_id=1)
    namespace = {
        "transaction": transaction,
        "bind_ticket_fields": bind_ticket_fields,
        "Ticket": SimpleNamespace(objects=SimpleNamespace(get=lambda **kwargs: ticket)),
        "Status": SimpleNamespace(objects=SimpleNamespace(get=lambda **kwargs: status)),
        "logger": logging.getLogger(__name__),
    }
    service.save_sign_fields = load_method(
        "pipeline_plugins/components/collections/itsm_sign.py",
        "save_sign_fields",
        namespace,
    )
    schedule = load_method(
        "pipeline_plugins/components/collections/itsm_sign.py", "schedule", namespace
    )
    callback = {
        "ticket_id": 1,
        "state_id": 1,
        "operator": "alice",
        "source": "WEB",
        "fields": [{"key": "attachment", "value": value(record)}],
    }
    return schedule, service, ticket, callback


def test_sign_rejects_foreign_attachment_before_state_writes_or_finish():
    record = upload(uploader="bob")
    schedule, service, ticket, callback = sign_schedule(record)
    with pytest.raises(PermissionDenied):
        schedule(
            service,
            SimpleNamespace(inputs={}, outputs={}),
            SimpleNamespace(inputs={}),
            callback,
        )
    ticket.do_in_sign_state.assert_not_called()
    ticket.update_ticket_fields.assert_not_called()
    service.final_execute.assert_not_called()


def test_sign_write_failure_rolls_back_binding():
    record = upload()
    schedule, service, ticket, callback = sign_schedule(record, fail_save=True)
    with pytest.raises(RuntimeError):
        schedule(
            service,
            SimpleNamespace(inputs={}, outputs={}),
            SimpleNamespace(inputs={}),
            callback,
        )
    record.refresh_from_db()
    assert record.ticket_id is None


def test_misc_entry_cannot_bypass_ticket_ownership():
    record = upload(ticket_id=1)
    store = Mock()
    download, namespace = load_view(
        "misc/views.py", "download", store, root="/attachments"
    )
    compile_path, _ = load_view(
        "misc/views.py", "compile_file_path", store, root="/attachments"
    )
    namespace.update(
        compile_file_path=compile_path,
        _check_resource_access=lambda request: (True, ""),
    )
    with pytest.raises(PermissionDenied):
        download(
            SimpleNamespace(
                GET={
                    "ticket_id": "2",
                    "state_id": "3",
                    "key": "key",
                    "file_name": FILE_PREFIX + record.pk,
                }
            )
        )
    assert not store.mock_calls


def test_workflow_version_entry_cannot_bypass_ticket_ownership():
    record = upload(ticket_id=1)
    store = Mock()
    download, namespace = load_view(
        "workflow/views.py", "download_file", store, root=""
    )
    # A snapshot is untrusted JSON, even if it includes a ticket_id attribute.
    field = SimpleNamespace(type="FILE", choice=value(record), ticket_id=1)
    version = SimpleNamespace(get_field=lambda pk: field)
    namespace.update(
        WorkflowVersion=SimpleNamespace(
            objects=SimpleNamespace(get=lambda **kwargs: version),
            DoesNotExist=LookupError,
        ),
        bunchify=lambda data: data,
    )
    permission = Mock()
    with pytest.raises(PermissionDenied):
        download(
            SimpleNamespace(_check_version_download_permission=permission),
            SimpleNamespace(
                GET={"unique_key": record.pk, "file_type": "version", "flow_id": "1"}
            ),
            pk="1",
        )
    permission.assert_called_once()
    assert not store.mock_calls


def test_concurrent_claims_keep_a_single_owner(tmp_path):
    env = dict(
        os.environ,
        ITSM_ATTACHMENT_TEST_DB=str(tmp_path / "claims.sqlite3"),
        CLAIM_GATE=str(tmp_path / "start"),
    )
    setup = """
import django
django.setup()
from django.core.management import call_command
from itsm.attachment.models import Attachment
call_command('migrate', 'attachment', verbosity=0)
Attachment.objects.create(id='a'*32, path='fields/__itsm_attachment_'+'a'*32, uploader='alice')
"""
    subprocess.run(
        [sys.executable, "-c", setup], env=env, check=True, capture_output=True
    )
    worker = """
import os
import sys
import time
from pathlib import Path
import django
django.setup()
from django.core.exceptions import PermissionDenied
from django.db import OperationalError
from itsm.attachment.services import bind_attachments
identity = int(sys.argv[1])
gate = Path(os.environ['CLAIM_GATE'])
gate.with_name('ready'+str(identity)).touch()
for attempt in range(500):
    if gate.exists():
        break
    time.sleep(0.01)
else:
    raise RuntimeError('start gate timed out')
try:
    bind_attachments(identity, [{'file': {'path': 'fields/__itsm_attachment_'+'a'*32}}], 'alice')
    print('claimed')
except (PermissionDenied, OperationalError):
    # SQLite may report write contention; neither outcome may change the owner.
    print('rejected')
"""
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", worker, str(ticket)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for ticket in (1, 2)
    ]
    try:
        for attempt in range(500):
            if all((tmp_path / ("ready" + str(ticket))).exists() for ticket in (1, 2)):
                break
            time.sleep(0.01)
        else:
            pytest.fail("workers did not become ready")
        (tmp_path / "start").touch()
        results = [process.communicate(timeout=10) for process in processes]
        assert all(process.returncode == 0 for process in processes), results
        outputs = [stdout.strip() for stdout, stderr in results]
        assert "claimed" in outputs
        # 同一上传人并发复用同一文件时允许 "claimed + claimed"，但归属只能有一个，
        # 另一张单必须通过共享关系（AttachmentRef）拿到，原归属不能被改写。
        state = json.loads(
            subprocess.check_output(
                [
                    sys.executable,
                    "-c",
                    "import json, django; django.setup(); "
                    "from itsm.attachment.models import Attachment, AttachmentRef; "
                    "print(json.dumps([Attachment.objects.get().ticket_id, "
                    "sorted(AttachmentRef.objects.values_list('ticket_id', flat=True))]))",
                ],
                env=env,
                text=True,
            )
        )
        owner, refs = state
        assert owner in (1, 2)
        claimed = [index for index, output in enumerate(outputs, 1) if output == "claimed"]
        if len(claimed) == 1:
            assert owner == claimed[0]
            assert refs == []
        else:
            assert claimed == [1, 2]
            assert refs == [2 if owner == 1 else 1]
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.wait()


@pytest.mark.parametrize("rollback", [False, True])
def test_create_binds_before_success_and_defers_side_effects(rollback):
    record = upload()
    ticket = Mock(id=1, sn="ticket")
    ticket.prepare_initial_fields.side_effect = (
        lambda fields, operator: bind_attachments(1, [value(record)], operator)
    )
    serializer = Mock(validated_data={"service_id": 1, "creator": "alice"})
    serializer.save.return_value = ticket
    start = Mock()

    def after_commit(ticket, action, callback):
        try:
            callback()
            return True
        except Exception:
            return False

    create = load_method(
        "ticket/views/ticket.py",
        "create",
        {
            "transaction": transaction,
            "Service": Mock(),
            "safe_after_commit": after_commit,
            "start_ticket": start,
            "Response": lambda data, status: (data, status),
        },
    )
    request = SimpleNamespace(
        user=SimpleNamespace(username="alice"), data={"fields": []}
    )
    with transaction.atomic():
        result = create(Mock(get_serializer=lambda **kwargs: serializer), request)
        assert result[1] == 201
        assert Attachment.objects.get(pk=record.pk).ticket_id == 1
        start.assert_not_called()
        if rollback:
            transaction.set_rollback(True)
    record.refresh_from_db()
    if rollback:
        assert record.ticket_id is None
        start.assert_not_called()
    else:
        assert record.ticket_id == 1
        start.assert_called_once()


def test_after_commit_failure_is_recorded_without_raising():
    safe, marks = isolated_safe_after_commit()
    ticket = SimpleNamespace(id=1, sn="SN-1")

    def boom():
        raise RuntimeError("flow init failed")

    assert safe(ticket, "start_ticket", boom) is False
    assert marks[0][0] == "ticket_start_error"
    assert marks[0][1] == "SN-1:start_ticket"
    assert safe(ticket, "start_ticket", lambda: None) is True


def test_start_ticket_initializes_before_dispatch():
    calls = []
    ticket = Mock()
    ticket.do_after_create.side_effect = lambda *a, **k: calls.append("init")
    pipeline = Mock()
    pipeline.apply_async.side_effect = lambda *a, **k: calls.append("dispatch")
    start = load_method("ticket/tasks.py", "start_ticket", {"start_pipeline": pipeline})
    start(ticket, [], None, "alice")
    assert calls == ["init", "dispatch"]

    # 初始化失败时绝不投递 pipeline，避免流程跑在半初始化的单据上
    calls.clear()
    ticket.do_after_create.side_effect = RuntimeError("init failed")
    with pytest.raises(RuntimeError):
        start(ticket, [], None, "alice")
    assert calls == []


def test_openapi_create_ticket_keeps_response_when_dispatch_fails():
    """投递失败仍返回原响应体（不含 started），不抛 CreateTicketError。"""
    safe, marks = isolated_safe_after_commit()
    record = upload()
    ticket = Mock(id=1, sn="SN-API", pc_ticket_url="url")
    ticket.prepare_initial_fields.side_effect = (
        lambda fields, operator: bind_attachments(1, [value(record)], operator)
    )
    serializer = Mock()
    serializer.save.return_value = ticket
    task = Mock()
    task.apply_async.side_effect = RuntimeError("broker down")
    create = load_view_method(
        "openapi/ticket/views.py",
        "create_ticket",
        {
            "copy": copy,
            "logger": logging.getLogger(__name__),
            "transaction": transaction,
            "safe_after_commit": safe,
            "Response": lambda data, status=None: (data, status),
            "CreateTicketError": RuntimeError,
            "TicketCreateSerializer": lambda **kwargs: serializer,
            "DynamicFieldSerializer": Mock(),
            "ServiceCatalog": Mock(),
            "Service": Mock(),
            "INVISIBLE": "",
            "openapi_start_ticket": task,
        },
    )
    request = SimpleNamespace(
        user=SimpleNamespace(username="alice"), data={"fields": []}
    )
    with transaction.atomic():
        result = create(Mock(), request)
        assert set(result[0]) == {"sn", "id", "ticket_url"}
        assert Attachment.objects.get(pk=record.pk).ticket_id == 1
    assert task.apply_async.called
    assert marks[0][1] == "SN-API:openapi_start_ticket"


def test_openapi_create_ticket_with_version_keeps_response_when_start_fails():
    """两个后置步骤合并为一个回调，失败只记录，响应体不变。"""
    safe, marks = isolated_safe_after_commit()
    record = upload()
    ticket = Mock(id=1, sn="SN-BASE", pc_ticket_url="url")
    ticket.prepare_initial_fields.side_effect = (
        lambda fields, operator: bind_attachments(1, [value(record)], operator)
    )
    serializer = Mock()
    serializer.save.return_value = ticket
    start = Mock(side_effect=RuntimeError("flow init failed"))
    create = load_view_method(
        "openapi/base_service/views/ticket.py",
        "create_ticket_with_version",
        {
            "copy": copy,
            "logger": logging.getLogger(__name__),
            "transaction": transaction,
            "safe_after_commit": safe,
            "start_ticket": start,
            "Response": lambda data, status=None: (data, status),
            "CreateTicketError": RuntimeError,
            "TicketCreateSerializer": lambda **kwargs: serializer,
        },
    )
    request = SimpleNamespace(
        user=SimpleNamespace(username="alice"), data={"fields": []}
    )
    with transaction.atomic():
        result = create(Mock(), request)
        assert set(result[0]) == {"sn", "id", "ticket_url"}
        assert Attachment.objects.get(pk=record.pk).ticket_id == 1
        start.assert_not_called()
    start.assert_called_once()
    assert marks[0][1] == "SN-BASE:start_ticket"


@pytest.mark.parametrize("component", ["modify_field", "modify_first_state_field"])
def test_automated_field_writes_reject_pending_upload_before_update(component):
    record = upload()
    ticket = Mock(pk=1)
    fields = ticket.fields.filter.return_value
    fields.values_list.return_value = ["attachment"]
    execute = load_method(
        "trigger/action/components/" + component + ".py",
        "_execute",
        {
            "transaction": transaction,
            "bind_ticket_fields": bind_ticket_fields,
            "Ticket": SimpleNamespace(
                objects=SimpleNamespace(get=lambda **kwargs: ticket),
                DoesNotExist=LookupError,
            ),
        },
    )
    service = Mock()
    service.data.get_one_of_inputs.return_value = "attachment"
    service.data.inputs = {"field_value": value(record)}
    with pytest.raises(PermissionDenied):
        execute(service)
    fields.update.assert_not_called()
    record.refresh_from_db()
    assert record.ticket_id is None
    bind_attachments(1, [value(record)], "alice")
    assert execute(service) is True
    fields.update.assert_called_once()


def initialize_fields(defaults, submitted, operator="alice", choices=None):
    """Run production initialization; only the ticket-field ORM is isolated."""
    persisted = []

    class Fields:
        def filter(self, **filters):
            return [
                field
                for field in persisted
                if ("key__in" not in filters or field.key in filters["key__in"])
                and ("type" not in filters or field.type == filters["type"])
            ]

    class Field:
        objects = SimpleNamespace(bulk_create=lambda fields: persisted.extend(fields))

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.meta = {}

        @property
        def value(self):
            return getattr(self, "_value", "")

        @value.setter
        def value(self, value):
            self._value = value

    namespace = {
        "transaction": transaction,
        "copy": copy,
        "TicketField": Field,
        "TicketStatus": SimpleNamespace(
            objects=SimpleNamespace(get_status_choice=lambda value: [])
        ),
        "FIELD_STATUS": "status",
        "FIELD_PRIORITY": "priority",
        "bind_attachments": bind_attachments,
        "bulk_update": Mock(),
        "FIELD_IGNORE_ESCAPE": ["FILE"],
        "datetime": Mock(now=lambda: None),
    }
    ticket = SimpleNamespace(
        pk=1,
        service_type="request",
        fields=Fields(),
        flow=SimpleNamespace(
            table={"fields": []},
            fields={
                key: {
                    "id": index,
                    "key": key,
                    "type": "FILE",
                    "default": default,
                    "choice": choices or {},
                }
                for index, (key, default) in enumerate(defaults.items(), 1)
            },
        ),
    )
    prepare = load_method("ticket/models/ticket.py", "prepare_all_fields", namespace)
    fill = load_method("ticket/models/ticket.py", "fill_state_fields", namespace)
    initialize = load_method(
        "ticket/models/ticket.py", "prepare_initial_fields", namespace
    )
    ticket.prepare_all_fields = lambda: prepare(ticket)
    ticket.fill_state_fields = lambda fields, operator: fill(ticket, fields, operator)
    initialize(ticket, submitted, operator=operator)
    return persisted


def test_omitted_file_default_is_bound_and_downloadable():
    record = upload()
    fields = initialize_fields({"attachment": json.dumps(value(record))}, [])
    assert json.loads(fields[0].value) == value(record)
    record.refresh_from_db()
    assert record.ticket_id == 1
    authorize_download(record.path, ticket_id=1)
    with pytest.raises(PermissionDenied):
        authorize_download(record.path, ticket_id=2)


@pytest.mark.parametrize("owner", ["foreign_uploader", "other_ticket", "missing"])
def test_invalid_file_default_rejects_and_rolls_back_submitted_binding(owner):
    own = upload()
    foreign = upload(
        "b" * 32,
        uploader="bob",
        ticket_id=2 if owner == "other_ticket" else None,
    )
    foreign_value = value(foreign)
    if owner == "missing":
        foreign.delete()
    with pytest.raises(PermissionDenied):
        initialize_fields(
            {"default_file": json.dumps(foreign_value), "submitted_file": ""},
            [{"key": "submitted_file", "value": json.dumps(value(own))}],
        )
    own.refresh_from_db()
    assert own.ticket_id is None


@pytest.mark.parametrize("replacement", ["", "new"])
def test_overridden_default_is_not_bound(replacement):
    default = upload(uploader="bob")
    submitted = upload("b" * 32)
    new_value = json.dumps(value(submitted)) if replacement else ""
    initialize_fields(
        {"attachment": json.dumps(value(default))},
        [{"key": "attachment", "value": new_value}],
    )
    default.refresh_from_db()
    submitted.refresh_from_db()
    assert default.ticket_id is None
    assert submitted.ticket_id == (1 if replacement else None)


def test_historical_default_and_template_choice_remain_unbound():
    template = upload(uploader="template_owner")
    legacy = {"old": {"path": "fields/old-file", "name": "legacy.txt"}}
    fields = initialize_fields(
        {"attachment": json.dumps(legacy)}, [], choices=value(template)
    )
    assert json.loads(fields[0].value) == legacy
    template.refresh_from_db()
    assert template.ticket_id is None
    assert Attachment.objects.count() == 1
    authorize_download("fields/old-file", ticket_id=1)
    authorize_download(template.path, allow_unbound=True)

"""Bind registered uploads once and enforce ownership at every download entry."""

import json
import re
from urllib.parse import unquote

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.translation import gettext as _

from itsm.attachment.models import Attachment

FILE_PREFIX = "__itsm_attachment_"
ATTACHMENT_PATTERN = re.compile(FILE_PREFIX + r"([0-9a-f]{32})", re.IGNORECASE)


def attachment_ids(path):
    """Recognize identifiers even in encoded paths/query suffixes before I/O.

    New filenames carry the registry ID. Unknown IDs fail closed, so deleting
    metadata or spelling an object key differently cannot trigger legacy mode.
    Multiple IDs must all be authorized, including IDs in URL-like input.
    """
    if not isinstance(path, str):
        raise PermissionDenied(_("附件路径无效"))
    for depth in range(8):
        decoded = unquote(path)
        if decoded == path:
            break
        path = decoded
    else:
        raise PermissionDenied(_("附件路径编码无效"))
    ids = {value.lower() for value in ATTACHMENT_PATTERN.findall(path)}
    if FILE_PREFIX in path.lower() and not ids:
        raise PermissionDenied(_("附件标识无效"))
    return ids


def file_ids(value):
    if not value:
        return set()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            raise PermissionDenied(_("附件字段格式无效"))
    if not isinstance(value, dict):
        raise PermissionDenied(_("附件字段格式无效"))
    ids = set()
    for item in value.values():
        if not isinstance(item, dict) or "path" not in item:
            raise PermissionDenied(_("附件字段格式无效"))
        ids.update(attachment_ids(item["path"]))
    return ids


@transaction.atomic
def bind_attachments(ticket_id, values, operator):
    ids = set()
    for value in values:
        ids.update(file_ids(value))
    if not ids:
        return  # Pre-upgrade attachments keep their existing behavior.
    records = list(
        Attachment.objects.select_for_update().filter(pk__in=ids).order_by("pk")
    )
    if len(records) != len(ids):
        raise PermissionDenied(_("附件上传记录不存在，请重新上传"))
    for record in records:
        if record.ticket_id == ticket_id:
            continue
        if record.ticket_id is not None or not operator or record.uploader != operator:
            raise PermissionDenied(_("不能将他人的附件或其他工单附件绑定到当前工单"))
        # Conditional update also protects backends without SELECT FOR UPDATE.
        changed = Attachment.objects.filter(
            pk=record.pk, ticket_id__isnull=True
        ).update(ticket_id=ticket_id)
        if changed != 1:
            raise PermissionDenied(_("附件归属已变更，请重试"))


def authorize_download(path, ticket_id=None, allow_unbound=False):
    ids = attachment_ids(path)
    if not ids:
        return  # No migration/backfill of historical files in this change.
    records = list(Attachment.objects.filter(pk__in=ids))
    if len(records) != len(ids):
        raise PermissionDenied(_("附件上传记录不存在"))
    for record in records:
        if record.ticket_id is None:
            if ticket_id is not None and not allow_unbound:
                raise PermissionDenied(_("附件尚未提交到当前工单"))
            # Unbound workflow templates retain the existing resource checks.
            continue
        if ticket_id is None or str(record.ticket_id) != str(ticket_id):
            raise PermissionDenied(_("附件不属于当前工单"))


def bind_ticket_fields(ticket, fields, operator):
    """Use persisted field types, never the type supplied by the submitter."""
    values = {field["key"]: field.get("value", field.get("_value")) for field in fields}
    file_keys = ticket.fields.filter(type="FILE", key__in=values).values_list(
        "key", flat=True
    )
    bind_attachments(ticket.pk, [values[key] for key in file_keys], operator)

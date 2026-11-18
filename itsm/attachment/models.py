"""Ownership of newly uploaded attachments; existing files are not backfilled."""

from django.db import models


class Attachment(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    path = models.TextField()
    uploader = models.CharField(max_length=255)
    # Retain ownership even if a ticket is deleted. A missing ticket must not
    # turn a protected file back into an unbound/legacy attachment.
    ticket_id = models.BigIntegerField(null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AttachmentRef(models.Model):
    """Additional tickets allowed by the uploader to reuse the same file.

    Keeps the "recreate ticket" copy flow working as before: a user may carry
    their own uploads into another ticket, but nobody can reuse an upload they
    did not create. The original ownership (``Attachment.ticket_id``) stays.
    """

    attachment = models.ForeignKey(
        Attachment, related_name="refs", on_delete=models.CASCADE
    )
    ticket_id = models.BigIntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("attachment", "ticket_id")

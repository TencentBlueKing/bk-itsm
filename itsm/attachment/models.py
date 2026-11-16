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

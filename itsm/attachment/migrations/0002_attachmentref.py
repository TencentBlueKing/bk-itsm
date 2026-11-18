import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attachment", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AttachmentRef",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ticket_id", models.BigIntegerField(db_index=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "attachment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="refs",
                        to="attachment.attachment",
                    ),
                ),
            ],
            options={
                "unique_together": {("attachment", "ticket_id")},
            },
        ),
    ]

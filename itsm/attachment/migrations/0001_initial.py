from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.CharField(primary_key=True, max_length=32, serialize=False),
                ),
                ("path", models.TextField()),
                ("uploader", models.CharField(max_length=255)),
                ("ticket_id", models.BigIntegerField(null=True, db_index=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

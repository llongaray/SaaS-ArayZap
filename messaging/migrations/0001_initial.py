# Generated manually for ArayZap

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0001_initial"),
        ("integrations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MessageLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "direction",
                    models.CharField(
                        choices=[("in", "Recebida"), ("out", "Enviada")],
                        max_length=8,
                    ),
                ),
                ("from_address", models.CharField(blank=True, default="", max_length=128)),
                ("to_address", models.CharField(blank=True, default="", max_length=128)),
                ("body", models.TextField(blank=True, default="")),
                ("external_id", models.CharField(blank=True, db_index=True, default="", max_length=128)),
                ("raw_payload", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "integration",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="message_logs",
                        to="integrations.integration",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="message_logs",
                        to="core.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de mensagem",
                "verbose_name_plural": "Registros de mensagens",
                "ordering": ["-created_at"],
            },
        ),
    ]

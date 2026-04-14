# Generated manually for ArayZap

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Integration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                (
                    "type",
                    models.CharField(
                        choices=[("official", "API oficial (Meta)"), ("unofficial", "Não oficial (PyWaBot / Baileys)")],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendente"),
                            ("connected", "Conectado"),
                            ("error", "Erro"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("credentials_encrypted", models.TextField(blank=True, default="")),
                ("session_name", models.CharField(blank=True, default="", max_length=128)),
                ("last_error", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="integrations",
                        to="core.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Integração",
                "verbose_name_plural": "Integrações",
                "ordering": ["-created_at"],
            },
        ),
    ]

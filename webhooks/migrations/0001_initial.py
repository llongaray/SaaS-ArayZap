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
            name="WebhookSubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("url", models.URLField(max_length=2048)),
                (
                    "secret",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Opcional: usado para assinar payload (HMAC-SHA256).",
                        max_length=256,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webhook_subscriptions",
                        to="core.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Webhook CRM",
                "verbose_name_plural": "Webhooks CRM",
                "ordering": ["-created_at"],
            },
        ),
    ]

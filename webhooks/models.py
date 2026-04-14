"""URLs de webhook configuradas pelo cliente (CRM)."""
from django.db import models

from core.models import Organization


class WebhookSubscription(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="webhook_subscriptions",
    )
    url = models.URLField(max_length=2048)
    secret = models.CharField(
        max_length=256,
        blank=True,
        default="",
        help_text="Opcional: usado para assinar payload (HMAC-SHA256).",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Webhook CRM"
        verbose_name_plural = "Webhooks CRM"

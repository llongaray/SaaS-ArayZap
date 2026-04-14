"""Histórico de mensagens (envio e recebimento)."""
from django.db import models

from core.models import Organization
from integrations.models import Integration


class MessageLog(models.Model):
    DIRECTION_IN = "in"
    DIRECTION_OUT = "out"
    DIRECTION_CHOICES = [
        (DIRECTION_IN, "Recebida"),
        (DIRECTION_OUT, "Enviada"),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="message_logs",
    )
    integration = models.ForeignKey(
        Integration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_logs",
    )
    direction = models.CharField(max_length=8, choices=DIRECTION_CHOICES)
    from_address = models.CharField(max_length=128, blank=True, default="")
    to_address = models.CharField(max_length=128, blank=True, default="")
    body = models.TextField(blank=True, default="")
    external_id = models.CharField(max_length=128, blank=True, default="", db_index=True)
    raw_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Registro de mensagem"
        verbose_name_plural = "Registros de mensagens"

"""Integrações oficiais (Meta) e não oficiais (PyWaBot)."""
from django.db import models

from core.crypto import decrypt_json, encrypt_json
from core.models import Organization


class Integration(models.Model):
    """Conexão WhatsApp por organização."""

    TYPE_OFFICIAL = "official"
    TYPE_UNOFFICIAL = "unofficial"
    TYPE_CHOICES = [
        (TYPE_OFFICIAL, "API oficial (Meta)"),
        (TYPE_UNOFFICIAL, "Não oficial (PyWaBot / Baileys)"),
    ]

    STATUS_PENDING = "pending"
    STATUS_CONNECTED = "connected"
    STATUS_ERROR = "error"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendente"),
        (STATUS_CONNECTED, "Conectado"),
        (STATUS_ERROR, "Erro"),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="integrations",
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    # Credenciais específicas do canal (JSON criptografado ou texto em dev)
    credentials_encrypted = models.TextField(blank=True, default="")
    # Sessão PyWaBot (nome estável para reconectar)
    session_name = models.CharField(max_length=128, blank=True, default="")
    last_error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Integração"
        verbose_name_plural = "Integrações"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_type_display()})"

    def get_credentials(self) -> dict:
        return decrypt_json(self.credentials_encrypted or "{}")

    def set_credentials(self, data: dict) -> None:
        self.credentials_encrypted = encrypt_json(data)

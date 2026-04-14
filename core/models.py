"""Organizações (multi-tenant) e tokens de API."""
import hashlib
import secrets

from django.db import models


class Organization(models.Model):
    """Tenant do SaaS — isola integrações e mensagens."""

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Organização"
        verbose_name_plural = "Organizações"

    def __str__(self) -> str:
        return self.name


class ApiToken(models.Model):
    """Token de acesso à API REST (valor exibido apenas na criação)."""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="api_tokens",
    )
    # SHA-256 hex do token (nunca armazenar o token em claro)
    token_hash = models.CharField(max_length=64, db_index=True)
    # Primeiros caracteres para identificação em listagens
    prefix = models.CharField(max_length=12)
    name = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Token de API"
        verbose_name_plural = "Tokens de API"

    def __str__(self) -> str:
        return f"{self.prefix}… ({self.organization})"

    @staticmethod
    def hash_token(raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def generate_raw_token(cls) -> str:
        return secrets.token_urlsafe(32)

    @classmethod
    def create_for_org(cls, organization: Organization, name: str = "") -> tuple["ApiToken", str]:
        """Cria token; retorna (instância, valor_em_claro_para_mostrar_uma_vez)."""
        raw = cls.generate_raw_token()
        prefix = raw[:10]
        token = cls.objects.create(
            organization=organization,
            token_hash=cls.hash_token(raw),
            prefix=prefix,
            name=name,
        )
        return token, raw

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

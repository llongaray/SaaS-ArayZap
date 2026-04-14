"""Autenticação por API Key (Bearer ou X-Api-Key)."""
from rest_framework import authentication, exceptions

from core.models import ApiToken, Organization


class ApiUser:
    """Usuário mínimo para DRF — representa o tenant autenticado pelo token."""

    def __init__(self, organization: Organization, api_token: ApiToken):
        self.organization = organization
        self.api_token = api_token

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def pk(self):
        return self.organization.pk


class ApiKeyAuthentication(authentication.BaseAuthentication):
    """Valida token contra ApiToken ativo."""

    keyword = "Bearer"

    def authenticate(self, request):
        raw = self._extract_raw_token(request)
        if not raw:
            return None

        digest = ApiToken.hash_token(raw)
        try:
            token = ApiToken.objects.select_related("organization").get(
                token_hash=digest,
                revoked_at__isnull=True,
            )
        except ApiToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Token inválido ou revogado.")

        return ApiUser(token.organization, token), token

    def _extract_raw_token(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith(self.keyword + " "):
            return auth[len(self.keyword) + 1 :].strip()
        return request.META.get("HTTP_X_API_KEY", "").strip() or None

    def authenticate_header(self, request):
        return self.keyword

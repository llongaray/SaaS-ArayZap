"""Endpoints de token e bootstrap."""
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import ApiToken, Organization
from core.serializers import (
    ApiTokenCreateSerializer,
    ApiTokenResponseSerializer,
    BootstrapSerializer,
)


class BootstrapTokenView(APIView):
    """Cria primeira organização e token (protegido por BOOTSTRAP_SECRET)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(request=BootstrapSerializer, responses={201: ApiTokenResponseSerializer})
    def post(self, request):
        if not getattr(settings, "ALLOW_TOKEN_BOOTSTRAP", False):
            return Response(
                {"detail": "Bootstrap desabilitado."},
                status=status.HTTP_403_FORBIDDEN,
            )
        ser = BootstrapSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        secret = getattr(settings, "BOOTSTRAP_SECRET", "") or ""
        if not secret or ser.validated_data["bootstrap_secret"] != secret:
            return Response({"detail": "Credencial inválida."}, status=status.HTTP_403_FORBIDDEN)

        org = Organization.objects.create(name=ser.validated_data["organization_name"])
        token_obj, raw = ApiToken.create_for_org(org, name="bootstrap")
        return Response(
            {
                "id": token_obj.id,
                "prefix": token_obj.prefix,
                "name": token_obj.name,
                "token": raw,
                "created_at": token_obj.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class TokenListCreateView(APIView):
    """Lista tokens (sem valor completo) ou cria novo token para a organização autenticada."""

    @extend_schema(responses={200: ApiTokenResponseSerializer(many=True)})
    def get(self, request):
        user = request.user
        qs = ApiToken.objects.filter(organization=user.organization, revoked_at__isnull=True)
        data = [
            {
                "id": t.id,
                "prefix": t.prefix,
                "name": t.name,
                "created_at": t.created_at,
            }
            for t in qs
        ]
        return Response(data)

    @extend_schema(request=ApiTokenCreateSerializer, responses={201: ApiTokenResponseSerializer})
    def post(self, request):
        ser = ApiTokenCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token_obj, raw = ApiToken.create_for_org(
            request.user.organization,
            name=ser.validated_data.get("name") or "",
        )
        return Response(
            {
                "id": token_obj.id,
                "prefix": token_obj.prefix,
                "name": token_obj.name,
                "token": raw,
                "created_at": token_obj.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class TokenRevokeView(APIView):
    """Revoga um token pelo id."""

    def delete(self, request, pk):
        updated = ApiToken.objects.filter(
            pk=pk,
            organization=request.user.organization,
            revoked_at__isnull=True,
        ).update(revoked_at=timezone.now())
        if not updated:
            from rest_framework.exceptions import NotFound

            raise NotFound()
        return Response(status=status.HTTP_204_NO_CONTENT)

"""CRUD de integrações e pairing PyWaBot."""
import asyncio
import logging

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.models import Integration
from integrations.serializers import (
    IntegrationCreateSerializer,
    IntegrationReadSerializer,
    PairingRequestSerializer,
)
from integrations.services.unofficial import (
    UnofficialWhatsAppError,
    connect_and_pair,
    delete_remote_session,
)

logger = logging.getLogger(__name__)


class IntegrationListCreateView(APIView):
    @extend_schema(responses={200: IntegrationReadSerializer(many=True)})
    def get(self, request):
        qs = Integration.objects.filter(organization=request.user.organization)
        return Response(IntegrationReadSerializer(qs, many=True).data)

    @extend_schema(
        request=IntegrationCreateSerializer,
        responses={201: IntegrationReadSerializer},
    )
    def post(self, request):
        ser = IntegrationCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        inst = ser.save()
        return Response(IntegrationReadSerializer(inst).data, status=status.HTTP_201_CREATED)


class IntegrationDetailView(APIView):
    @extend_schema(responses={200: IntegrationReadSerializer})
    def get(self, request, pk):
        inst = get_object_or_404(
            Integration,
            pk=pk,
            organization=request.user.organization,
        )
        return Response(IntegrationReadSerializer(inst).data)


class IntegrationPairingView(APIView):
    """Inicia pairing PyWaBot para integração não oficial."""

    @extend_schema(request=PairingRequestSerializer)
    def post(self, request, pk):
        inst = get_object_or_404(
            Integration,
            pk=pk,
            organization=request.user.organization,
            type=Integration.TYPE_UNOFFICIAL,
        )
        ser = PairingRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        creds = inst.get_credentials()
        api_key = creds.get("api_key") or creds.get("pywabot_api_key")
        if not api_key:
            return Response(
                {"detail": "Defina api_key nas credenciais da integração."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session = inst.session_name
        phone = ser.validated_data["phone_number"]

        async def run():
            return await connect_and_pair(session, api_key, phone, wait_timeout=120)

        try:
            result = asyncio.run(run())
        except UnofficialWhatsAppError as e:
            inst.status = Integration.STATUS_ERROR
            inst.last_error = str(e)
            inst.save(update_fields=["status", "last_error", "updated_at"])
            return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        inst.status = Integration.STATUS_CONNECTED if result.get("connected") else Integration.STATUS_PENDING
        inst.last_error = ""
        inst.save(update_fields=["status", "last_error", "updated_at"])
        return Response(result, status=status.HTTP_200_OK)


class IntegrationSessionDeleteView(APIView):
    """Remove sessão no servidor PyWaBot."""

    def delete(self, request, pk):
        inst = get_object_or_404(
            Integration,
            pk=pk,
            organization=request.user.organization,
            type=Integration.TYPE_UNOFFICIAL,
        )
        creds = inst.get_credentials()
        api_key = creds.get("api_key") or creds.get("pywabot_api_key")
        if not inst.session_name or not api_key:
            return Response({"detail": "Sessão ou api_key ausente."}, status=400)
        try:

            async def run():
                return await delete_remote_session(inst.session_name, api_key)

            ok = asyncio.run(run())
        except Exception as e:
            logger.exception("delete_session")
            return Response({"detail": str(e)}, status=502)
        if ok:
            inst.status = Integration.STATUS_PENDING
            inst.save(update_fields=["status", "updated_at"])
        return Response({"deleted": ok})

"""Envio unificado de mensagens."""
import asyncio
import re

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.models import Integration
from integrations.services.official import OfficialWhatsAppError, OfficialWhatsAppService
from integrations.services.unofficial import UnofficialWhatsAppError, send_text
from messaging.models import MessageLog
from messaging.serializers import SendMessageSerializer


def normalize_digits(numero: str) -> str:
    return re.sub(r"\D", "", numero)


class SendMessageView(APIView):
    @extend_schema(request=SendMessageSerializer)
    def post(self, request):
        ser = SendMessageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        org = request.user.organization
        iid = ser.validated_data["integration_id"]
        inst = get_object_or_404(Integration, pk=iid, organization=org)
        digits = normalize_digits(ser.validated_data["numero"])
        text = ser.validated_data["mensagem"]

        if inst.type == Integration.TYPE_OFFICIAL:
            try:
                svc = OfficialWhatsAppService.from_integration_credentials(inst.get_credentials())
                data = svc.send_text_message(digits, text)
            except OfficialWhatsAppError as e:
                inst.last_error = str(e)
                inst.status = Integration.STATUS_ERROR
                inst.save(update_fields=["last_error", "status", "updated_at"])
                return Response(
                    {"detail": str(e), "payload": e.payload},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            ext = ""
            if isinstance(data, dict) and data.get("messages"):
                ext = str(data["messages"][0].get("id", ""))
            MessageLog.objects.create(
                organization=org,
                integration=inst,
                direction=MessageLog.DIRECTION_OUT,
                to_address=digits,
                body=text,
                external_id=ext[:128],
                raw_payload=data if isinstance(data, dict) else {},
            )
            inst.status = Integration.STATUS_CONNECTED
            inst.last_error = ""
            inst.save(update_fields=["status", "last_error", "updated_at"])
            return Response({"success": True, "provider_response": data})

        # Não oficial
        creds = inst.get_credentials()
        api_key = creds.get("api_key") or creds.get("pywabot_api_key")
        if not api_key or not inst.session_name:
            return Response(
                {"detail": "Configure session_name e api_key nas credenciais."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        async def run():
            return await send_text(inst.session_name, api_key, digits, text)

        try:
            data = asyncio.run(run())
        except UnofficialWhatsAppError as e:
            inst.last_error = str(e)
            inst.save(update_fields=["last_error", "updated_at"])
            return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        MessageLog.objects.create(
            organization=org,
            integration=inst,
            direction=MessageLog.DIRECTION_OUT,
            to_address=digits,
            body=text,
            raw_payload=data if isinstance(data, dict) else {"result": data},
        )
        return Response({"success": True, "provider_response": data})

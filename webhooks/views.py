"""Webhook Meta (público) e registro de webhook CRM."""
import json
import logging

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.models import Integration
from integrations.services.official import verify_webhook_signature
from messaging.models import MessageLog
from webhooks.dispatch import notify_organization_webhooks
from webhooks.meta_parser import iter_incoming_messages
from webhooks.models import WebhookSubscription
from webhooks.serializers import CrmWebhookSerializer

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class MetaWebhookView(View):
    """
    GET: verificação Meta (hub.challenge).
    POST: eventos de mensagem (requer META_APP_SECRET para validar assinatura).
    """

    def get(self, request):
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        verify = getattr(settings, "META_VERIFY_TOKEN", "") or ""
        if mode == "subscribe" and token == verify and challenge:
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponse(status=403)

    def post(self, request):
        raw = request.body
        sig = request.META.get("HTTP_X_HUB_SIGNATURE_256")
        secret = getattr(settings, "META_APP_SECRET", "") or ""
        if secret and not verify_webhook_signature(raw, sig, secret):
            logger.warning("Assinatura Meta inválida.")
            return HttpResponse(status=403)
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return HttpResponse(status=400)

        for item in iter_incoming_messages(body):
            phone_id = item.get("phone_number_id") or ""
            inst = None
            for candidate in Integration.objects.filter(type=Integration.TYPE_OFFICIAL):
                c = candidate.get_credentials()
                if str(c.get("phone_number_id")) == str(phone_id):
                    inst = candidate
                    break
            if not inst:
                logger.info("Integração não encontrada para phone_number_id=%s", phone_id)
                continue
            MessageLog.objects.create(
                organization=inst.organization,
                integration=inst,
                direction=MessageLog.DIRECTION_IN,
                from_address=item["from_e164"],
                body=item["text"],
                external_id=(item.get("message_id") or "")[:128],
                raw_payload=item.get("raw_message"),
            )
            notify_organization_webhooks(
                inst.organization_id,
                "whatsapp.message.received",
                {
                    "integration_id": inst.id,
                    "from": item["from_e164"],
                    "text": item["text"],
                    "message_id": item.get("message_id"),
                },
            )
        return JsonResponse({"success": True})


class CrmWebhookView(APIView):
    """GET: lista webhooks. POST: cadastra URL do CRM."""

    def get(self, request):
        qs = WebhookSubscription.objects.filter(organization=request.user.organization)
        data = [{"id": s.id, "url": s.url, "is_active": s.is_active} for s in qs]
        return Response(data)

    @extend_schema(request=CrmWebhookSerializer, responses={201: CrmWebhookSerializer})
    def post(self, request):
        ser = CrmWebhookSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sub = WebhookSubscription.objects.create(
            organization=request.user.organization,
            url=ser.validated_data["url"],
            secret=ser.validated_data.get("secret") or "",
        )
        return Response(
            {"id": sub.id, "url": sub.url, "is_active": sub.is_active},
            status=status.HTTP_201_CREATED,
        )

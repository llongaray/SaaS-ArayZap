"""Encaminha eventos para URLs cadastradas pelo tenant."""
import hashlib
import hmac
import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


def deliver_to_crm(
    url: str,
    payload: dict[str, Any],
    secret: str = "",
    timeout: float = 15.0,
) -> tuple[bool, str]:
    """POST JSON para o CRM; opcionalmente assina com HMAC-SHA256 (hex) no header X-Webhook-Signature."""
    body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if secret:
        sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        headers["X-Webhook-Signature"] = sig
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(url, content=body, headers=headers)
        ok = r.status_code < 400
        return ok, f"{r.status_code} {r.text[:500]}"
    except Exception as e:
        logger.warning("Falha ao entregar webhook CRM: %s", e)
        return False, str(e)


def notify_organization_webhooks(organization_id: int, event_type: str, data: dict[str, Any]) -> None:
    """Envia para todas as URLs ativas da organização (não bloqueia falhas)."""
    from webhooks.models import WebhookSubscription

    subs = WebhookSubscription.objects.filter(organization_id=organization_id, is_active=True)
    payload = {"event": event_type, "data": data}
    for sub in subs:
        deliver_to_crm(sub.url, payload, secret=sub.secret or "")

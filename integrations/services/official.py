"""Cliente HTTP para WhatsApp Cloud API (Meta Graph)."""
from typing import Any

import httpx


class OfficialWhatsAppError(Exception):
    """Erro retornado pela Graph API ou HTTP."""

    def __init__(self, message: str, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class OfficialWhatsAppService:
    """Envio de mensagens texto pela API oficial."""

    GRAPH_VERSION = "v21.0"
    BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"

    def __init__(self, phone_number_id: str, access_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token

    @classmethod
    def from_integration_credentials(cls, creds: dict) -> "OfficialWhatsAppService":
        pid = creds.get("phone_number_id")
        token = creds.get("access_token") or creds.get("permanent_token")
        if not pid or not token:
            raise OfficialWhatsAppError("Credenciais oficiais incompletas (phone_number_id, access_token).")
        return cls(str(pid), str(token))

    def send_text_message(self, to_e164: str, body: str) -> dict[str, Any]:
        """
        Envia mensagem de texto. `to` sem + (ex.: 5511999999999).
        """
        url = f"{self.BASE}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_e164.lstrip("+"),
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }
        headers = {"Authorization": f"Bearer {self.access_token}"}
        with httpx.Client(timeout=60.0) as client:
            r = client.post(url, json=payload, headers=headers)
        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text}
        if r.status_code >= 400:
            raise OfficialWhatsAppError(
                data.get("error", {}).get("message", r.text) if isinstance(data, dict) else r.text,
                status_code=r.status_code,
                payload=data,
            )
        return data


def verify_webhook_signature(raw_body: bytes, signature_header: str | None, app_secret: str) -> bool:
    """Valida cabeçalho X-Hub-Signature-256 (sha256=...)."""
    import hashlib
    import hmac

    if not signature_header or not app_secret or not signature_header.startswith("sha256="):
        return False
    expected = signature_header.split("=", 1)[1]
    mac = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, expected)

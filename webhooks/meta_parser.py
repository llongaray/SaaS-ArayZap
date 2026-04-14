"""Extrai mensagens simplificadas do payload WhatsApp Cloud API."""
from typing import Any


def iter_incoming_messages(body: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Retorna lista de dicts com keys: from_e164, text, message_id, raw (opcional).
    """
    out: list[dict[str, Any]] = []
    entries = body.get("entry") or []
    for ent in entries:
        for change in ent.get("changes") or []:
            value = change.get("value") or {}
            messages = value.get("messages") or []
            metadata = value.get("metadata", {})
            phone_number_id = metadata.get("phone_number_id", "")
            for msg in messages:
                if msg.get("type") != "text":
                    continue
                from_obj = msg.get("from") or ""
                txt = (msg.get("text") or {}).get("body") or ""
                mid = msg.get("id") or ""
                out.append(
                    {
                        "from_e164": from_obj,
                        "text": txt,
                        "message_id": mid,
                        "phone_number_id": phone_number_id,
                        "raw_message": msg,
                    }
                )
    return out

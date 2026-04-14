"""Criptografia opcional de credenciais (Fernet)."""
import json
from typing import Any

from django.conf import settings


def _get_fernet():
    key = getattr(settings, "FERNET_KEY", None) or ""
    if not key:
        return None
    from cryptography.fernet import Fernet

    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_json(data: dict[str, Any]) -> str:
    """Serializa e criptografa; se FERNET_KEY não estiver definido, retorna JSON em claro (apenas dev)."""
    raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
    f = _get_fernet()
    if f is None:
        return raw.decode("utf-8")
    return f.encrypt(raw).decode("ascii")


def decrypt_json(payload: str) -> dict[str, Any]:
    """Descriptografa ou interpreta JSON em claro."""
    if not payload:
        return {}
    f = _get_fernet()
    if f is None:
        return json.loads(payload)
    try:
        dec = f.decrypt(payload.encode("ascii"))
    except Exception:
        # Compatível com payload antigo em JSON sem criptografia
        return json.loads(payload)
    return json.loads(dec.decode("utf-8"))

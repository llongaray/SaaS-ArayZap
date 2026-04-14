"""Adaptador PyWaBot (assíncrono) para sessão não oficial."""
from typing import Any


class UnofficialWhatsAppError(Exception):
    """Falha ao usar PyWaBot ou servidor Baileys."""


async def build_bot(session_name: str, api_key: str) -> Any:
    """Instancia PyWaBot (URL do servidor vem da própria biblioteca)."""
    try:
        from pywabot import PyWaBot
    except ImportError as e:
        raise UnofficialWhatsAppError("Pacote pywabot não instalado.") from e
    return PyWaBot(session_name, api_key)


def phone_to_jid(e164_digits: str) -> str:
    """Converte número só dígitos para JID individual."""
    d = "".join(c for c in e164_digits if c.isdigit())
    return f"{d}@s.whatsapp.net"


async def connect_and_pair(
    session_name: str,
    api_key: str,
    phone_number: str,
    *,
    wait_timeout: int = 120,
) -> dict[str, Any]:
    """
    Fluxo da documentação PyWaBot: connect; se falhar, pairing + espera.
    """
    bot = await build_bot(session_name, api_key)
    if await bot.connect():
        return {"pairing_code": None, "connected": True}

    code = await bot.request_pairing_code(phone_number)
    if not code:
        raise UnofficialWhatsAppError("Não foi possível obter código de pairing.")
    ok = await bot.wait_for_connection(timeout=wait_timeout)
    if not ok:
        raise UnofficialWhatsAppError("Timeout aguardando conexão após pairing.")
    return {"pairing_code": code, "connected": True}


async def send_text(session_name: str, api_key: str, to_e164: str, text: str) -> dict[str, Any] | None:
    """Conecta (se necessário) e envia texto para um número."""
    bot = await build_bot(session_name, api_key)
    if not await bot.connect():
        raise UnofficialWhatsAppError("Sessão não conectada. Conclua o pairing antes.")
    jid = phone_to_jid(to_e164)
    return await bot.send_message(jid, text)


async def delete_remote_session(session_name: str, api_key: str) -> bool:
    from pywabot import PyWaBot

    return await PyWaBot.delete_session(session_name, api_key)

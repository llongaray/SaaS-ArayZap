"""
Processo long-running: mantém sessões PyWaBot e encaminha mensagens ao CRM.

Uso (após migrar e configurar o banco):
    python manage.py run_pywabot_consumer
"""
import asyncio
import logging

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from integrations.models import Integration
from messaging.models import MessageLog
from webhooks.dispatch import notify_organization_webhooks

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Escuta mensagens via PyWaBot para todas as integrações não oficiais conectadas."

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        self.stdout.write(self.style.NOTICE("Iniciando consumer PyWaBot (Ctrl+C para sair)..."))
        try:
            from pywabot import PyWaBot
        except ImportError:
            self.stderr.write(self.style.ERROR("Instale o pacote pywabot."))
            return

        qs = list(
            Integration.objects.filter(type=Integration.TYPE_UNOFFICIAL).exclude(session_name="")
        )
        if not qs:
            self.stdout.write("Nenhuma integração não oficial com session_name.")
            return

        try:
            asyncio.run(self._run(PyWaBot, qs))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Encerrado."))

    async def _run(self, PyWaBot, integrations: list):
        tasks = [self._listen_one(PyWaBot, inst) for inst in integrations]
        await asyncio.gather(*tasks)

    async def _listen_one(self, PyWaBot, inst: Integration):
        creds = inst.get_credentials()
        api_key = creds.get("api_key") or creds.get("pywabot_api_key")
        if not api_key:
            logger.warning("Integração %s sem api_key.", inst.pk)
            return

        bot = PyWaBot(inst.session_name, api_key)

        @bot.on_message
        async def handler(message):
            if getattr(message, "from_me", False):
                return
            text = getattr(message, "text", None) or ""
            chat = getattr(message, "chat", None) or ""
            mid = getattr(message, "id", None) or ""

            await self._persist_and_notify(inst, chat, text, mid, message.raw)

        try:
            if not await bot.connect():
                logger.warning("Não conectado: integração %s (%s).", inst.pk, inst.name)
                return
            logger.info("Escutando sessão %s (integração %s).", inst.session_name, inst.pk)
            await bot.start_listening()
        except Exception as e:
            logger.exception("Erro na sessão %s: %s", inst.session_name, e)

    @staticmethod
    async def _persist_and_notify(inst, chat, text, mid, raw_payload):
        @sync_to_async
        def _save():
            MessageLog.objects.create(
                organization=inst.organization,
                integration=inst,
                direction=MessageLog.DIRECTION_IN,
                from_address=(chat or "")[:128],
                body=text,
                external_id=(str(mid) if mid else "")[:128],
                raw_payload=raw_payload if isinstance(raw_payload, dict) else {"raw": str(raw_payload)},
            )
            notify_organization_webhooks(
                inst.organization_id,
                "whatsapp.message.received",
                {
                    "integration_id": inst.id,
                    "channel": "unofficial",
                    "from_jid": chat,
                    "text": text,
                    "message_id": str(mid) if mid else None,
                },
            )

        await _save()

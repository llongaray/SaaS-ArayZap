# ArayZap — SaaS WhatsApp (API oficial + PyWaBot)

Backend **Django + Django REST Framework**, **somente rotas REST** (sem templates HTML). Integra:

- **WhatsApp Cloud API (Meta)** — envio HTTP e webhook de entrada.
- **Canal não oficial** — cliente [**PyWaBot**](https://pypi.org/project/pywabot/) (Baileys via servidor usado pela biblioteca), pairing e consumer dedicado.

Persistência: **PostgreSQL**. Documentação para PostgreSQL no Windows 11: [docs/postgresql-windows.md](docs/postgresql-windows.md).

## Requisitos

- Python 3.11+
- PostgreSQL 14+
- Variáveis de ambiente (veja [.env.example](.env.example))

## Instalação (resumo)

```powershell
cd E:\Programas\SaaS-ArayZap
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edite .env (SECRET_KEY, DB_*, BOOTSTRAP_SECRET, META_*)
python manage.py migrate
python manage.py runserver
```

## Autenticação da API

Header:

- `Authorization: Bearer <token>` **ou**
- `X-Api-Key: <token>`

Primeiro token (apenas com `ALLOW_TOKEN_BOOTSTRAP=true` e `BOOTSTRAP_SECRET` definidos):

`POST /api/tokens/bootstrap/` — JSON: `bootstrap_secret`, `organization_name`.

Resposta inclui `token` **uma única vez**; guarde com segurança.

Novos tokens (já autenticado): `POST /api/tokens/`.

Revogar: `DELETE /api/tokens/<id>/`.

## Endpoints principais

| Método | Caminho | Descrição |
|--------|---------|-----------|
| GET/POST | `/api/tokens/` | Listar / criar tokens |
| POST | `/api/tokens/bootstrap/` | Primeiro token (bootstrap) |
| DELETE | `/api/tokens/<id>/` | Revogar token |
| GET/POST | `/api/integrations/` | Listar / criar integração |
| GET | `/api/integrations/<id>/` | Detalhe |
| POST | `/api/integrations/<id>/pairing/` | Pairing PyWaBot (`phone_number`) |
| DELETE | `/api/integrations/<id>/session/` | Remover sessão no servidor PyWaBot |
| POST | `/api/messages/send/` | Envio unificado |
| GET/POST | `/api/webhooks/crm/` | Listar / registrar webhook do CRM |
| GET/POST | `/api/meta/webhook/` | Webhook Meta (verificação + eventos) |
| GET | `/api/schema/` | OpenAPI (schema) |
| GET | `/api/docs/` | Swagger UI |

### Criar integração oficial

`POST /api/integrations/`

```json
{
  "name": "Linha oficial",
  "type": "official",
  "session_name": "",
  "credentials": {
    "phone_number_id": "SEU_PHONE_NUMBER_ID",
    "access_token": "TOKEN_DE_LONGA_DURACAO"
  }
}
```

### Criar integração não oficial (PyWaBot)

```json
{
  "name": "Sessão suporte",
  "type": "unofficial",
  "session_name": "minha_sessao_unica",
  "credentials": {
    "api_key": "SUA_API_KEY_PYWABOT"
  }
}
```

Depois: `POST /api/integrations/<id>/pairing/` com `{"phone_number": "5511999999999"}` (só dígitos).

### Enviar mensagem

`POST /api/messages/send/`

```json
{
  "integration_id": 1,
  "numero": "5511999999999",
  "mensagem": "Olá!"
}
```

### Webhook Meta

Configure no painel da Meta a URL pública `https://seu-dominio/api/meta/webhook/` e o mesmo `META_VERIFY_TOKEN` do `.env`. Assinatura: `META_APP_SECRET`.

### Webhook do CRM

`POST /api/webhooks/crm/` — `url`, `secret` (opcional). Eventos recebidos pelo backend são reenviados em JSON; se `secret` estiver definido, o header `X-Webhook-Signature` traz HMAC-SHA256 do corpo.

## Processo auxiliar: escuta PyWaBot

Em paralelo ao `runserver`, para receber mensagens no canal não oficial:

```powershell
python manage.py run_pywabot_consumer
```

## Segurança e compliance

- Canal não oficial pode violar os Termos do WhatsApp; use por sua conta e risco.
- Produção: `DEBUG=false`, `ALLOW_TOKEN_BOOTSTRAP=false`, `FERNET_KEY` definido, HTTPS e segredos fortes.

## Disclaimer

PyWaBot e integrações não oficiais não são produtos Meta. Este projeto é uma base técnica para API REST e multi-tenant por organização.

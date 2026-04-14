# PostgreSQL no Windows 11 (terminal)

Instruções para instalar e usar o PostgreSQL em uma máquina Windows 11 comum, focando no uso pelo **PowerShell** ou **cmd**.

## 1. Instalação

1. Baixe o instalador em [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/) (pacote **EnterpriseDB**) ou use o **winget**, se disponível no seu ambiente:
   - `winget search PostgreSQL` e depois `winget install PostgreSQL.PostgreSQL` (o id exato pode variar).
2. Durante o instalador, anote:
   - a **porta** (padrão `5432`);
   - a **senha** do usuário `postgres`;
   - a pasta de instalação (ex.: `C:\Program Files\PostgreSQL\16`).

## 2. Adicionar ao PATH (para usar no terminal)

Inclua a pasta `bin` do PostgreSQL no PATH do Windows, por exemplo:

`C:\Program Files\PostgreSQL\16\bin`

- **Painel de Controle** → Sistema → Configurações avançadas → Variáveis de ambiente → editar **Path** → Novo → colar o caminho acima (ajuste a versão `16` se necessário).

Feche e reabra o terminal. Teste:

```powershell
psql --version
```

## 3. Serviço Windows

O instalador costuma registrar o PostgreSQL como **serviço** (inicia com o Windows). Para verificar:

- `Win + R` → `services.msc` → procure **postgresql-x64-…**.

Alternativa manual (avançado), com `pg_ctl` (troque `-D` pelo diretório de dados real, ex.: `C:\Program Files\PostgreSQL\16\data`):

```powershell
& "C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe" -D "C:\Program Files\PostgreSQL\16\data" start
& "C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe" -D "C:\Program Files\PostgreSQL\16\data" stop
```

## 4. Criar banco e usuário para o Django

Abra o **SQL Shell (psql)** ou o PowerShell com `psql` no PATH:

```powershell
psql -U postgres -h localhost
```

No prompt `postgres=#`:

```sql
CREATE USER arayzap_user WITH PASSWORD 'sua_senha_aqui';
CREATE DATABASE arayzap OWNER arayzap_user;
GRANT ALL PRIVILEGES ON DATABASE arayzap TO arayzap_user;
\q
```

## 5. Variáveis do projeto ArayZap

No arquivo `.env` (a partir de `.env.example`), use:

```env
DB_NAME=arayzap
DB_USER=arayzap_user
DB_PASSWORD=sua_senha_aqui
DB_HOST=localhost
DB_PORT=5432
```

## 6. Aplicar migrações Django (você executa localmente)

Com o ambiente virtual ativo e dependências instaladas:

```powershell
python manage.py migrate
```

(Este passo não é executado automaticamente pelo assistente; rode na sua máquina quando o banco estiver pronto.)

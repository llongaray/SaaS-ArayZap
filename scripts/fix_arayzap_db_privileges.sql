-- Corrige "permissão negada para tabela django_migrations" quando as tabelas
-- pertencem ao usuário postgres e o Django usa arayzap_user.
--
-- Nota: em PostgreSQL recente, REASSIGN OWNED BY postgres pode falhar para objetos
-- do sistema; por isso usamos GRANT em schema public.
--
-- Rode como superusuário, no banco arayzap:
--   psql -U postgres -h localhost -d arayzap -f scripts/fix_arayzap_db_privileges.sql

GRANT USAGE ON SCHEMA public TO arayzap_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO arayzap_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO arayzap_user;

-- Objetos criados no futuro pelo postgres (ex.: novas migrações) — ajuste se necessário
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO arayzap_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO arayzap_user;

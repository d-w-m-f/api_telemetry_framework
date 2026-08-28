-- Requer shared_preload_libraries='pg_stat_statements' no postgresql.conf.
-- Aplicado pelo orquestrador, nunca pelo sujeito sob teste.
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

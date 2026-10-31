-- Camadas: raw (landing, append-only) -> bronze (parsing 1:1, tudo VARCHAR) -> silver/gold/marts (dbt)
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS raw.fetch_log (
    raw_id           VARCHAR,    -- determinístico: hash(source|url|payload_sha256); falhas incluem timestamp
    run_id           VARCHAR,
    source           VARCHAR,    -- 'bbr' | 'nba'
    endpoint         VARCHAR,    -- ex.: season_advanced | nba_api:LeagueDashPlayerStats
    url              VARCHAR,
    params_json      VARCHAR,
    fetched_at       TIMESTAMP,
    http_status      INTEGER,
    payload_path     VARCHAR,    -- arquivo imutável em data/raw/<source>/<sha[:2]>/<sha>.<ext>
    payload_sha256   VARCHAR,
    payload_bytes    BIGINT,
    terms_ref        VARCHAR,    -- versão dos termos de uso vigente na coleta
    last_verified_at TIMESTAMP,
    note             VARCHAR
);

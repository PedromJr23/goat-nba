WITH pool AS (
    SELECT player_id FROM {{ ref('int_goat_pool') }}
),
season_data AS (
    SELECT * FROM {{ ref('stg_bbr_advanced') }}
    WHERE team_id = 'TOT'
       OR player_id NOT IN (SELECT DISTINCT player_id FROM {{ ref('stg_bbr_advanced') }} WHERE team_id = 'TOT' AND season_end_year = stg_bbr_advanced.season_end_year)
),
-- Calcula média e desvio padrão por temporada (com piso de 500 minutos)
season_stats AS (
    SELECT
        season_end_year,
        AVG(per) AS avg_per, STDDEV(per) AS std_per,
        AVG(ws_per_48) AS avg_ws48, STDDEV(ws_per_48) AS std_ws48,
        AVG(bpm) AS avg_bpm, STDDEV(bpm) AS std_bpm,
        AVG(vorp) AS avg_vorp, STDDEV(vorp) AS std_vorp
    FROM season_data
    WHERE minutes_played >= 500
    GROUP BY season_end_year
)
SELECT
    d.raw_id,
    d.season_end_year,
    d.player_id,
    d.player_name,
    d.games_played,
    d.minutes_played,
    d.win_shares,
    d.vorp,
    -- Normalização Z-Score por Temporada (Ajuste de Era)
    (d.per - s.avg_per) / NULLIF(s.std_per, 0) AS z_per,
    (d.ws_per_48 - s.avg_ws48) / NULLIF(s.std_ws48, 0) AS z_ws48,
    (d.bpm - s.avg_bpm) / NULLIF(s.std_bpm, 0) AS z_bpm,
    (d.vorp - s.avg_vorp) / NULLIF(s.std_vorp, 0) AS z_vorp
FROM season_data d
JOIN season_stats s ON d.season_end_year = s.season_end_year
WHERE d.player_id IN (SELECT player_id FROM pool)

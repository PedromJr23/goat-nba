WITH stg AS (
    SELECT * FROM {{ ref('stg_bbr_advanced') }}
),
-- Filtra a linha consolidada "TOT" para quem trocou de time, mantendo o total da temporada
deduped AS (
    SELECT * FROM stg
    WHERE team_id = 'TOT'
       OR player_id NOT IN (SELECT DISTINCT player_id FROM stg WHERE team_id = 'TOT' AND season_end_year = stg.season_end_year)
),
-- Calcula métricas acumuladas e de pico
player_totals AS (
    SELECT
        player_id,
        player_name,
        SUM(win_shares) AS total_ws,
        COUNT(DISTINCT season_end_year) AS total_seasons
    FROM deduped
    WHERE season_end_year BETWEEN 1974 AND 2024
    GROUP BY 1, 2
),
ranked_accumulated AS (
    SELECT
        player_id,
        player_name,
        total_ws,
        DENSE_RANK() OVER (ORDER BY total_ws DESC) AS rank_accumulated_ws
    FROM player_totals
),
season_ranks AS (
    SELECT
        player_id,
        win_shares,
        ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY win_shares DESC) AS season_rank
    FROM deduped
),
peak_totals AS (
    SELECT
        player_id,
        SUM(win_shares) AS peak_5yr_ws
    FROM season_ranks
    WHERE season_rank <= 5
    GROUP BY 1
),
ranked_peak AS (
    SELECT
        player_id,
        peak_5yr_ws,
        DENSE_RANK() OVER (ORDER BY peak_5yr_ws DESC) AS rank_peak_ws
    FROM peak_totals
)
-- União objetiva: Top 40 em WS Acumulado OU Top 40 em Pico (5 melhores anos)
SELECT
    COALESCE(a.player_id, p.player_id) AS player_id,
    a.player_name,
    a.total_ws,
    a.rank_accumulated_ws,
    p.peak_5yr_ws,
    p.rank_peak_ws,
    TRUE AS is_in_pool
FROM ranked_accumulated a
FULL OUTER JOIN ranked_peak p ON a.player_id = p.player_id
WHERE a.rank_accumulated_ws <= 40 OR p.rank_peak_ws <= 40

WITH pool AS (
    SELECT * FROM {{ ref('int_goat_pool') }}
),
stats AS (
    SELECT
        player_id,
        MIN(season_end_year) AS first_season,
        MAX(season_end_year) AS last_season,
        COUNT(DISTINCT season_end_year) AS seasons_played,
        SUM(games_played) AS total_games,
        SUM(minutes_played) AS total_minutes
    FROM {{ ref('stg_bbr_advanced') }}
    GROUP BY 1
)
SELECT
    p.player_id,
    p.player_name,
    p.total_ws,
    p.rank_accumulated_ws,
    p.peak_5yr_ws,
    p.rank_peak_ws,
    s.first_season,
    s.last_season,
    s.seasons_played,
    s.total_games,
    s.total_minutes
FROM pool p
LEFT JOIN stats s ON p.player_id = s.player_id

WITH raw_advanced AS (
    SELECT * FROM {{ source('bronze', 'bbr_season_advanced') }}
),
cleaned AS (
    SELECT
        raw_id,
        CAST(season_end_year AS INT) AS season_end_year,
        player_id,
        player AS player_name,
        pos AS position,
        team_id,
        CAST(games AS INT) AS games_played,
        CAST(mp AS INT) AS minutes_played,
        CAST(per AS FLOAT) AS per,
        CAST(ws AS FLOAT) AS win_shares,
        CAST(ws_per_48 AS FLOAT) AS ws_per_48,
        CAST(bpm AS FLOAT) AS bpm,
        CAST(vorp AS FLOAT) AS vorp,
        _loaded_at
    FROM raw_advanced
    WHERE player_id IS NOT NULL
)
SELECT * FROM cleaned

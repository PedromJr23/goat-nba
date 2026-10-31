SELECT
    player_id,
    COUNT(*) AS total_rows
FROM {{ ref('int_goat_pool') }}
GROUP BY player_id
HAVING COUNT(*) > 1

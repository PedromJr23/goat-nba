SELECT *
FROM {{ ref('stg_bbr_advanced') }}
WHERE win_shares < -5 OR win_shares > 40

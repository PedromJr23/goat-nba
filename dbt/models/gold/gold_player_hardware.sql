WITH pool AS (
    SELECT player_id, player_name FROM {{ ref('int_goat_pool') }}
),
hardware_raw AS (
    SELECT 'Michael Jordan' AS name, 5 AS mvp, 6 AS fmvp, 6 AS rings, 11 AS all_nba, 9 AS all_def
    UNION ALL SELECT 'Kareem Abdul-Jabbar', 6, 2, 6, 15, 11
    UNION ALL SELECT 'LeBron James', 4, 4, 4, 20, 6
    UNION ALL SELECT 'Magic Johnson', 3, 3, 5, 10, 0
    UNION ALL SELECT 'Tim Duncan', 2, 3, 5, 15, 15
    UNION ALL SELECT 'Kobe Bryant', 1, 2, 5, 15, 12
    UNION ALL SELECT 'Shaquille O''Neal', 1, 3, 4, 14, 3
    UNION ALL SELECT 'Larry Bird', 3, 2, 3, 10, 3
    UNION ALL SELECT 'Stephen Curry', 2, 1, 4, 10, 0
    UNION ALL SELECT 'Kevin Durant', 1, 2, 2, 11, 0
    UNION ALL SELECT 'Hakeem Olajuwon', 1, 2, 2, 12, 9
    UNION ALL SELECT 'Nikola Jokić', 3, 1, 1, 6, 0
    UNION ALL SELECT 'Giannis Antetokounmpo', 2, 1, 1, 8, 5
    UNION ALL SELECT 'Karl Malone', 2, 0, 0, 14, 4
    UNION ALL SELECT 'David Robinson', 1, 0, 2, 10, 8
    UNION ALL SELECT 'Kevin Garnett', 1, 0, 1, 9, 12
    UNION ALL SELECT 'Dirk Nowitzki', 1, 1, 1, 12, 0
    UNION ALL SELECT 'Charles Barkley', 1, 0, 0, 11, 0
    UNION ALL SELECT 'Julius Erving', 1, 0, 1, 9, 1
    UNION ALL SELECT 'Moses Malone', 3, 1, 1, 8, 2
    UNION ALL SELECT 'Dwyane Wade', 0, 1, 3, 8, 3
    UNION ALL SELECT 'Scottie Pippen', 0, 0, 6, 7, 10
    UNION ALL SELECT 'Chris Paul', 0, 0, 0, 11, 9
    UNION ALL SELECT 'James Harden', 1, 0, 0, 7, 0
    UNION ALL SELECT 'John Stockton', 0, 0, 0, 11, 5
    UNION ALL SELECT 'Steve Nash', 2, 0, 0, 7, 0
    UNION ALL SELECT 'Russell Westbrook', 1, 0, 0, 9, 0
    UNION ALL SELECT 'Bob McAdoo', 1, 0, 2, 0, 0
    UNION ALL SELECT 'Clyde Drexler', 0, 0, 1, 5, 0
    UNION ALL SELECT 'Gary Payton', 0, 0, 1, 9, 9
    UNION ALL SELECT 'Paul Pierce', 0, 1, 1, 4, 0
    UNION ALL SELECT 'Jason Kidd', 0, 0, 1, 6, 9
    UNION ALL SELECT 'Patrick Ewing', 0, 0, 0, 7, 3
    UNION ALL SELECT 'Pau Gasol', 0, 0, 2, 4, 0
    UNION ALL SELECT 'Dwight Howard', 0, 0, 1, 8, 5
    UNION ALL SELECT 'Anthony Davis', 0, 0, 1, 5, 5
    UNION ALL SELECT 'Chauncey Billups', 0, 1, 1, 3, 2
    UNION ALL SELECT 'Ray Allen', 0, 0, 2, 2, 0
)
SELECT 
    p.player_id,
    p.player_name,
    COALESCE(h.mvp, 0) AS mvp,
    COALESCE(h.fmvp, 0) AS fmvp,
    COALESCE(h.rings, 0) AS rings,
    COALESCE(h.all_nba, 0) AS all_nba,
    COALESCE(h.all_def, 0) AS all_def
FROM pool p
LEFT JOIN hardware_raw h ON p.player_name = h.name

-- ===== Parameter (Messintervall in Sekunden) =====
CREATE OR REPLACE VIEW v_params AS
SELECT 30::int AS interval_seconds;

-- ===== Erster Messpunkt pro Gerät =====
CREATE OR REPLACE VIEW v_first_seen AS
SELECT device_id, MIN(timestamp) AS first_seen
FROM sensor_data
GROUP BY device_id;

-- ===== Tages-Ist je Device =====
CREATE OR REPLACE VIEW v_counts_daily AS
SELECT time_bucket('1 day', timestamp) AS day,
       device_id,
       COUNT(*)::bigint AS ist_count
FROM sensor_data
GROUP BY 1,2;

-- ===== Tages-Soll je Device (ab first_seen, bis jetzt) =====
CREATE OR REPLACE VIEW v_expected_daily AS
WITH
  params AS (SELECT interval_seconds FROM v_params),
  fs AS (SELECT * FROM v_first_seen),
  day_bounds AS (
    SELECT generate_series(
             date_trunc('day', (SELECT MIN(first_seen) FROM fs)),
             date_trunc('day', now()),
             interval '1 day'
           ) AS day
  ),
  expanded AS (
    SELECT d.day, f.device_id, f.first_seen
    FROM day_bounds d
    CROSS JOIN fs f
  ),
  effective_window AS (
    SELECT
      e.device_id,
      e.day,
      GREATEST(e.day, e.first_seen)          AS start_ts,
      LEAST(e.day + interval '1 day', now()) AS end_ts
    FROM expanded e
  )
SELECT
  device_id,
  day,
  CASE
    WHEN end_ts <= start_ts THEN 0::bigint
    ELSE 1 + FLOOR(EXTRACT(EPOCH FROM (end_ts - start_ts)) / (SELECT interval_seconds FROM v_params))::bigint
  END AS soll_count
FROM effective_window;


-- ===== Tages-Gesamt (Ist/Soll) =====
CREATE OR REPLACE VIEW v_totals_daily AS
SELECT
  e.day,
  SUM(e.soll_count)::bigint AS soll_total,
  SUM(COALESCE(i.ist_count,0))::bigint AS ist_total
FROM v_expected_daily e
LEFT JOIN v_counts_daily i
  ON i.device_id = e.device_id AND i.day = e.day
GROUP BY e.day
ORDER BY e.day;

-- ===== Heute (Ist/Soll) =====
CREATE OR REPLACE VIEW v_totals_today AS
SELECT
  (SELECT COALESCE(SUM(soll_count),0) FROM v_expected_daily WHERE day = date_trunc('day', now())) AS soll_today,
  (SELECT COALESCE(SUM(ist_count),0)  FROM v_counts_daily  WHERE day = date_trunc('day', now())) AS ist_today;

-- ===== Seit Start (Ist/Soll, gesamt) =====
CREATE OR REPLACE VIEW v_totals_since_start AS
WITH params AS (SELECT interval_seconds FROM v_params),
per_dev AS (
  SELECT
    f.device_id,
    f.first_seen,
    COUNT(s.*)::bigint AS ist_count,
    CASE
      WHEN now() <= f.first_seen THEN 0::bigint
      ELSE 1 + FLOOR(EXTRACT(EPOCH FROM (now() - f.first_seen)) / (SELECT interval_seconds FROM params))::bigint
    END AS soll_count
  FROM v_first_seen f
  LEFT JOIN sensor_data s
    ON s.device_id = f.device_id AND s.timestamp >= f.first_seen
  GROUP BY f.device_id, f.first_seen
)
SELECT SUM(ist_count)::bigint  AS ist_total,
       SUM(soll_count)::bigint AS soll_total
FROM per_dev;


-- ===== Gaps > 10 Minuten =====
CREATE OR REPLACE VIEW v_sensor_gaps AS
WITH ordered AS (
  SELECT
    device_id,
    timestamp,
    LEAD(timestamp) OVER (PARTITION BY device_id ORDER BY timestamp) AS next_ts
  FROM sensor_data
)
SELECT
  device_id,
  timestamp AS gap_start,
  next_ts   AS gap_end,
  (next_ts - timestamp) AS gap_duration
FROM ordered
WHERE next_ts IS NOT NULL
  AND next_ts - timestamp > interval '10 minutes'
ORDER BY device_id, gap_start;

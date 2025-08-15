-- ===== Parameter (Messintervall in Sekunden) =====
CREATE OR REPLACE VIEW v_params AS
SELECT 30::int AS interval_seconds;

-- ===== Geräte-Liste (fix: IDs 1 und 2) =====
CREATE OR REPLACE VIEW v_devices AS
SELECT * FROM (VALUES (1),(2)) AS t(device_id);

-- ===== First/Last Seen & Global Start =====
CREATE OR REPLACE VIEW v_first_seen AS
SELECT device_id, MIN(timestamp) AS first_seen
FROM sensor_data
GROUP BY device_id;

CREATE OR REPLACE VIEW v_last_seen AS
SELECT device_id, MAX(timestamp) AS last_seen
FROM sensor_data
GROUP BY device_id;

-- Globaler Start des Monitorings (oder fallback: heute 00:00, wenn noch keine Daten vorhanden)
CREATE OR REPLACE VIEW v_global_start AS
SELECT COALESCE((SELECT MIN(timestamp) FROM sensor_data), date_trunc('day', now())) AS start_ts;

-- ===== Seit-Beginn: Soll/Ist/Availability je Device =====
CREATE OR REPLACE VIEW v_totals_since_start_by_device AS
WITH params AS (SELECT interval_seconds FROM v_params),
gs AS (SELECT start_ts FROM v_global_start),
ref AS (
  -- reference start: first_seen if available, otherwise global start
  SELECT d.device_id,
         COALESCE(f.first_seen, (SELECT start_ts FROM gs)) AS ref_start
  FROM v_devices d
  LEFT JOIN v_first_seen f USING (device_id)
),
calc AS (
  SELECT
    r.device_id,
    r.ref_start,
    -- expected since the moment AFTER ref_start (no +1, no instant bucket)
    GREATEST(
      0,
      FLOOR(EXTRACT(EPOCH FROM (now() - r.ref_start)) / (SELECT interval_seconds FROM params))
    )::bigint AS soll_calc
  FROM ref r
)
SELECT
  c.device_id,
  c.soll_calc                          AS soll_total,
  -- count only samples strictly AFTER ref_start (avoid the “first hit = 100%”)
  COUNT(s.*)::bigint                   AS ist_total,
CASE WHEN c.soll_calc = 0 THEN 0.0
     ELSE ROUND(100.0 * COUNT(s.*) / c.soll_calc, 2)
END AS availability_pct

FROM calc c
LEFT JOIN sensor_data s
  ON s.device_id = c.device_id
 AND s.timestamp > c.ref_start
GROUP BY c.device_id, c.ref_start, c.soll_calc
ORDER BY c.device_id;


-- ===== Gaps > 10 Minuten (seit Beginn) =====
CREATE OR REPLACE VIEW v_sensor_gaps AS
WITH gs AS (SELECT start_ts FROM v_global_start),
-- interne Lücken zwischen Messpunkten
ordered AS (
  SELECT
    device_id,
    timestamp,
    LEAD(timestamp) OVER (PARTITION BY device_id ORDER BY timestamp) AS next_ts
  FROM sensor_data
),
internal AS (
  SELECT
    device_id,
    timestamp AS gap_start,
    next_ts   AS gap_end,
    (next_ts - timestamp) AS gap_duration
  FROM ordered
  WHERE next_ts IS NOT NULL
    AND next_ts - timestamp > interval '10 minutes'
),
-- Head-Gap: von globalem Start bis zum ersten Messpunkt (oder bis jetzt, wenn nie gesendet)
head AS (
  SELECT
    d.device_id,
    (SELECT start_ts FROM gs) AS gap_start,
    COALESCE(f.first_seen, now()) AS gap_end,
    COALESCE(f.first_seen, now()) - (SELECT start_ts FROM gs) AS gap_duration
  FROM v_devices d
  LEFT JOIN v_first_seen f ON f.device_id = d.device_id
  WHERE COALESCE(f.first_seen, now()) - (SELECT start_ts FROM gs) > interval '10 minutes'
),
-- Tail-Gap: vom letzten Messpunkt bis jetzt
tail AS (
  SELECT
    d.device_id,
    l.last_seen AS gap_start,
    now()       AS gap_end,
    now() - l.last_seen AS gap_duration
  FROM v_devices d
  LEFT JOIN v_last_seen l ON l.device_id = d.device_id
  WHERE l.last_seen IS NOT NULL
    AND now() - l.last_seen > interval '10 minutes'
)
SELECT device_id, gap_start, gap_end, gap_duration FROM internal
UNION ALL
SELECT device_id, gap_start, gap_end, gap_duration FROM head
UNION ALL
SELECT device_id, gap_start, gap_end, gap_duration FROM tail
ORDER BY device_id, gap_start;

-- ===== Parameter (measurement interval in seconds) =====
CREATE OR REPLACE VIEW v_params AS
SELECT 30::int AS interval_seconds;

-- ===== Device list (fixed: IDs 1 and 2) =====
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

-- Global monitoring start (or fallback: today at 00:00 if no data exists yet)
CREATE OR REPLACE VIEW v_global_start AS
SELECT COALESCE((SELECT MIN(timestamp) FROM sensor_data), date_trunc('day', now())) AS start_ts;

-- ===== Since start: expected/actual/availability per device =====
CREATE OR REPLACE VIEW v_totals_since_start_by_device AS
WITH params AS (
  SELECT
    interval_seconds::int AS sec,
    (interval '1 second') * interval_seconds::int AS iv
  FROM v_params
),
gs AS (SELECT start_ts FROM v_global_start),

-- per-device reference start
ref AS (
  SELECT d.device_id,
         COALESCE(f.first_seen, (SELECT start_ts FROM gs)) AS ref_start
  FROM v_devices d
  LEFT JOIN v_first_seen f USING (device_id)
),

-- last fully completed bucket with 10s grace, aligned to device phase
bounds AS (
  SELECT
    r.device_id,
    r.ref_start,
    p.sec,
    p.iv,
    time_bucket(p.iv, now() - interval '10 seconds', r.ref_start) AS cutoff_bucket
  FROM ref r CROSS JOIN params p
),

-- expected = # fully elapsed device-phased intervals since ref_start up to cutoff
calc AS (
  SELECT
    b.device_id,
    b.ref_start,
    b.sec,
    b.iv,
    b.cutoff_bucket,
    GREATEST(
      0,
      FLOOR(EXTRACT(EPOCH FROM (b.cutoff_bucket - b.ref_start)) / b.sec)
    )::bigint AS expected_total
  FROM bounds b
)

SELECT
  c.device_id,
  c.expected_total,

  -- actual = # distinct buckets with at least one sample (capped 1 per interval),
  -- counted strictly after ref_start and up to cutoff bucket
  COUNT(DISTINCT tb.bucket)::bigint AS actual_total,

  CASE
    WHEN c.expected_total = 0 THEN 0.0
    ELSE ROUND(100.0 * COUNT(DISTINCT tb.bucket) / c.expected_total, 2)
  END AS availability_pct

FROM calc c
LEFT JOIN LATERAL (
  SELECT time_bucket(c.iv, s.timestamp, c.ref_start) AS bucket
  FROM sensor_data s
  WHERE s.device_id = c.device_id
    AND s.timestamp > c.ref_start
    AND time_bucket(c.iv, s.timestamp, c.ref_start) <= c.cutoff_bucket
) tb ON TRUE
GROUP BY c.device_id, c.expected_total
ORDER BY c.device_id;


-- ===== Per-sensor actual counts & availability (since start) =====
-- We count non-null values per sensor column per device and normalise by expected_total.
CREATE OR REPLACE VIEW v_counts_since_start_by_device_and_sensor AS
WITH params AS (
  SELECT
    interval_seconds::int AS sec,
    (interval '1 second') * interval_seconds::int AS iv
  FROM v_params
),
gs AS (SELECT start_ts FROM v_global_start),

ref AS (
  SELECT d.device_id,
         COALESCE(f.first_seen, (SELECT start_ts FROM gs)) AS ref_start
  FROM v_devices d
  LEFT JOIN v_first_seen f USING (device_id)
),
bounds AS (
  SELECT
    r.device_id,
    r.ref_start,
    p.sec,
    p.iv,
    time_bucket(p.iv, now() - interval '10 seconds', r.ref_start) AS cutoff_bucket
  FROM ref r CROSS JOIN params p
),
expected AS (
  SELECT
    b.device_id,
    GREATEST(
      0,
      FLOOR(EXTRACT(EPOCH FROM (b.cutoff_bucket - b.ref_start)) / b.sec)
    )::bigint AS expected_total,
    b.iv,
    b.ref_start,
    b.cutoff_bucket
  FROM bounds b
),
-- helper to time-bucket and cap to 1 per interval for a column
bucketed AS (
  SELECT
    s.device_id,
    'temperature'::text AS sensor,
    time_bucket(e.iv, s.timestamp, e.ref_start) AS bucket
  FROM sensor_data s
  JOIN expected e USING (device_id)
  WHERE s.temperature IS NOT NULL
    AND s.timestamp > e.ref_start
    AND time_bucket(e.iv, s.timestamp, e.ref_start) <= e.cutoff_bucket
  UNION ALL
  SELECT
    s.device_id,
    'humidity' AS sensor,
    time_bucket(e.iv, s.timestamp, e.ref_start) AS bucket
  FROM sensor_data s
  JOIN expected e USING (device_id)
  WHERE s.humidity IS NOT NULL
    AND s.timestamp > e.ref_start
    AND time_bucket(e.iv, s.timestamp, e.ref_start) <= e.cutoff_bucket
  UNION ALL
  SELECT
    s.device_id,
    'pollen' AS sensor,
    time_bucket(e.iv, s.timestamp, e.ref_start) AS bucket
  FROM sensor_data s
  JOIN expected e USING (device_id)
  WHERE s.pollen IS NOT NULL
    AND s.timestamp > e.ref_start
    AND time_bucket(e.iv, s.timestamp, e.ref_start) <= e.cutoff_bucket
  UNION ALL
  SELECT
    s.device_id,
    'particulate_matter' AS sensor,
    time_bucket(e.iv, s.timestamp, e.ref_start) AS bucket
  FROM sensor_data s
  JOIN expected e USING (device_id)
  WHERE s.particulate_matter IS NOT NULL
    AND s.timestamp > e.ref_start
    AND time_bucket(e.iv, s.timestamp, e.ref_start) <= e.cutoff_bucket
),
agg AS (
  SELECT device_id, sensor, COUNT(DISTINCT bucket)::bigint AS actual_count
  FROM bucketed
  GROUP BY device_id, sensor
)

SELECT
  e.device_id,
  s.sensor,
  e.expected_total,
  COALESCE(a.actual_count, 0) AS actual_count,
  CASE
    WHEN e.expected_total = 0 THEN 0.0
    ELSE ROUND(100.0 * COALESCE(a.actual_count, 0) / e.expected_total, 2)
  END AS availability_pct
FROM expected e
CROSS JOIN (VALUES ('temperature'), ('humidity'), ('pollen'), ('particulate_matter')) AS s(sensor)
LEFT JOIN agg a ON a.device_id = e.device_id AND a.sensor = s.sensor
ORDER BY e.device_id, s.sensor;


-- ===== Gaps > 10 minutes (since start) =====
CREATE OR REPLACE VIEW v_sensor_gaps AS
WITH gs AS (SELECT start_ts FROM v_global_start),
-- internal gaps between measurement points
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
-- Head gap: from global start until the first measurement (or until now if never sent)
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
-- Tail gap: from last measurement until now
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
# Grafana Alerting - Arduino Offline

This document describes how the alerting for offline arduino works and how to configure it in Grafana for this project.

## Components
- sensor-exporter (./sensor-exporter/exporter.py) — exposes metric `sensor_seconds_since_last_data{device_id="<id>"}`
  - exporter polls DB every 15s and sets a Gauge per device.
  - exporter must use timezone-aware datetimes (UTC) so delays are correct.
- Prometheus (monitoring/prometheus/prometheus.yml) — scrapes exporter every 15s.
- Grafana — evaluates alert rules and sends email via SMTP contact point.

## Metric to monitor
- Name: `sensor_seconds_since_last_data`
- Label: `device_id`
- Meaning: seconds since the last DB timestamp for that device.

## Required conifguration
- Prometheus scrape interval: 15s (monitoring/prometheus/prometheus.yml).
- Grafana SMTP env in `.env`:
  - GF_SMTP_HOST, GF_SMTP_USER, GF_SMTP_PASSWORD, GF_SMTP_FROM (in docker-compose mapped to GF_SMTP_FROM_ADDRESS), GF_SMTP_FROM_NAME
- Docker Compose mounts (optional): provisioning folders for Grafana datasource / alerting if you want infra-as-code.

## Create Grafana Contact Point (Email)
1. Login Grafana: http://localhost:3003 (admin from `.env`).
2. Alerting → Contact points → New contact point.
3. Type: Email. Add recipient(s).
4. Save → Send test to verify SMTP/auth works.
5. If test fails, check Grafana logs:
   - ```docker compose logs -f grafana```

## Create Alert Rule (Grafana UI)
1. Alerting → Rules → New rule.
2. Data source: Prometheus.
3. Query (example):
   - A: sensor_seconds_since_last_data{job="sensor_exporter"} OR
   - A: sensor_seconds_since_last_data{device_id=~".+"}
   - Click "Run query" — you should see one series per device_id.
4. Condition:
   - WHEN last() OF A IS ABOVE 120
   - For: 2m
   - Evaluate every: 1m
   - No data / Error handling: choose "Alert" if you want missing metrics to trigger.
5. Notifications: select the Email contact point created earlier.
6. Message template examples:
   - Title: Sensor {{ $labels.device_id }} is offline
   - Message: Sensor {{ $labels.device_id }} last seen {{ $value }} seconds ago.

## Troubleshooting
- Status "Pending": condition is true but not yet true for the full "For" duration OR evaluation frequency is too low. Increase evaluation frequency or wait for For duration.
- No email:
  - Check Grafana logs: docker compose logs -f grafana
  - Verify SMTP host/port, credentials and TLS settings. GF_SMTP_HOST may include :465 for SMTPS.
  - Remove quotes around GF_SMTP_PASSWORD in `.env` if present.
- Query returns no series:
  - Confirm exporter is reachable: http://localhost:9100/metrics
  - Confirm Prometheus scraping: http://localhost:9090/targets
  - Confirm exporter sets `device_id` label.
- Incorrect delays:
  - Ensure exporter uses timezone-aware UTC timestamps (exporter.py already uses datetime.now(timezone.utc) and adjusts DB timestamps).

  ## Useful commands (project root, macOS)
- Start / rebuild services:
  - ```docker compose up -d --build grafana prometheus sensor-exporter```
- Follow logs:
  - ```docker compose logs -f grafana```
  - ```docker compose logs -f prometheus```
  - ```docker compose logs -f sensor-exporter```
- Inspect Prometheus:
  - http://localhost:9090/targets
  - http://localhost:9090/graph
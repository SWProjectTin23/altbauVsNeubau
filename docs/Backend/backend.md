## Backend Overview

This backend powers the AltbauVsNeubau project. It consists of:

- API service (Flask + Flask-RESTful) exposing endpoints consumed by the frontend
- MQTT ingester that validates sensor messages and writes metrics to the database
- Database access layer (PostgreSQL/TimescaleDB) and alerting support
- Structured logging and error handling

Key components in the repository:
- API app entry: [`backend/run.py`](../../backend/run.py), [`backend/api/__init__.py`](../../backend/api/__init__.py)
- MQTT ingester: [`backend/mqtt_client/main_ingester.py`](../../backend/mqtt_client/main_ingester.py)
- MQTT/DB config: [`backend/mqtt_client/mqtt_config.py`](../../backend/mqtt_client/mqtt_config.py)
- Common logging: [`backend/common/logging_setup.py`](../../backend/common/logging_setup.py)
- Common exceptions: [`backend/common/exceptions.py`](../../backend/common/exceptions.py)
- Database helpers: [`backend/api/db/`](../../backend/api/db/)
- Dependencies: [`backend/requirements.txt`](../../backend/requirements.txt)

---

## API Service

In [`backend/api/__init__.py`](../../backend/api/__init__.py) the Flask app is created with `create_app` and routes are also registered in the same file. Default dev port is 5001 (see [`backend/run.py`](../../backend/run.py)).

CORS is enabled for specific origins to allow the frontend to call the API.

### Endpoints

| Method | Path | Purpose | Handler | DB layer |
|---|---|---|---|---|
| GET | `/api/devices/<device_id>/data` | Time-series data for device; optional `start`, `end`, `metric` | [`DeviceData`](../../backend/api/device_data.py) | [`get_device_data_from_db`](../../backend/api/db/device_data.py) |
| GET | `/api/range` | Earliest/latest timestamps per device | [`TimeRange`](../../backend/api/range.py) | [`get_all_device_time_ranges_from_db`](../../backend/api/db/time_ranges.py) |
| GET | `/api/devices/<device_id>/latest` | Latest datapoint for device | [`DeviceLatest`](../../backend/api/device_latest.py) | [`get_latest_device_data_from_db`](../../backend/api/db/device_latest.py) |
| GET | `/api/comparison` | Compare two devices over time; `metric`, `device_1`, `device_2`, optional `start`, `end`, `buckets` | [`Comparison`](../../backend/api/comparison.py) | [`compare_devices_over_time`](../../backend/api/db/comparison.py) |
| GET | `/api/thresholds` | Read thresholds | [`Thresholds`](../../backend/api/thresholds.py) | [`get_thresholds_from_db`](../../backend/api/db/thresholds.py) |
| POST | `/api/thresholds` | Update thresholds | [`Thresholds`](../../backend/api/thresholds.py) | [`update_thresholds_in_db`](../../backend/api/db/thresholds.py) |
| GET | `/api/alert_email` | Get configured alert email | [`AlertEmail`](../../backend/api/alertMail.py) | [`get_alert_email`](../../backend/api/db/alertMail.py) |
| POST | `/api/alert_email` | Set alert email (sends confirmation mail) | [`AlertEmail`](../../backend/api/alertMail.py) | [`set_alert_email`](../../backend/api/db/alertMail.py) |
| POST | `/api/confirm_email` | Confirm alert email with token | [`ConfirmEmail`](../../backend/api/confirm_mail.py) | Uses [`get_db_connection`](../../backend/api/db/connection.py) |
| POST | `/api/send_alert_mail` | Send threshold alert mail and manage cooldown | [`SendAlertMail`](../../backend/api/sendAlertMail.py) | [`is_alert_active`/`set_alert_active`/`reset_alert`](../../backend/api/db/sendAlertMail.py) |
| GET | `/health` | Health check | In `create_app` | — |

Additional API docs:
- High-level API notes: [`docs/Backend/api.md`](./api.md)
- Alerts and thresholds: [`docs/Backend/alerts.md`](./alerts.md), [`docs/Backend/thresholds_alerting.md`](./thresholds_alerting.md)

---

## MQTT Ingestion

The ingester subscribes to sensor topics, validates messages, maps them to metrics, and writes to the DB.

- Transport/topic parsing and JSON decoding: [`backend/mqtt_client/main_ingester.py`](../../backend/mqtt_client/main_ingester.py)
- Payload validation and DB writes: [`backend/mqtt_client/handler.py`](../../backend/mqtt_client/handler.py), [`backend/mqtt_client/db_writer.py`](../../backend/mqtt_client/db_writer.py)
- Configuration (env variables): [`backend/mqtt_client/mqtt_config.py`](../../backend/mqtt_client/mqtt_config.py)
- Detailed ingestion documentation: [`docs/Backend/mqtt.md`](./mqtt.md)

Expected topic format, payload schema, metric mapping, and error handling are described in `mqtt.md` and implemented across the files above.

---

## Database Layer

The API uses a thin DB layer under `backend/api/db/` with consistent error mapping and structured logging.

- Connection and config checks: [`connection.py`](../../backend/api/db/connection.py)
- Validation helpers: [`validation.py`](../../backend/api/db/validation.py)
- Devices: [`devices.py`](../../backend/api/db/devices.py)
- Time ranges: [`time_ranges.py`](../../backend/api/db/time_ranges.py)
- Device data: [`device_data.py`](../../backend/api/db/device_data.py)
- Latest data: [`device_latest.py`](../../backend/api/db/device_latest.py)
- Comparison/aggregation: [`comparison.py`](../../backend/api/db/comparison.py)
- Thresholds CRUD: [`thresholds.py`](../../backend/api/db/thresholds.py)
- Alert email storage/cooldowns: [`alertMail.py`](../../backend/api/db/alertMail.py), [`sendAlertMail.py`](../../backend/api/db/sendAlertMail.py)
- Row serialization: [`serialization.py`](../../backend/api/db/serialization.py)

Schema and initialization:
- DB schema overview: [`docs/DB/db.md`](../DB/db.md)
- Init scripts: [`db/init.sql`](../../db/init.sql), availability helper: [`db/availability_sensor.sql`](../../db/availability_sensor.sql)
- ADR: TimescaleDB decision: [`docs/adr/0008-use-timescaledb-for-db.md`](../adr/0008-use-timescaledb-for-db.md)

---

## Logging and Error Handling

- Structured JSON logging via Loguru sink: [`backend/common/logging_setup.py`](../../backend/common/logging_setup.py)
- Unified exceptions for API, DB, MQTT, and ingestion domains: [`backend/common/exceptions.py`](../../backend/common/exceptions.py)
- Operational logging and monitoring decisions: [`docs/software-quality/logging-monitoring.md`](../software-quality/logging-monitoring.md), [`docs/software-quality/logging.md`](../software-quality/logging.md)

---

## Configuration

Configuration is sourced from environment variables. Notable keys:

- Database: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (see [`connection.py`](../../backend/api/db/connection.py))
- MQTT: `MQTT_BROKER`, `MQTT_PORT`, optional `MQTT_BROKER_BACKUP`, `MQTT_PORT_BACKUP`, `MQTT_BASE_TOPIC`, `MQTT_QOS` (see [`mqtt_config.py`](../../backend/mqtt_client/mqtt_config.py))
- Alert mail (Grafana SMTP relays): `GF_SMTP_HOST`, `GF_SMTP_USER`, `GF_SMTP_PASSWORD`, `GF_SMTP_FROM`, `GF_SMTP_FROM_NAME` (see [`sendAlertMail.py`](../../backend/api/sendAlertMail.py))
- Frontend URL for confirmation links: `FRONTEND_URL` (see [`alertMail.py`](../../backend/api/alertMail.py))

`.env` is supported locally by the MQTT ingester; containers typically use environment variables (see `USE_DOTENV` in [`mqtt_config.py`](../../backend/mqtt_client/mqtt_config.py)).

---

## Running and Deployment

- Local dev API: `python backend/run.py` (listens on port 5001 by default)
- Docker images:
  - API service Dockerfile: [`backend/Dockerfile.api`](../../backend/Dockerfile.api)
  - MQTT ingester Dockerfile: [`backend/Dockerfile.mqtt`](../../backend/Dockerfile.mqtt)

---

## Testing

Backend tests live under [`backend/tests/`](../../backend/tests/). See also [`docs/Backend/tests.md`](./tests.md).

---

## Related Documentation

- Frontend overview: [`docs/Frontend/frontend.md`](../Frontend/frontend.md)
- Backend API notes: [`docs/Backend/api.md`](./api.md)
- MQTT ingestion: [`docs/Backend/mqtt.md`](./mqtt.md)
- Alerts and thresholds: [`docs/Backend/alerts.md`](./alerts.md), [`docs/Backend/thresholds_alerting.md`](./thresholds_alerting.md)
- Architecture diagrams: [`docs/architecture/`](../architecture/), images under [`docs/images/`](../images/)
- ADRs (decisions): [`docs/adr/`](../adr/)


# Logging Specification

Lightweight baseline (v0)
*No code usage in this document; this is a format/operational spec.*

---

## 1. Purpose & Scope

Establish a **uniform, structured logging standard** so that:

* All services emit machine-parsable logs with the **same core fields**.
* Containers write **JSON to stdout** (ready for later centralization).
* Each service can add **domain-specific fields** without breaking the baseline.

---

## 2. Operating Principles

* **Single format:** JSON only, written to **stdout** from every container.
* **Single baseline:** Common required fields across all services.
* **Per-service extensions:** Add fields that fit the domain (API, MQTT ingestor, backend).
* **Event names:** Short, stable, `snake_case` (e.g., `request_ok`, `msg_processed`).
* **Durations:** When an event represents an operation, include `duration_ms` (elapsed time in milliseconds).
* **Keep payloads out:** Log identifiers, sizes, and reasons. Not full raw payloads for security reasons.

---

## 3. Unified JSON Schema (Baseline)

Every log line **must** include these keys:

| Field         | Type   | Description                                                  |
| ------------- | ------ | ------------------------------------------------------------ |
| `timestamp`   | string | ISO-8601 UTC (`YYYY-MM-DDTHH:mm:ss.sssZ`).                   |
| `level`       | string | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` \| `CRITICAL`.     |
| `service`     | string | Logical service name: `api`, `ingestor`, …                   |
| `module`      | string | Component or source within the service.                      |
| `event`       | string | Short event name (not a prose sentence), e.g., `request_ok`. |
| `env`         | string | Deployment environment: `dev` \| `staging` \| `prod`.        |
| `duration_ms` | number | **When applicable**: elapsed time of the operation (ms).     |

**Duration definition:** Time between the operation’s start and end (e.g., request handling, message processing, DB write), recorded in **milliseconds**.

---

## 4. Per-Service Extensions (Examples)

### 4.1 API (Flask)

Add:

* `request_id` — Correlates a request across components.
* `method` — HTTP method.
* `path` — Request path.
* `status_code` — HTTP status code.

**Example**

```json
{
  "timestamp": "2025-08-12T14:35:12.512Z",
  "level": "INFO",
  "service": "api",
  "module": "routes",
  "event": "request_ok",
  "env": "staging",
  "request_id": "abc123",
  "method": "GET",
  "path": "/api/devices",
  "status_code": 200,
  "duration_ms": 25
}
```

### 4.2 MQTT Ingestor

Use domain-specific fields (no HTTP status code):

* `device_id` — Sensor/device identifier.
* `metric` — e.g., `temperature`, `humidity`, `pollen`.
* `msg_ts` — Sensor message timestamp (ISO-8601 or epoch).
* `payload_size` — Size in bytes of the received payload.
* `result` — `ok` | `failed`.
* `reason` — Short reason on warnings/errors (e.g., `min_max_check`, `schema_mismatch`).
* `error_type` — Exception/failure type (on errors).
* (Optional) `qos`, `broker` for connection lifecycle events.

**Examples**

```json
{
  "timestamp": "2025-08-12T14:36:00.101Z",
  "level": "INFO",
  "service": "ingestor",
  "module": "handler",
  "event": "msg_processed",
  "env": "prod",
  "device_id": 1,
  "metric": "temperature",
  "msg_ts": "2025-08-12T14:35:59.900Z",
  "payload_size": 128,
  "result": "ok",
  "duration_ms": 7
}
```

```json
{
  "timestamp": "2025-08-12T14:36:05.003Z",
  "level": "WARNING",
  "service": "ingestor",
  "module": "validator",
  "event": "value_out_of_range",
  "env": "prod",
  "device_id": 1,
  "metric": "temperature",
  "result": "failed",
  "reason": "min_max_check",
  "payload_size": 124
}
```

---

## 5. Logging Event Reference (Minimal Set)

**API**

* `request_ok` (INFO): successful request completed.
* `validation_failed` (WARNING): client-side validation issue.
* `unhandled_exception` (ERROR): unexpected server-side error.

**Ingestor**

* `mqtt_connected` / `mqtt_reconnected` / `mqtt_disconnected` (INFO).
* `msg_processed` (INFO): message parsed/handled successfully.
* `value_out_of_range` (WARNING): domain validation failed.
* `db_write_failed` (ERROR): persistence failed.

---

## 6. Payload Policy

* **Do not log raw payloads** in production logs.
* Log **identifiers and metadata** instead: `payload_size`, `device_id`, `metric`, `reason`, and (when relevant) `invalid_payload_file`.
* **Invalid payload storage (local file):**

  * Store the full invalid payload in `/var/log/app/invalid_payloads/` (mounted volume).
  * File naming: timestamp + stable identifier (e.g., `2025-08-12T14-36-05Z_req-abc123.json`).
  * In the log entry, include the path as `invalid_payload_file` so incidents can be correlated without embedding the payload.
  * Apply lifecycle management (e.g., delete files older than 7 days) and restrict access.
* **Development-only exception:** In non-production environments, truncated snippets (first N characters) may be captured for debugging. Avoid in shared/staging/prod.

# Backend Logging & Exceptions (API & MQTT)

## 1.Overview

### Logging

- Emit one JSON log line per event to stdout (Docker).

- A single sink is installed once per process; all modules share it.

- Verbosity is controlled only by the environment variable LOG_LEVEL (DEBUG|INFO|WARNING|ERROR|CRITICAL, default INFO).

- Each module gets a bound logger via setup_logger(service, module) and writes events with log_event(...).

- Use DurationTimer to add duration_ms for timings (for operation).

### Exceptions

- A unified application error model so higher layers never see driver-specific exceptions (e.g., psycopg2).

- DB code maps low-level errors to our exception types (e.g., DatabaseQueryTimeoutError).

- API code translates those exceptions into HTTP responses and logs them.

- MQTT/ingestion code uses dedicated ingest and MQTT error types for structured logging and handling.

---

## 2. Logging: Types & Usage
### What gets logged (JSON fields)

Each log line contains: 
  - timestamp, level, service, module, message (short event code), env
  - plus your extra fields (e.g., device_id, metric, duration_ms, error_type, error_code, details)

### Use in any module (API or MQTT)
```python
from common.logging_setup import setup_logger, log_event, DurationTimer

logger = setup_logger(service="api", module="device_data")  # or service="mqtt", module="ingester"

t = DurationTimer().start()
log_event(logger, "INFO", "device_data.start", device_id=1)

# ... do the work ...
log_event(logger, "INFO", "device_data.ok", device_id=1, row_count=123, duration_ms=t.stop_ms())
```

### Example JSON log lines

**Success**
```json
{
  "timestamp": "2025-08-15T10:12:03.112Z",
  "level": "INFO",
  "service": "api",
  "module": "device_data",
  "message": "device_data.ok",
  "env": "dev",
  "device_id": 7,
  "row_count": 123,
  "duration_ms": 24
}
```

**Error** : db timeout for example
```json
{
  "timestamp": "2025-08-15T10:12:05.551Z",
  "level": "ERROR",
  "service": "api",
  "module": "device_data",
  "message": "device_data.db_query_timeout",
  "env": "dev",
  "error_type": "DatabaseQueryTimeoutError",
  "error_code": "DB_QUERY_TIMEOUT",
  "details": {"op":"get_device_data","device_id":7}
}
```

---

## 3. Exceptions: Types & Usage

### Exception Tree

```
AppError
├─ ApiError (HTTP)
│  ├─ ValidationError (400)
│  └─ NotFoundError   (404)
├─ DatabaseError (non-HTTP)
│  ├─ DatabaseConnectionError   [error_code="DB_CONN_FAIL"]
│  ├─ DatabaseTimeoutError      [error_code="DB_TIMEOUT"]
│  ├─ DatabaseQueryTimeoutError [error_code="DB_QUERY_TIMEOUT"]
│  └─ DatabaseOperationalError  [error_code="DB_OPERATIONAL_ERROR"]
├─ MQTTError (non-HTTP)
│  ├─ MQTTConnectionError [error_code="MQTT_CONN_FAIL"]
│  └─ MQTTTimeoutError    [error_code="MQTT_TIMEOUT"]
└─ IngestError (non-HTTP)
   ├─ PayloadValidationError  [error_code="PAYLOAD_INVALID"]
   ├─ UnknownMetricError      [error_code="UNKNOWN_METRIC"]
   ├─ NonNumericMetricError   [error_code="NON_NUMERIC_VALUE"]
   └─ MetricOutOfRangeError   [error_code="VALUE_OUT_OF_RANGE"]
```

### By Category

**HTTP**

* `ApiError(message, status_code, details?)`

  * `ValidationError` → **400**
  * `NotFoundError` → **404**

**Non-HTTP (all inherit from `AppError`)**

* **DatabaseError**

  * `DatabaseConnectionError` — `DB_CONN_FAIL`
  * `DatabaseTimeoutError` — `DB_TIMEOUT`
  * `DatabaseQueryTimeoutError` — `DB_QUERY_TIMEOUT`
  * `DatabaseOperationalError` — `DB_OPERATIONAL_ERROR`
* **MQTTError**

  * `MQTTConnectionError` — `MQTT_CONN_FAIL`
  * `MQTTTimeoutError` — `MQTT_TIMEOUT`
* **IngestError**

  * `PayloadValidationError` — `PAYLOAD_INVALID`
  * `UnknownMetricError` — `UNKNOWN_METRIC`
  * `NonNumericMetricError` — `NON_NUMERIC_VALUE`
  * `MetricOutOfRangeError` — `VALUE_OUT_OF_RANGE`

**Core Base**

* `AppError(message, error_code?, details?)`
  Provides `to_log_fields()` → `{"error_type","error_code?","details?"}` for structured logging.





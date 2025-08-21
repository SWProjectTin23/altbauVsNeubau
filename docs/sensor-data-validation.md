## Sensor data validation (MQTT ingestion)

This document summarizes how incoming MQTT messages are validated and written to the database by the ingester.

### Topic format
- Expected: `dhbw/ai/si2023/<group>/<sensor-type>/<sensor-id>`
- Example: `dhbw/ai/si2023/01/temperature/01`
- Mapping to metric (from `backend/mqtt_client/main_ingester.py`):
  - `ikea/01` → `pollen`
  - `ikea/02` → `particulate_matter`
  - `temperature/01` → `temperature`
- If the topic has too few segments or no mapping exists, the message is skipped and a warning log with reason `schema_mismatch` is emitted.

### Payload schema
- JSON body example:
```json
{
  "value": 22.5,
  "timestamp": "1722945600",
  "meta": { "device_id": 1 }
}
```
- Required fields:
  - `meta.device_id` (integer, positive)
  - `timestamp` (epoch seconds as string/integer; must parse to an integer)
  - `value` (numeric)
- Failures emit a warning log with reason `schema_mismatch` and the message is skipped.

### Metric handling and value types
- Supported metrics and ranges (inclusive):
  - `temperature`: 1–40 (float allowed)
  - `humidity`: 1–100 (float allowed)
  - `pollen`: 1–700 (integer only; `12.0` is accepted and cast to `12`, `12.3` is rejected)
  - `particulate_matter`: 1–700 (integer only; `12.0` ok, `12.3` rejected)
- Non-numeric `value` → warning with reason `schema_mismatch`.
- Out-of-range `value` → warning with reason `min_max_check`.

### Timestamp normalization
- The `timestamp` is parsed from epoch seconds to a `datetime` and logged in ISO-8601 UTC `...Z` format.

### Database write behavior
- Only the current metric is passed to the DB; other fields are `None` for this write.
- `insert_sensor_data` performs an upsert with `COALESCE`, preserving existing values when `None` is provided.
- On success, a single info log `msg_processed` is emitted.

### Error mapping (DB)
- Transient/driver messages containing "timeout/timed out" → `DatabaseTimeoutError` → error log `db_write_failed` with reason `timeout`.
- Generic DB failures → `DatabaseError` → error log `db_write_failed` with reason `db_error`.
- Rollback errors are swallowed; the original DB error mapping is preserved.

### Examples
- Valid temperature message:
```json
{"value": 23.4, "timestamp": "1722945600", "meta": {"device_id": 2}}
```
- Invalid value type (rejected):
```json
{"value": "NaN", "timestamp": "1722945600", "meta": {"device_id": 2}}
```
- Invalid range (rejected):
```json
{"value": 1000, "timestamp": "1722945600", "meta": {"device_id": 2}}
```
- Integer metric with non-integer float (rejected):
```json
{"value": 12.3, "timestamp": "1722945600", "meta": {"device_id": 2}}
```

### Responsibilities: main_ingester vs handler
- `backend/mqtt_client/main_ingester.py` (transport-layer checks)
  - Validate/parse topic: check segment count; map `<sensor-type>/<sensor-id>` to a supported metric.
  - Decode JSON: if decoding fails, skip the message and log WARNING with reason `schema_mismatch`.
  - Pass `topic` and decoded `payload` to the handler for domain validation and persistence.

- `backend/mqtt_client/handler.py` (domain validation and persistence)
  - Parse and validate required payload fields: `meta.device_id`, `timestamp`, `value`.
  - Type and range rules:
    - Floating-point metrics (`temperature`, `humidity`) accept floats and must be within range.
    - Integer metrics (`pollen`, `particulate_matter`) accept values like `12.0` (cast to `12`) but reject `12.3`; must be within range.
  - Timestamp normalization: epoch → `datetime`; logs use ISO-8601 UTC.
  - Database write: write only the current metric; pass `None` for others so DB-side `COALESCE` preserves previous values.
  - Error mapping and logging: map driver/timeout errors to domain errors and emit structured logs; rollback failures are swallowed while preserving the original error mapping.

### Related implementation files
- Topic/JSON validation and routing: `backend/mqtt_client/main_ingester.py`
- Payload parsing, type/range validation, DB write: `backend/mqtt_client/handler.py`
- Upsert/COALESCE details: `backend/mqtt_client/db_writer.py`

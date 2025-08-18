# mqtt_client/handler.py
# All comments in this file are in English by requirement.

from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from mqtt_client.db_writer import insert_sensor_data
from common.logging_setup import setup_logger, log_event, DurationTimer
from common.exceptions import (
    AppError,
    PayloadValidationError,
    UnknownMetricError,
    NonNumericMetricError,
    MetricOutOfRangeError,
    DatabaseTimeoutError,
    DatabaseError,
    to_log_fields,
)

# Bind a logger for this module; every log line carries service/module/env automatically.
logger = setup_logger(service="ingester", module="handler")

# Allowed ranges for each metric (inclusive).
VALID_RANGES = {
    "temperature": (10, 40),
    "humidity": (00, 100),
    "pollen": (10, 700),
    "particulate_matter": (10, 700),
}


# ---------- Helpers ----------

def _iso_utc(dt: datetime) -> str:
    """Return ISO-8601 UTC string with 'Z' suffix (seconds precision is enough)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


# ---------- Keep original API (minimal changes) ----------

def parse_payload(payload: Dict[str, Any]) -> Tuple[int, datetime, Any]:
    """
    Extract device_id, timestamp (as datetime), and value from payload dict.
    Raise domain-specific ingestion errors instead of logging here.
    """
    try:
        value = payload.get("value")
        timestamp_str = payload.get("timestamp")
        meta = payload.get("meta", {})
        device_id = meta.get("device_id")

        missing = []
        if device_id is None:
            missing.append("device_id")
        if timestamp_str is None:
            missing.append("timestamp")
        else:
            try:
            # Original code used epoch seconds (string) → datetime
                timestamp = datetime.fromtimestamp(int(timestamp_str))
            except Exception as e:
                raise PayloadValidationError("invalid timestamp", details={"timestamp": timestamp_str}) from e
        if value is None:
            missing.append("value")
        if missing:
            raise PayloadValidationError("missing required fields", details={"missing": missing})

        return device_id, timestamp, value

    except AppError:
        # Bubble known ingestion errors unchanged
        raise
    except Exception as e:
        # Wrap any unexpected parsing issue
        raise PayloadValidationError("payload parsing failed", details={"error": str(e)[:120]}) from e


def handle_metric(metric_name: str, topic: str, payload_dict: Dict[str, Any], db_conn) -> None:
    """
    Validate and write the metric value into the database.
    Emit v0-compliant structured logs (JSON to stdout) here.
    """
    t = DurationTimer().start()

    try:
        # Parse payload
        device_id, timestamp, value = parse_payload(payload_dict)

        # Map metric name to database column
        metric_map = {
            "temperature": "temperature",
            "humidity": "humidity",
            "pollen": "pollen",
            "particulate_matter": "particulate_matter",
        }
        if metric_name not in metric_map:
            raise UnknownMetricError(f"Unknown metric: {metric_name}")

        # Prepare data for insertion
        insert_kwargs = {
            "device_id": device_id,
            "timestamp": timestamp,
            metric_map[metric_name]: value,
        }

        # Insert into the database
        insert_sensor_data(db_conn, **insert_kwargs)

        # 4) Success log (single JSON line, v0 fields)
        log_event(
            logger,
            "INFO",
            "msg_processed",
            duration_ms=t.stop_ms(),
            result="ok",
            device_id=device_id,
            metric=metric_name,
            msg_ts=_iso_utc(timestamp),
            topic=topic,
        )

    # ---- Ingestion/domain validation failures (Warning) ----
    except (PayloadValidationError, UnknownMetricError, NonNumericMetricError, MetricOutOfRangeError) as e:
        # Map reason: range issues -> min_max_check; others -> schema_mismatch
        code = getattr(e, "error_code", "")
        reason = "min_max_check" if code == "VALUE_OUT_OF_RANGE" else "schema_mismatch"

        log_event(
            logger,
            "WARNING",
            "value_out_of_range",
            duration_ms=t.stop_ms(),
            result="failed",
            reason=reason,
            device_id=payload_dict.get("meta", {}).get("device_id"),
            metric=metric_name,
            msg_ts=str(payload_dict.get("timestamp")),
            topic=topic,
            **to_log_fields(e),  # adds error_type / error_code / details
        )

    # ---- DB failures (Error) ----
    except DatabaseTimeoutError as e:
        log_event(
            logger,
            "ERROR",
            "db_write_failed",
            duration_ms=t.stop_ms(),
            result="failed",
            reason="timeout",
            device_id=payload_dict.get("meta", {}).get("device_id"),
            metric=metric_name,
            msg_ts=str(payload_dict.get("timestamp")),
            topic=topic,
            **to_log_fields(e),
        )

    except DatabaseError as e:
        log_event(
            logger,
            "ERROR",
            "db_write_failed",
            duration_ms=t.stop_ms(),
            result="failed",
            reason="db_error",
            device_id=payload_dict.get("meta", {}).get("device_id"),
            metric=metric_name,
            msg_ts=str(payload_dict.get("timestamp")),
            topic=topic,
            **to_log_fields(e),
        )

    # ---- Unknown/unexpected (Error) ----
    except Exception as e:
        log_event(
            logger,
            "ERROR",
            "unhandled_exception",
            duration_ms=t.stop_ms(),
            result="failed",
            reason="unexpected",
            device_id=payload_dict.get("meta", {}).get("device_id"),
            metric=metric_name,
            msg_ts=str(payload_dict.get("timestamp")),
            topic=topic,
            **to_log_fields(e),
        )

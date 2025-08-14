import os
import sys
import json
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict, Optional
from loguru import logger as _logger


# ---------- Time helpers ----------

def _utc_now_iso_ms() -> str:
    """
    Returns current UTC time in ISO-8601 with millisecond precision and 'Z' suffix.
    Example: 2025-08-12T14:36:05.003Z
    """
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


# ---------- JSON sink for Loguru ----------

def _json_sink(message):
    """
    Custom sink that converts Loguru records into the exact v0 JSON line format.
    Writes one JSON object per line to stdout.
    """
    record = message.record

    # Baseline fields required by v0 spec
    payload: Dict[str, Any] = {
        "timestamp": _utc_now_iso_ms(),
        "level": record["level"].name,
        "service": record["extra"].get("service"),
        "module": record["extra"].get("module"),
        # v0 uses `message` as short event name (snake_case), not a prose sentence
        "message": record["extra"].get("event") or record["message"],
        "env": record["extra"].get("env", "dev"),
    }

    # duration_ms is optional: include only when provided
    if "duration_ms" in record["extra"] and record["extra"]["duration_ms"] is not None:
        try:
            payload["duration_ms"] = int(record["extra"]["duration_ms"])
        except Exception:
            # If a non-int sneaks in, omit to keep schema clean
            pass

    # Merge domain-specific fields from `extra` while avoiding baseline keys
    baseline_keys = {"service", "module", "env", "event", "duration_ms"}
    for k, v in record["extra"].items():
        if k in baseline_keys:
            continue
        if v is None or v == "":
            continue
        payload[k] = v

    print(json.dumps(payload, ensure_ascii=False), file=sys.stdout)


# ---------- Public API ----------

def setup_logger(service: str, module: str, env: Optional[str] = None, level: str = "INFO"):
    """
    Configure Loguru to emit v0-compliant JSON logs to stdout.
    Returns a bound logger which already carries `service`, `module`, and `env`.

    - service: logical service name, e.g., "ingester" or "api"
    - module: source component within the service, e.g., "handler" or "routes"
    - env: "dev" | "staging" | "prod" (default reads APP_ENV or falls back to "dev")
    - level: minimal level to emit (default "INFO")
    """
    if env is None:
        env = os.getenv("APP_ENV", "dev")

    # Remove default Loguru handler and add our JSON sink
    _logger.remove()
    _logger.add(
        _json_sink,
        level=level.upper(),
        backtrace=False,   # keep output minimal and stable
        diagnose=False,    # avoid dumping internals
        enqueue=False,     # direct stdout write; set True if you need cross-process safety
    )

    # Bind baseline context so every log line contains service/module/env
    return _logger.bind(service=service, module=module, env=env)


def log_event(
    logger,
    level: str,
    event: str,
    *,
    duration_ms: Optional[int] = None,
    **fields: Any,
) -> None:
    """
    Emit a single v0-compliant event.

    - level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL"
    - event: short, stable snake_case code (e.g., "msg_processed")
    - duration_ms: optional elapsed time in milliseconds (int)
    - **fields: domain-specific extension fields (e.g., device_id, metric, msg_ts, payload_size, result, reason, error_type, qos, broker)
    """
    # Attach event and duration; other fields go as domain extensions
    bound = logger.bind(event=event, duration_ms=duration_ms, **fields)

    lvl = level.upper()
    if lvl == "DEBUG":
        bound.debug(event)
    elif lvl == "INFO":
        bound.info(event)
    elif lvl == "WARNING":
        bound.warning(event)
    elif lvl == "ERROR":
        bound.error(event)
    elif lvl == "CRITICAL":
        bound.critical(event)
    else:
        bound.info(event)


# ---------- Utilities for duration & invalid payload policy ----------

class DurationTimer:
    """
    Lightweight operation timer to produce duration_ms according to the v0 spec.
    Usage:
        t = DurationTimer().start()
        ... do work ...
        ms = t.stop_ms()
    """
    def __init__(self):
        self._t0 = None

    def start(self):
        self._t0 = perf_counter()
        return self

    def stop_ms(self) -> int:
        if self._t0 is None:
            return 0
        return int((perf_counter() - self._t0) * 1000)


def save_invalid_payload(base_dir: str, file_stem: str, data: bytes) -> str:
    """
    Persist the full invalid payload to a mounted volume as per v0 spec.
    - base_dir: e.g., "/var/log/app/invalid_payloads"
    - file_stem: use timestamp + stable identifier; avoid user-controlled strings
    - data: raw bytes to save (UTF-8 JSON is typical but not enforced here)
    Returns the absolute file path.
    """
    os.makedirs(base_dir, exist_ok=True)
    safe_stem = "".join(c for c in file_stem if c.isalnum() or c in ("-", "_"))
    path = os.path.join(base_dir, f"{safe_stem}.json")
    with open(path, "wb") as f:
        f.write(data)
    return path

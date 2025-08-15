# common/logging_setup.py
import os
import sys
import json
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict, Optional
from loguru import logger as _logger

# ---------- helpers ----------
def _utc_now_iso_ms() -> str:
    """
    Returns current UTC time in ISO-8601 with millisecond precision and 'Z' suffix.
    Example: 2025-08-12T14:36:05.003Z
    """
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


# ---------- JSON sink for Loguru ----------

def _json_sink(message):
    """
    Convert each Loguru record to one JSON line (v0 style) and write to stdout.
    """
    record = message.record
    payload: Dict[str, Any] = {
        "timestamp": _utc_now_iso_ms(),
        "level": record["level"].name,
        "service": record["extra"].get("service"),
        "module": record["extra"].get("module"),
        "message": record["extra"].get("event") or record["message"],  # short event code
        "env": record["extra"].get("env", "dev"),
    }
    # merge extra fields (skip baseline keys)
    baseline = {"service", "module", "env", "event"}
    for k, v in record["extra"].items():
        if k in baseline or v in (None, ""):
            continue
        payload[k] = v
    print(json.dumps(payload, ensure_ascii=False, default=str), file=sys.stdout)

_LEVELS = {"DEBUG": "DEBUG", "INFO": "INFO", "WARNING": "WARNING", "ERROR": "ERROR", "CRITICAL": "CRITICAL"}
_sink_installed = False  # guard: install sink only once

def _ensure_sink_installed(default_level: str):
    """
    Install the JSON sink. Log level is read from LOG_LEVEL (env).
    """
    global _sink_installed
    if _sink_installed:
        return
    level = os.getenv("LOG_LEVEL", default_level).upper()
    level = _LEVELS.get(level, "INFO")

    _logger.remove()  # remove any default handlers
    _logger.add(
        _json_sink,
        level=level,        # single global threshold from env
        backtrace=False,
        diagnose=False,
        enqueue=False,
    )
    _sink_installed = True

# ---------- public API ----------
def setup_logger(service: str, module: str, env: Optional[str] = None, level: str = "INFO"):
    """
    Return a bound logger. Sink is installed once globally with level from LOG_LEVEL.
    """
    if env is None:
        env = os.getenv("APP_ENV", "dev")
    _ensure_sink_installed(default_level=level)
    return _logger.bind(service=service, module=module, env=env)

def log_event(logger, level: str, event: str, *, duration_ms: Optional[int] = None, **fields: Any) -> None:
    """
    Emit one structured log event (JSON).
    """
    bound = logger.bind(event=event, duration_ms=duration_ms, **fields)

    lvl = level.upper()
    if   lvl == "DEBUG":    bound.debug(event)
    elif lvl == "INFO":     bound.info(event)
    elif lvl == "WARNING":  bound.warning(event)
    elif lvl == "ERROR":    bound.error(event)
    elif lvl == "CRITICAL": bound.critical(event)
    else:                   bound.info(event)

class DurationTimer:
    """
    Simple timer to compute duration_ms.
    """
    def __init__(self): self._t0 = None
    def start(self): self._t0 = perf_counter(); return self
    def stop_ms(self) -> int:
        if self._t0 is None: return 0
        return int((perf_counter() - self._t0) * 1000)

def save_invalid_payload(base_dir: str, file_stem: str, data: bytes) -> str:
    """
    Keep for compatibility. Saves payload bytes to a file (optional to use).
    """
    os.makedirs(base_dir, exist_ok=True)
    safe_stem = "".join(c for c in file_stem if c.isalnum() or c in ("-", "_"))
    path = os.path.join(base_dir, f"{safe_stem}.json")
    with open(path, "wb") as f:
        f.write(data)
    return path

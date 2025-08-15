# mqtt_client/mqtt_config.py
from dotenv import load_dotenv
import os
from pathlib import Path

# structured logging
from common.logging_setup import setup_logger, log_event

logger = setup_logger(service="mqtt", module="mqtt_config")

# --- load .env ---
env_path = Path(__file__).resolve().parents[2] / ".env"

# Heuristics: running in a container?
IN_DOCKER = os.path.exists("/.dockerenv") or os.getenv("CONTAINER") == "1"
# Allow explicit override, e.g., USE_DOTENV=1 in local dev
USE_DOTENV = os.getenv("USE_DOTENV", "0" if IN_DOCKER else "1") == "1"

if USE_DOTENV:
    if env_path.exists():
        # Note: python-dotenv does NOT override already-set env vars by default.
        load_dotenv(dotenv_path=env_path)
        log_event(logger, "INFO", "config.env_loaded", path=str(env_path), source="dotenv")
    else:
        # Missing .env only matters if we explicitly wanted to use dotenv.
        log_event(logger, "DEBUG", "config.env_file_absent", path=str(env_path), note="skipping dotenv; not found")
else:
    # In containers or when explicitly disabled, skip dotenv silently.
    log_event(logger, "DEBUG", "config.env_skip", reason="container_or_disabled")


# Function to get required environment variable or raise an error
def required(key: str) -> str:
    """
    Read a required environment variable.
    Logs a structured error when missing and raises RuntimeError.
    Never logs values, only the key name.
    """
    value = os.getenv(key)
    if value is None:
        log_event(logger, "ERROR", "config.missing_key", key=key)
        raise RuntimeError(f"Environment variable {key} is missing")
    # noisy at DEBUG only
    log_event(logger, "DEBUG", "config.key_loaded", key=key)
    return value


# --- MQTT configuration ---
MQTT_BROKER = required("MQTT_BROKER")
MQTT_PORT = int(required("MQTT_PORT"))
MQTT_BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC", "dhbw/ai/si2023/01")
QOS = int(os.getenv("MQTT_QOS", "1"))

log_event(
    logger, "INFO", "mqtt.config.loaded",
    broker=MQTT_BROKER, port=MQTT_PORT, base_topic=MQTT_BASE_TOPIC, qos=QOS
)


# --- Database configuration ---
DB_HOST = required("DB_HOST")
DB_PORT = int(required("DB_PORT"))
DB_NAME = required("DB_NAME")
DB_USER = required("DB_USER")
DB_PASSWORD = required("DB_PASSWORD")  # NEVER log secrets

log_event(
    logger, "INFO", "db.config.loaded",
    host=DB_HOST, port=DB_PORT, name=DB_NAME, user=DB_USER
)


#  a sanitized view useful for debugging endpoints or health checks
def public_config() -> dict:
    """
    Return a sanitized config snapshot (no secrets).
    """
    return {
        "mqtt": {
            "broker": MQTT_BROKER,
            "port": MQTT_PORT,
            "base_topic": MQTT_BASE_TOPIC,
            "qos": QOS,
        },
        "db": {
            "host": DB_HOST,
            "port": DB_PORT,
            "name": DB_NAME,
            "user": DB_USER,
        },
    }

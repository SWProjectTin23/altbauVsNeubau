from dotenv import load_dotenv
import os
from pathlib import Path
import logging

# mqtt_client.mqtt_config
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path(__file__).resolve().parents[2] / ".env"
if not env_path.exists():
    logger.error(".env file not found at: %s", env_path)
else:
    logger.info("Loading environment variables from: %s", env_path)
load_dotenv(dotenv_path=env_path)

# Function to get required environment variable or raise an error
def required(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        logger.error("Missing required environment variable: %s", key)
        raise RuntimeError(f"Environment variable {key} is missing")
    logger.debug("Loaded required env: %s", key)
    return value

# MQTT configuration
MQTT_BROKER = required("MQTT_BROKER")
MQTT_PORT = int(required("MQTT_PORT"))
logger.info("MQTT configuration loaded: MQTT broker=%s, port=%d", MQTT_BROKER, MQTT_PORT)
MQTT_BASE_TOPIC="dhbw/ai/si2023/01"
QOS = 1

# Database configuration
DB_HOST = required("DB_HOST")
DB_PORT = int(required("DB_PORT"))
DB_NAME = required("DB_NAME")
DB_USER = required("DB_USER")
DB_PASSWORD = required("DB_PASSWORD")
logger.info(
    "Database configuration loaded: host=%s, port=%s, name=%s, user=%s",
    DB_HOST, DB_PORT, DB_NAME, DB_USER
)
# Never log secret var
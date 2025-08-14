from dotenv import load_dotenv
import os
from pathlib import Path
import logging
from exceptions import MQTTError

# mqtt_client.mqtt_config
logger = logging.getLogger(__name__)

load_dotenv()

# Function to get required environment variable or raise an error
def required(key: str) -> str:
    v = os.getenv(key)
    if v is None:
        raise MQTTError(f"Missing environment variable: {key}")
    return v

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
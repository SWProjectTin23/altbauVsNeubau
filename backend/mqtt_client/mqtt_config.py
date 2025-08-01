from dotenv import load_dotenv
import os

load_dotenv()

def required(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"Environment variable {key} is missing")
    return value

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(required("MQTT_PORT"))
MQTT_BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC")
QOS = 1

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(required("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

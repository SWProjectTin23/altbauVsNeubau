import time
import json
import os
from dotenv import load_dotenv
import threading
from prometheus_client import start_http_server, Gauge
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from common.logging_setup import setup_logger, log_event
from pathlib import Path

load_dotenv(dotenv_path=str(Path(__file__).resolve().parents[1] / ".env"))
logger = setup_logger(service="exporter", module="sensor_exporter")

sensor_delay = Gauge(
    'sensor_seconds_since_last_data',
    'Seconds since last sensor value',
    ['device_id']
)

MQTT_BROKER = os.getenv("MQTT_BROKER", "isd-gerold.de")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC", "dhbw/ai/si2023/01")
QOS = int(os.getenv("MQTT_QOS", "1"))   

last_seen = {}

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        device_id = str(payload.get("meta", {}).get("device_id"))
        if device_id is None or device_id == "None":
            log_event(logger, "WARNING", "mqtt.device_id_missing", topic=msg.topic)
            return
        last_seen[device_id] = datetime.now(timezone.utc)
        log_event(logger, "INFO", "mqtt.payload.received", device_id=device_id, topic=msg.topic)
    except Exception as e:
        log_event(logger, "ERROR", "mqtt.payload.decode_failed", error_msg=str(e)[:120], topic=msg.topic)
        return

def mqtt_thread():
    client = mqtt.Client()
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        log_event(logger, "INFO", "mqtt.connected", broker=MQTT_BROKER, port=MQTT_PORT)
    except Exception as e:
        log_event(logger, "ERROR", "mqtt.connect_failed", error_msg=str(e)[:120], broker=MQTT_BROKER, port=MQTT_PORT)
        return
    client.subscribe(f"{MQTT_BASE_TOPIC}/+/+", QOS)
    log_event(logger, "INFO", "mqtt.subscribed", topic=f"{MQTT_BASE_TOPIC}/+/+", qos=QOS)
    client.loop_forever()

def metrics_loop():
    while True:
        now = datetime.now(timezone.utc)
        for device_id, ts in last_seen.items():
            delay = (now - ts).total_seconds()
            sensor_delay.labels(device_id=device_id).set(delay)
            log_event(logger, "DEBUG", "metrics.sensor_delay_set", device_id=device_id, delay=delay)
        time.sleep(5)

if __name__ == '__main__':
    start_http_server(9100)
    log_event(logger, "INFO", "exporter.start", msg="Exporter listening on port 9100")

    threading.Thread(target=mqtt_thread, daemon=True).start()
    metrics_loop()
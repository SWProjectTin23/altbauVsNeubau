from prometheus_client import Gauge, start_http_server
from backend.common.logging_setup import setup_logger, log_event, DurationTimer
from backend.common.exceptions import (
    MQTTConnectionError, PayloadValidationError, to_log_fields
)
from dotenv import load_dotenv
import time
import os
import json
import threading
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

logger = setup_logger(service="monitoring", module="exporter")

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

sensor_delay = Gauge(
    'sensor_seconds_since_last_data',
    'Seconds since last sensor value',
    ['device_id', 'sensor_type']
)

SENSOR_MAP = {
    ("ikea", "01"): "pollen",
    ("ikea", "02"): "particulate_matter",
}

MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_BROKER_BACKUP = os.getenv('MQTT_BROKER_BACKUP', 'localhost')
MQTT_PORT_BACKUP = int(os.getenv('MQTT_PORT_BACKUP', '1884'))
MQTT_BASE_TOPIC = os.getenv('MQTT_BASE_TOPIC', 'dhbw/ai/si2023/01')

last_seen = {}

def on_connect(client, _userdata, _flags, rc):
    try:
        if rc != 0:
            raise MQTTConnectionError("MQTT connect failed", details={"rc": rc, "broker": client._host, "port": client._port})
        log_event(
            logger, "INFO", "mqtt_connected",
            broker=client._host, port=client._port, rc=rc
        )
        client.subscribe(f"{MQTT_BASE_TOPIC}/+/+", qos=1)
    except MQTTConnectionError as e:
        log_event(logger, "ERROR", "mqtt_connect_error", **to_log_fields(e))

def on_message(_client, _userdata, msg):
    t = DurationTimer().start()
    try:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            raise PayloadValidationError("Invalid JSON payload", details={"topic": msg.topic, "raw": msg.payload[:120]})

        meta = payload.get("meta", {})
        device_id = str(meta.get("device_id"))
        topic_parts = msg.topic.split("/")
        sensor_type = topic_parts[-2] if len(topic_parts) >= 2 else "unknown"
        sensor_id = topic_parts[-1] if len(topic_parts) >= 1 else "unknown"
        sensor_type_mapped = SENSOR_MAP.get((sensor_type, sensor_id), sensor_type)
        timestamp = payload.get("timestamp")
        value = payload.get("value")
        if not device_id or not sensor_type_mapped:
            raise PayloadValidationError("Missing device_id or sensor_type", details={"topic": msg.topic, "payload": payload})

        if timestamp is not None:
            ts = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
        else:
            ts = datetime.now(timezone.utc)

        last_seen[(device_id, sensor_type_mapped)] = ts
        log_event(
            logger, "INFO", "sensor_data_received",
            duration_ms=t.stop_ms(),
            device_id=device_id,
            sensor_type=sensor_type_mapped,
            topic=msg.topic,
            value=value,
            msg_ts=ts.isoformat(),
        )
    except PayloadValidationError as e:
        log_event(
            logger, "ERROR", "sensor_data_parse_failed",
            duration_ms=t.stop_ms(),
            topic=msg.topic,
            **to_log_fields(e)
        )
    except Exception as e:
        log_event(
            logger, "ERROR", "sensor_data_parse_failed",
            duration_ms=t.stop_ms(),
            topic=msg.topic,
            error_type=type(e).__name__,
            error_msg=str(e)[:120]
        )

def mqtt_loop(broker, port):
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.loop_forever()
    except Exception as e:
        log_event(logger, "ERROR", "mqtt_loop_error", **to_log_fields(e), broker=broker, port=port)

if __name__ == '__main__':
    start_http_server(9100)
    log_event(logger, "INFO", "exporter_started", port=9100)
    threading.Thread(target=mqtt_loop, args=(MQTT_BROKER, MQTT_PORT), daemon=True).start()
    threading.Thread(target=mqtt_loop, args=(MQTT_BROKER_BACKUP, MQTT_PORT_BACKUP), daemon=True).start()

    while True:
        now = datetime.now(timezone.utc)
        for (device_id, sensor_type), ts in last_seen.items():
            delay = (now - ts).total_seconds()
            if delay < 0:
                log_event(
                    logger, "INFO", "negative_delay",
                    device_id=device_id,
                    sensor_type=sensor_type,
                    delay=delay,
                    msg_ts=ts.isoformat()
                )
                delay = 0
            sensor_delay.labels(device_id=device_id, sensor_type=sensor_type).set(delay)
            log_event(
                logger, "INFO", "sensor_delay_updated",
                device_id=device_id,
                sensor_type=sensor_type,
                delay=delay,
                msg_ts=ts.isoformat()
            )
        time.sleep(15)
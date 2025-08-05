import paho.mqtt.client as mqtt
import json
from mqtt_config import MQTT_BROKER, MQTT_PORT, MQTT_BASE_TOPIC, QOS
from handler import handle_metric
import logging
from logging_setup import setup_logging

logger = logging.getLogger(__name__)


# Metric mapping from topic suffix to database column
metric_map = {
    'ikea': {
        '01': 'pollen',
        '02': 'particulate_matter',
    },
    'temperature': {
        '01': 'temperature',
    },
    # future mappings
    # 'humidity': '?',
}

# MQTT connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker.")
        client.subscribe(f"{MQTT_BASE_TOPIC}/+/+", QOS)
    else:
        logger.error("MQTT connection failed. Code=%s", rc)

# MQTT message callback
def on_message(client, userdata, msg):
    db_conn = userdata.get("db_connection")
    topic_parts = msg.topic.split("/")
    if len(topic_parts) < 6:
        logger.warning("Unexpected topic format: %s", msg.topic)
        return

    # Beispiel-Topic: dhbw/ai/si2023/<group>/<sensor-type>/<sensor-id>
    sensor_type = topic_parts[-2]
    sensor_id = topic_parts[-1]
    metric_name = metric_map.get(sensor_type, {}).get(sensor_id)
    if not metric_name:
        logger.warning(
            "Unknown metric mapping: sensor_type=%s, sensor_id=%s, topic=%s", sensor_type, sensor_id, msg.topic
        )
        return

    try:
        payload = json.loads(msg.payload.decode())
        handle_metric(metric_name, msg.topic, payload, db_conn)
    except Exception as e:
        logger.error("Failed to process message from topic=%s: %s", msg.topic, str(e))

# Database connection helper
def connect_db():
    import psycopg2
    from mqtt_config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        conn.autocommit = False
        logger.info("Connected to database: host=%s, db=%s", DB_HOST, DB_NAME)
        return conn
    except Exception as e:
        logger.error("Failed to connect to database: %s", str(e))
        return None

# Main entry point
if __name__ == "__main__":
    setup_logging()  # initalize logging
    logger.info("Launching MQTT ingester...")

    db_connection = connect_db()
    if not db_connection:
        logger.critical("Database connection failed. Exiting.")
        exit(1)

    client = mqtt.Client(userdata={"db_connection": db_connection})
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        if db_connection:
            db_connection.close()
            logger.info("Database connection closed.")

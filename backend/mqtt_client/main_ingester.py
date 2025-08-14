import paho.mqtt.client as mqtt
import json
import psycopg2
from mqtt_client.mqtt_config import MQTT_BROKER, MQTT_PORT, MQTT_BASE_TOPIC, QOS, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
from mqtt_client.handler import handle_metric
import logging
from logging_configure import configure_logging
from exceptions import (
    AppError,
    ValidationError,
    DatabaseError,
    DatabaseConnectionError,
    MQTTConnectionError,
)

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

    # Process the payload
    try:
        payload = json.loads(msg.payload.decode())
        handle_metric(metric_name, msg.topic, payload, db_conn)

    # Handle specific exceptions
    except ValidationError as e:
        logger.warning("MQTT ValidationError topic=%s: %s", msg.topic, str(e))

    # Handle database errors
    except DatabaseError as e:
        logger.error("MQTT DatabaseError topic=%s: %s", msg.topic, str(e))

    # Handle application errors
    except AppError as e:
        logger.error("MQTT AppError topic=%s type=%s: %s", msg.topic, e.__class__.__name__, str(e))

    # Handle exceptions
    except Exception:
        logger.exception("MQTT Unhandled exception topic=%s", msg.topic)


# Database connection helper
def connect_db():
    """
    Connect to the PostgreSQL database.
    """

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        conn.autocommit = False
        return conn
    except psycopg2.OperationalError as e:
        raise DatabaseConnectionError(f"Failed to connect to database: {e}")
    except psycopg2.Error as e:
        raise DatabaseError(e.pgerror or f"Unexpected database error: {e}")


# Main entry point
if __name__ == "__main__":
    configure_logging(service_name="mqtt")
    logger.info("Launching MQTT ingester...")

    try:
        db_connection = connect_db()
    except AppError as e:
        logger.critical("Startup failed: %s", str(e))
        raise

    # Create MQTT client
    client = mqtt.Client(userdata={"db_connection": db_connection})
    client.on_connect = on_connect
    client.on_message = on_message

    # Start the MQTT client
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception:
        logger.exception("Fatal error in MQTT loop")
        raise
    finally:
        if db_connection:
            db_connection.close()
            logger.info("Database connection closed.")

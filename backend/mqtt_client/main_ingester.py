import json
import psycopg2
import paho.mqtt.client as mqtt

from mqtt_client.mqtt_config import (
    MQTT_BROKER, MQTT_PORT, MQTT_BROKER2, MQTT_PORT2, MQTT_BASE_TOPIC, QOS,
    DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
)
from mqtt_client.handler import handle_metric
from common.logging_setup import setup_logger, log_event

# Structured logger bound to this module/service
logger = setup_logger(service="ingester", module="main_ingester")

# Log the MQTT broker configuration at the start
log_event(
    logger, "INFO", "env_mqtt_broker_config",
    broker_1=MQTT_BROKER, port_1=MQTT_PORT,
    broker_2=MQTT_BROKER2, port_2=MQTT_PORT2
)

# Metric mapping from topic suffix to database column
metric_map = {
    "ikea": {
        "01": "pollen",
        "02": "particulate_matter",
    },
    "temperature": {
        "01": "temperature",
    },
    "humidity": {
        "01": "humidity",
    },
    # future mappings (e.g., "humidity": {...})
}


# ---------------- MQTT callbacks ----------------

def on_connect(client, userdata, flags, rc):
    """Log connection result and subscribe on success."""
    if rc == 0:
        log_event(
            logger, "INFO", "mqtt_connected",
            result="ok", rc=rc, broker=f"{MQTT_BROKER}:{MQTT_PORT}"
        )
        client.subscribe(f"{MQTT_BASE_TOPIC}/+/+", QOS)
    else:
        # Connection failed: treat as MQTT failure (no message processing yet)
        log_event(
            logger, "ERROR", "mqtt_connected",
            result="failed", reason="connect_failed", rc=rc, broker=f"{MQTT_BROKER}:{MQTT_PORT}"
        )


def on_disconnect(client, userdata, rc):
    """Log clean vs unexpected disconnects."""
    level = "INFO" if rc == 0 else "WARNING"
    reason = "clean" if rc == 0 else "unexpected"
    log_event(logger, level, "mqtt_disconnected", rc=rc, reason=reason)


def on_message(client, userdata, msg):
    """
    Parse topic → route to handler. Topic/schema issues are logged here.
    Handler is responsible for structured logging of processing success/failure.
    """
    db_conn = userdata.get("db_connection")
    topic = msg.topic or ""

     # Check if connection is closed (psycopg2: closed==True means unusable)
    if db_conn is None or getattr(db_conn, "closed", True):
        log_event(
            logger, "WARNING", "db_connection_closed",
            result="failed", reason="reconnecting",
            topic=topic
        )
        db_conn = connect_db()
        userdata["db_connection"] = db_conn
        if db_conn is None or getattr(db_conn, "closed", True):
            log_event(
                logger, "ERROR", "db_reconnect_failed",
                result="failed", reason="db_unavailable",
                topic=topic
            )
            return

    # Expect topic like: dhbw/ai/si2023/<group>/<sensor-type>/<sensor-id>
    parts = topic.split("/")
    if len(parts) < 6:
        log_event(
            logger, "WARNING", "value_out_of_range",
            result="failed", reason="schema_mismatch",
            topic=topic, details={"why": "unexpected_topic_format"}
        )
        return

    sensor_type = parts[-2]
    sensor_id = parts[-1]
    metric_name = metric_map.get(sensor_type, {}).get(sensor_id)
    if not metric_name:
        log_event(
            logger, "WARNING", "value_out_of_range",
            result="failed", reason="schema_mismatch",
            topic=topic, details={"sensor_type": sensor_type, "sensor_id": sensor_id, "why": "unknown_metric_mapping"}
        )
        return

    # Decode JSON payload; on failure, log as schema mismatch (ingestion-side issue)
    try:
        payload_dict = json.loads(msg.payload.decode("utf-8"))
    except Exception as e:
        log_event(
            logger, "WARNING", "value_out_of_range",
            result="failed", reason="schema_mismatch",
            topic=topic, error_type=type(e).__name__, error_msg=str(e)[:200]
        )
        return

    # Delegate to handler; it will log success/failure per v0
    try:
        handle_metric(metric_name, topic, payload_dict, db_conn)
    except Exception as e:
        log_event(
            logger, "ERROR", "unhandled_exception",
            result="failed", reason="unexpected",
            topic=topic, error_type=type(e).__name__, error_msg=str(e)[:200]
        )


# ---------------- DB connection helper ----------------

def connect_db():
    """Create a DB connection; emit structured logs for success/failure."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
        )
        conn.autocommit = False
        log_event(
            logger, "INFO", "db_connected",
            result="ok", host=DB_HOST, db=DB_NAME
        )
        return conn
    except Exception as e:
        log_event(
            logger, "ERROR", "db_connect_failed",
            result="failed", reason="connection_error",
            host=DB_HOST, db=DB_NAME, error_type=type(e).__name__, error_msg=str(e)[:200]
        )
        return None


# ---------------- Main entry point ----------------

if __name__ == "__main__":
    log_event(logger, "INFO", "ingester_start", msg="Launching MQTT ingester")

    db_connection = connect_db()
    if not db_connection:
        log_event(logger, "CRITICAL", "ingester_exit", reason="db_unavailable")
        raise SystemExit(1)

    client = mqtt.Client(userdata={"db_connection": db_connection})
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Fallback: try first MQTT broker, then second, with structured logs
    try:
        connected = False
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            log_event(
                logger, "INFO", "mqtt_connect_attempt",
                broker=MQTT_BROKER, port=MQTT_PORT, result="ok"
            )
            connected = True
        except Exception as e:
            log_event(
                logger, "WARNING", "mqtt_connect_attempt",
                broker=MQTT_BROKER, port=MQTT_PORT, result="failed", error_type=type(e).__name__, error_msg=str(e)[:200]
            )
            if MQTT_BROKER2:
                log_event(
                    logger, "INFO", "mqtt_connect_fallback_attempt",
                    broker=MQTT_BROKER2, port=MQTT_PORT2, result="attempt"
                )
                try:
                    client.connect(MQTT_BROKER2, MQTT_PORT2, 60)
                    log_event(
                        logger, "INFO", "mqtt_connect_fallback",
                        broker=MQTT_BROKER2, port=MQTT_PORT2, result="ok"
                    )
                    connected = True
                except Exception as e2:
                    log_event(
                        logger, "WARNING", "mqtt_connect_attempt",
                        broker=MQTT_BROKER2, port=MQTT_PORT2, result="failed", error_type=type(e2).__name__, error_msg=str(e2)[:200]
                    )
                    log_event(
                        logger, "CRITICAL", "mqtt_connect_fallback",
                        broker=MQTT_BROKER2, port=MQTT_PORT2, result="failed", error_type=type(e2).__name__, error_msg=str(e2)[:200]
                    )
            else:
                log_event(
                    logger, "CRITICAL", "mqtt_connect_fallback",
                    broker=None, port=None, result="failed", reason="no_fallback_configured"
                )
        if not connected:
            log_event(logger, "CRITICAL", "ingester_exit", reason="no_mqtt_connection")
            raise SystemExit(1)
        client.loop_forever()
    except KeyboardInterrupt:
        log_event(logger, "INFO", "shutdown_requested")
    finally:
        try:
            if db_connection:
                db_connection.close()
                log_event(logger, "INFO", "db_connection_closed", result="ok")
        except Exception as e:
            log_event(
                logger, "WARNING", "db_connection_closed",
                result="failed", reason="close_failed",
                error_type=type(e).__name__, error_msg=str(e)[:200]
            )

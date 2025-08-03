import paho.mqtt.client as mqtt
import json
from mqtt_config import MQTT_BROKER, MQTT_PORT, MQTT_BASE_TOPIC, QOS
from handler import handle_metric

# Metric mapping from topic suffix to database column
metric_map = {
    '01': 'pollen',
    '02': 'particulate_matter',
    # future mappings
    # 'temperature': 'temperature',
    # 'humidity': '?',
}

# MQTT connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Connected successfully.")
        client.subscribe(f"{MQTT_BASE_TOPIC}/ikea/+", QOS)
    else:
        print(f"[MQTT] Connection failed with code {rc}")

# MQTT message callback
def on_message(client, userdata, msg):
    db_conn = userdata.get("db_connection")
    topic_parts = msg.topic.split("/")
    if len(topic_parts) < 6:
        print(f"[WARN] Unexpected topic: {msg.topic}")
        return

    metric_id = topic_parts[-1]
    metric_name = metric_map.get(metric_id)
    if not metric_name:
        print(f"[WARN] Unknown metric id: {metric_id}")
        return

    try:
        payload = json.loads(msg.payload.decode())
        handle_metric(metric_name, msg.topic, payload, db_conn)
    except Exception as e:
        print(f"[ERROR] Failed to process message: {e}")

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
        print("[DB] Connected to database.")
        return conn
    except Exception as e:
        print(f"[DB ERROR] Could not connect: {e}")
        return None

# Main entry point
if __name__ == "__main__":
    print("[START] Launching MQTT ingester...")
    db_connection = connect_db()
    if not db_connection:
        exit(1)

    client = mqtt.Client(userdata={"db_connection": db_connection})
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("[STOP] Interrupted by user.")
    finally:
        if db_connection:
            db_connection.close()
            print("[CLOSE] DB connection closed.")

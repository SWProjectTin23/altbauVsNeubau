from db_writer import insert_sensor_data
from datetime import datetime

def parse_payload(payload: dict):
    """
    Extract device_id, timestamp (as datetime), and value from payload dict.
    """
    try:
        value = payload.get("value")
        timestamp_str = payload.get("timestamp")
        # meta = payload.get("meta", {})
        # device_id = meta.get("device_id")
        device_id = int(1)



        if device_id is None or timestamp_str is None or value is None:
            raise ValueError("Missing required fields in payload.")

        timestamp = datetime.fromtimestamp(int(timestamp_str))
        return device_id, timestamp, value

    except Exception as e:
        print(f"[PARSER ERROR] Fehler beim Parsen des Payloads: {e}")
        return None, None, None

def handle_metric(metric_name: str, topic: str, payload_dict: dict, db_conn):
    """
    通用 handler，根据 metric_name 写入对应字段。
    """
    device_id, timestamp, value = parse_payload(payload_dict)
    if device_id is None:
        print(f"[{metric_name.upper()}] Ungültiger Payload übersprungen: {payload_dict}")
        return

    kwargs = {metric_name: value}
    insert_sensor_data(db_conn, device_id, timestamp, **kwargs)

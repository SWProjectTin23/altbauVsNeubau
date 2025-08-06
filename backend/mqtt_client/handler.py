from mqtt_client.db_writer import insert_sensor_data
from datetime import datetime

VALID_RANGES = {
    "temperature": (0, 40),
    "humidity": (0, 100),
    "pollen": (0, 700),
    "particulate_matter": (0, 1000)
}


def parse_payload(payload: dict):
    """
    Extract device_id, timestamp (as datetime), and value from payload dict.
    """
    try:
        value = payload.get("value")
        timestamp_str = payload.get("timestamp")
        meta = payload.get("meta", {})
        device_id = meta.get("device_id")

        # Check valid
        if device_id is None or timestamp_str is None or value is None:
            raise ValueError("Missing required fields in payload.")

        timestamp = datetime.fromtimestamp(int(timestamp_str))
        return device_id, timestamp, value

    except Exception as e:
        print(f"[PARSER ERROR] Fehler beim Parsen des Payloads: {e}")
        return None, None, None

def handle_metric(metric_name: str, topic: str, payload_dict: dict, db_conn):
    """
    Write the metric value in db
    """
    device_id, timestamp, value = parse_payload(payload_dict)
    if device_id is None:
        print(f"[{metric_name.upper()}] Ungültiger Payload übersprungen: {payload_dict}")
        return
    
    if metric_name not in VALID_RANGES:
        print("[UNKNOWN_METRIC] Metric is not recognized. Skipping.")
        return

    # Validate value range
    min_val, max_val = VALID_RANGES[metric_name]
    if not isinstance(value, (int, float)):
        print("[INVALID_VALUE_TYPE] Non-numeric value")
        return
    if not (min_val <= value <= max_val):
        print("[OUT_OF_RANGE] Metric value out of range.")
        return


    kwargs = {metric_name: value}
    insert_sensor_data(db_conn, device_id, timestamp, **kwargs)

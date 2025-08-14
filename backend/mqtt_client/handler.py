from mqtt_client.db_writer import insert_sensor_data
from datetime import datetime
import logging
from exceptions import ValidationError, DatabaseError

logger = logging.getLogger(__name__)

VALID_RANGES = {
    "temperature": (0, 40),
    "humidity": (0, 100),
    "pollen": (0, 700),
    "particulate_matter": (0, 1000)
}


def parse_payload(payload: dict):
    """
    Extract device_id, timestamp (as datetime), and value from payload dict.
    Raises ValidationError on invalid payload.
    """
    try:
        value = payload.get("value")
        timestamp_str = payload.get("timestamp")
        meta = payload.get("meta", {})
        device_id = meta.get("device_id")

        if device_id is None or timestamp_str is None or value is None:
            raise ValidationError("Missing required fields: device_id, timestamp, value")

        timestamp = datetime.fromtimestamp(int(timestamp_str))
        return device_id, timestamp, value

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid payload: {e}")


def handle_metric(metric_name: str, topic: str, payload_dict: dict, db_conn):
    """
    Validate and write the metric value into the database.
    Raises ValidationError for bad input and DatabaseError for DB issues.
    """
    device_id, timestamp, value = parse_payload(payload_dict)

    # Metric name validation
    if metric_name not in VALID_RANGES:
        raise ValidationError(f"Unknown metric '{metric_name}'")

    # Value validation
    min_val, max_val = VALID_RANGES[metric_name]
    if not isinstance(value, (int, float)):
        raise ValidationError(f"Non-numeric value for '{metric_name}'")
    if not (min_val <= value <= max_val):
        raise ValidationError(f"Value out of range for '{metric_name}': {value} not in [{min_val}, {max_val}]")

    # Write to DB
    try:
        kwargs = {metric_name: value}
        insert_sensor_data(db_conn, device_id, timestamp, **kwargs)
    except DatabaseError:
        raise
    except Exception as e:
        raise DatabaseError(f"Insert failed: {e}")
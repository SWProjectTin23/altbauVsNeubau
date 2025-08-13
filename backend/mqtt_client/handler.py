from mqtt_client.db_writer import insert_sensor_data
from datetime import datetime
import logging

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
    """
    try:
        value = payload.get("value")
        timestamp_str = payload.get("timestamp")
        meta = payload.get("meta", {})
        device_id = meta.get("device_id")

        # Check valid
        if device_id is None or timestamp_str is None or value is None:
            logger.error("Missing required fields in payload.")
            raise ValueError("Missing required fields in payload.")

        timestamp = datetime.fromtimestamp(int(timestamp_str))
        return device_id, timestamp, value

    except Exception as e:
        logger.error("Parsing payload failed, error=%s.", str(e))
        return None, None, None


def handle_metric(metric_name: str, topic: str, payload_dict: dict, db_conn):
    """
    Validate and write the metric value into the database.
    """
    device_id, timestamp, value = parse_payload(payload_dict)

    # Check device_id exists
    if device_id is None:
        logger.warning(
            "[INVALID_PAYLOAD] device_id missing. Skipping. topic=%s, raw_payload=%s",
            topic, payload_dict
        )
        return
    # Check timestamp exists
    if timestamp is None:
        logger.warning(
            "[INVALID_PAYLOAD] timestamp missing. Skipping. topic=%s, raw_payload=%s",
            topic, payload_dict
        )
        return
    
        # Check if metric is recognized
    if metric_name not in VALID_RANGES:
        logger.warning(
            "[UNKNOWN_METRIC] Metric '%s' is not recognized. Skipping. topic=%s, payload=%s",
            metric_name, topic, payload_dict
        )
        return

    # Validate value range
    min_val, max_val = VALID_RANGES[metric_name]
    if not isinstance(value, (int, float)):
        logger.warning(
            "[INVALID_VALUE_TYPE] Non-numeric value for Metric '%s'. device_id=%s, value=%s, timestamp=%s, raw_payload=%s",
            metric_name, device_id, value, timestamp, payload_dict
        )
        return
    if not (min_val <= value <= max_val):
        logger.warning(
            "[OUT_OF_RANGE] %s value out of range. device_id=%s, value=%s, expected=(%s-%s), timestamp=%s, raw_payload=%s",
            metric_name, device_id, value, min_val, max_val, timestamp, payload_dict
        )
        return

    # Write to DB
    kwargs = {metric_name: value}
    insert_sensor_data(db_conn, device_id, timestamp, **kwargs)
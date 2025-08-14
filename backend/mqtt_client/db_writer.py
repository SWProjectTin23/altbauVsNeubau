from typing import Any, Dict, Optional
from common.exceptions import (
    DatabaseError,
    DatabaseTimeoutError,
    DatabaseConnectionError,
)

def insert_sensor_data(
    conn: Any,
    device_id: int,
    timestamp: Any,  
    *,
    temperature: Optional[float] = None,
    humidity: Optional[float] = None,
    pollen: Optional[int] = None,
    particulate_matter: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Upsert a row into sensor_data.
    - No logging here (logging is done by the caller).
    - On failure: rollback and raise a domain-specific exception.
    - Returns a small summary for the caller to include in logs.
    """
    # Prevent inserting None values: skip fields that are None
    if temperature is None and humidity is None and pollen is None and particulate_matter is None:
        raise DatabaseError("No valid sensor values to insert (all are None)")

    # Build dynamic query and params
    fields = []
    values = []
    updates = []
    if temperature is not None:
        fields.append("temperature")
        values.append(temperature)
        updates.append("temperature = EXCLUDED.temperature")
    if humidity is not None:
        fields.append("humidity")
        values.append(humidity)
        updates.append("humidity = EXCLUDED.humidity")
    if pollen is not None:
        fields.append("pollen")
        values.append(pollen)
        updates.append("pollen = EXCLUDED.pollen")
    if particulate_matter is not None:
        fields.append("particulate_matter")
        values.append(particulate_matter)
        updates.append("particulate_matter = EXCLUDED.particulate_matter")

    insert_query = f"""
    INSERT INTO sensor_data (device_id, timestamp, {', '.join(fields)})
    VALUES (%s, %s, {', '.join(['%s'] * len(fields))})
    ON CONFLICT (device_id, timestamp)
    DO UPDATE SET {', '.join(updates)};
    """

    cursor = conn.cursor()
    try:
        cursor.execute(
            insert_query,
            (device_id, timestamp, *values),
        )
        conn.commit()

        updated_fields: Dict[str, Any] = {k: v for k, v in zip(fields, values)}
        rows_affected = getattr(cursor, "rowcount", 1)

        return {
            "device_id": device_id,
            "timestamp": timestamp,
            "updated_fields": updated_fields,
            "rows_affected": rows_affected,
        }

    except Exception as e:
        # Keep DB consistent
        try:
            conn.rollback()
        except Exception:
            pass

        # Very light classification without driver-specific imports
        msg = str(e).lower()
        if "timeout" in msg or "timed out" in msg:
            raise DatabaseTimeoutError("database write timeout") from e
        if "connect" in msg or "could not connect" in msg:
            raise DatabaseConnectionError("database connection error") from e
        raise DatabaseError("database write failed") from e

    finally:
        try:
            cursor.close()
        except Exception:
            pass

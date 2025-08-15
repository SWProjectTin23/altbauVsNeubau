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
    Insert a row into sensor_data only if all sensor values are provided.
    - No logging here (logging is done by the caller).
    - On failure: rollback and raise a domain-specific exception.
    - Returns a small summary for the caller to include in logs.
    """
    # Prevent inserting None values: skip fields that are None
    if temperature is None or humidity is None or pollen is None or particulate_matter is None:
        raise DatabaseError("Incomplete sensor data: all sensor values must be provided")

    # Build query and params
    insert_query = """
    INSERT INTO sensor_data (device_id, timestamp, temperature, humidity, pollen, particulate_matter)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (device_id, timestamp)
    DO UPDATE SET 
        temperature = EXCLUDED.temperature,
        humidity = EXCLUDED.humidity,
        pollen = EXCLUDED.pollen,
        particulate_matter = EXCLUDED.particulate_matter;
    """

    cursor = conn.cursor()
    try:
        cursor.execute(
            insert_query,
            (device_id, timestamp, temperature, humidity, pollen, particulate_matter),
        )
        conn.commit()

        return {
            "device_id": device_id,
            "timestamp": timestamp,
            "updated_fields": {
                "temperature": temperature,
                "humidity": humidity,
                "pollen": pollen,
                "particulate_matter": particulate_matter,
            },
            "rows_affected": getattr(cursor, "rowcount", 1),
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

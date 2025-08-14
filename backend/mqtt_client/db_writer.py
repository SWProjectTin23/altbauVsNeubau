from typing import Any, Dict, Optional
from exceptions.exceptions import (
    DatabaseError,
    DatabaseTimeoutError,
    DatabaseConnectionError,
)

def insert_sensor_data(
    conn: Any,
    device_id: int,
    timestamp: Any,  # timezone-aware datetime or DB-acceptable type
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
    cursor = conn.cursor()
    try:
        insert_query = """
        INSERT INTO sensor_data (device_id, timestamp, temperature, humidity, pollen, particulate_matter)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (device_id, timestamp)
        DO UPDATE SET
            temperature = COALESCE(EXCLUDED.temperature, sensor_data.temperature),
            humidity = COALESCE(EXCLUDED.humidity, sensor_data.humidity),
            pollen = COALESCE(EXCLUDED.pollen, sensor_data.pollen),
            particulate_matter = COALESCE(EXCLUDED.particulate_matter, sensor_data.particulate_matter);
        """

        cursor.execute(
            insert_query,
            (device_id, timestamp, temperature, humidity, pollen, particulate_matter),
        )
        conn.commit()

        updated_fields: Dict[str, Any] = {}
        if temperature is not None:
            updated_fields["temperature"] = temperature
        if humidity is not None:
            updated_fields["humidity"] = humidity
        if pollen is not None:
            updated_fields["pollen"] = pollen
        if particulate_matter is not None:
            updated_fields["particulate_matter"] = particulate_matter

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

from psycopg2.extensions import QueryCanceledError
from psycopg2 import OperationalError
from psycopg2 import extras
import psycopg2

from common.logging_setup import setup_logger, log_event, DurationTimer
from common.exceptions import (
    DatabaseError,
    DatabaseQueryTimeoutError,
    DatabaseOperationalError,
)
from .connection import get_db_connection
from .serialization import serialize_row


logger = setup_logger(service="api", module="db.device_latest")


def get_latest_device_data_from_db(device_id):
    t = DurationTimer().start()
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT device_id,
                EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT AS unix_timestamp_seconds,
                humidity, temperature, pollen, particulate_matter
                FROM sensor_data
                WHERE device_id = %s
                ORDER BY timestamp DESC
                LIMIT 1;
                """,
                (device_id,),
            )
            row = cursor.fetchone()
            if row:
                row_dict = serialize_row(dict(row))
                payload = {
                    "device_id": row_dict["device_id"],
                    "unix_timestamp_seconds": row_dict["unix_timestamp_seconds"],
                    "humidity": row_dict["humidity"],
                    "temperature": row_dict["temperature"],
                    "pollen": row_dict["pollen"],
                    "particulate_matter": row_dict["particulate_matter"],
                }
                log_event(logger, "INFO", "db.latest.ok", duration_ms=t.stop_ms(), device_id=device_id)
                return payload
            else:
                log_event(logger, "INFO", "db.latest.empty", duration_ms=t.stop_ms(), device_id=device_id)
                return []
    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.latest.timeout", duration_ms=t.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "get_latest_device_data_from_db"}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.latest.operational_error", duration_ms=t.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "get_latest_device_data_from_db"}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.latest.fail", duration_ms=t.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "get_latest_device_data_from_db"}) from e
    finally:
        conn.close()

__all__ = ["get_latest_device_data_from_db"]



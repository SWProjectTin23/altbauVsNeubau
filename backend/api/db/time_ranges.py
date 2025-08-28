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


logger = setup_logger(service="api", module="db.time_ranges")


def get_all_device_time_ranges_from_db():
    t = DurationTimer().start()
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT device_id,
                MIN(EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT) AS start,
                MAX(EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT) AS end
                FROM sensor_data
                GROUP BY device_id
                ORDER BY device_id;
                """
            )
            time_ranges = cursor.fetchall()
            payload = [serialize_row(dict(row)) for row in time_ranges]
            log_event(logger, "INFO", "db.time_ranges.ok", duration_ms=t.stop_ms(), device_count=len(payload))
            return payload
    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.time_ranges.timeout", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "get_all_device_time_ranges_from_db"}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.time_ranges.operational_error", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "get_all_device_time_ranges_from_db"}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.time_ranges.fail", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "get_all_device_time_ranges_from_db"}) from e
    finally:
        conn.close()

__all__ = ["get_all_device_time_ranges_from_db"]



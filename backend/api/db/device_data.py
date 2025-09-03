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


logger = setup_logger(service="api", module="db.device_data")


def get_device_data_from_db(device_id, metric=None, start=None, end=None):
    valid_metrics = ['humidity', 'temperature', 'pollen', 'particulate_matter']
    if metric and metric not in valid_metrics:
        raise ValueError(f"Invalid metric '{metric}'. Valid metrics: {', '.join(valid_metrics)}.")

    base_columns = [
        "device_id",
        "EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT AS unix_timestamp_seconds",
    ]
    select_columns = base_columns + ([metric] if metric else valid_metrics)

    query = f"""
        SELECT {', '.join(select_columns)}
        FROM sensor_data
        WHERE device_id = %s
    """

    params = [device_id]
    conditions = []
    if start:
        conditions.append("timestamp >= TO_TIMESTAMP(%s)::TIMESTAMPTZ")
        params.append(start)
    if end:
        conditions.append("timestamp <= TO_TIMESTAMP(%s)::TIMESTAMPTZ")
        params.append(end)
    if conditions:
        query += " AND " + " AND ".join(conditions)

    t = DurationTimer().start()
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(query, tuple(params))
            data = cursor.fetchall()
            result = [serialize_row(dict(row)) for row in data]
            log_event(logger, "INFO", "db.device_data.ok", duration_ms=t.stop_ms(), device_id=device_id, metric=metric or "ALL", row_count=len(result))
            return result
    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.device_data.timeout", duration_ms=t.stop_ms(), device_id=device_id, metric=metric or "ALL", error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "get_device_data_from_db"}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.device_data.operational_error", duration_ms=t.stop_ms(), device_id=device_id, metric=metric or "ALL", error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "get_device_data_from_db"}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.device_data.fail", duration_ms=t.stop_ms(), device_id=device_id, metric=metric or "ALL", error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "get_device_data_from_db"}) from e
    finally:
        conn.close()



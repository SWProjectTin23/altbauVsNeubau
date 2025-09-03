from psycopg2.extensions import QueryCanceledError
from psycopg2 import OperationalError
import psycopg2

from common.logging_setup import setup_logger, log_event, DurationTimer
from common.exceptions import (
    DatabaseError,
    DatabaseQueryTimeoutError,
    DatabaseOperationalError,
)
from .connection import get_db_connection


logger = setup_logger(service="api", module="db.devices")


def device_exists(device_id):
    t = DurationTimer().start()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM sensor_data WHERE device_id = %s);", (device_id,))
            result = cursor.fetchone()
            exists = result[0] if result is not None else False
            log_event(logger, "INFO", "db.device_exists.ok", duration_ms=t.stop_ms(), device_id=device_id, exists=bool(exists))
            return exists
    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.device_exists.timeout", duration_ms=t.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "device_exists", "device_id": device_id}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.device_exists.operational_error", duration_ms=t.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "device_exists", "device_id": device_id}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.device_exists.fail", duration_ms=t.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "device_exists", "device_id": device_id}) from e
    finally:
        conn.close()



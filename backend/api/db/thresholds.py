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


logger = setup_logger(service="api", module="db.thresholds")


def get_thresholds_from_db():
    t = DurationTimer().start()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute("SELECT * FROM thresholds LIMIT 1;")
        rows = cursor.fetchall()
        payload = [serialize_row(dict(row)) for row in rows]
        log_event(logger, "INFO", "db.thresholds.ok", duration_ms=t.stop_ms(), row_count=len(payload))
        cursor.close()
        return payload
    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.thresholds.timeout", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "get_thresholds_from_db"}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.thresholds.operational_error", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "get_thresholds_from_db"}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.thresholds.fail", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "get_thresholds_from_db"}) from e
    finally:
        if conn:
            conn.close()


def update_thresholds_in_db(threshold_data):
    t = DurationTimer().start()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM thresholds;")
        cur.execute(
            """
            INSERT INTO thresholds (
                temperature_min_hard, temperature_min_soft, temperature_max_soft, temperature_max_hard,
                humidity_min_hard, humidity_min_soft, humidity_max_soft, humidity_max_hard,
                pollen_min_hard, pollen_min_soft, pollen_max_soft, pollen_max_hard,
                particulate_matter_min_hard, particulate_matter_min_soft, particulate_matter_max_soft, particulate_matter_max_hard
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
            """,
            (
                threshold_data['temperature_min_hard'], threshold_data['temperature_min_soft'], threshold_data['temperature_max_soft'], threshold_data['temperature_max_hard'],
                threshold_data['humidity_min_hard'], threshold_data['humidity_min_soft'], threshold_data['humidity_max_soft'], threshold_data['humidity_max_hard'],
                threshold_data['pollen_min_hard'], threshold_data['pollen_min_soft'], threshold_data['pollen_max_soft'], threshold_data['pollen_max_hard'],
                threshold_data['particulate_matter_min_hard'], threshold_data['particulate_matter_min_soft'], threshold_data['particulate_matter_max_soft'], threshold_data['particulate_matter_max_hard']
            ),
        )
        conn.commit()
        cur.close()
        log_event(logger, "INFO", "db.thresholds.update_ok", duration_ms=t.stop_ms())
        return True
    except QueryCanceledError as e:
        if conn:
            conn.rollback()
        log_event(logger, "ERROR", "db.thresholds.update_timeout", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "update_thresholds_in_db"}) from e
    except OperationalError as e:
        if conn:
            conn.rollback()
        log_event(logger, "ERROR", "db.thresholds.update_operational_error", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "update_thresholds_in_db"}) from e
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        log_event(logger, "ERROR", "db.thresholds.update_fail", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "update_thresholds_in_db"}) from e
    finally:
        if conn:
            conn.close()

__all__ = ["get_thresholds_from_db", "update_thresholds_in_db"]



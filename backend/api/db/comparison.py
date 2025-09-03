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


logger = setup_logger(service="api", module="db.comparison")


def compare_devices_over_time(device_id1, device_id2, metric=None, start=None, end=None, num_buckets=None):
    t = DurationTimer().start()
    log_event(logger, "DEBUG", "db.compare.start", device_id1=device_id1, device_id2=device_id2, metric=metric, start=start, end=end, num_buckets=num_buckets)

    if metric not in ['humidity', 'temperature', 'pollen', 'particulate_matter']:
        raise ValueError("Invalid metric. Must be one of: 'humidity', 'temperature', 'pollen', 'particulate_matter'.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)

        count_query = """
            SELECT COUNT(*) FROM sensor_data
            WHERE (device_id = %s OR device_id = %s)
            AND timestamp >= TO_TIMESTAMP(%s) AT TIME ZONE 'UTC'
            AND timestamp <= TO_TIMESTAMP(%s) AT TIME ZONE 'UTC';
            """
        count_params = (device_id1, device_id2, start, end)
        cursor.execute(count_query, count_params)
        count_result = cursor.fetchone()
        total_raw_entries = count_result[0] if count_result is not None else 0

        log_event(logger, "DEBUG", "db.compare.count", total_raw_entries=total_raw_entries, num_buckets=num_buckets)

        if num_buckets is None or num_buckets > total_raw_entries:
            query = f"""
                SELECT device_id,
                EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT AS unix_timestamp_seconds,
                {metric}
                FROM sensor_data
                WHERE device_id IN (%s, %s)
            """
            params = (device_id1, device_id2)
            if start:
                query += " AND timestamp >= TO_TIMESTAMP(%s)::TIMESTAMPTZ"
                params += (start,)
            if end:
                query += " AND timestamp <= TO_TIMESTAMP(%s)::TIMESTAMPTZ"
                params += (end,)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            result = {
                "data": {
                    f"device_{device_id1}": [],
                    f"device_{device_id2}": [],
                },
                "message": None,
                "status": "success",
            }
            for row in rows:
                entry = {
                    "timestamp": int(row["unix_timestamp_seconds"]),
                    "value": float(row[metric]) if row[metric] is not None else None,
                }
                result["data"][f"device_{row['device_id']}"].append(entry)

            if num_buckets is not None and total_raw_entries is not None and num_buckets > total_raw_entries:
                result["message"] = f"Warning: The number of buckets ({num_buckets}) exceeds the total number of raw entries ({total_raw_entries})."

            log_event(logger, "INFO", "db.compare.all_data.ok", duration_ms=t.stop_ms(), device_id1=device_id1, device_id2=device_id2, rows=len(rows), warned=bool(result["message"]))
            cursor.close()
            conn.close()
            return result

        if not start or not end:
            cursor.execute(
                """
                SELECT MIN(EXTRACT(EPOCH FROM timestamp)), MAX(EXTRACT(EPOCH FROM timestamp))
                FROM sensor_data
                WHERE device_id = %s OR device_id = %s
                """,
                (device_id1, device_id2),
            )
            rng = cursor.fetchone()
            if rng is None or rng[0] is None or rng[1] is None:
                cursor.close()
                conn.close()
                raise ValueError("No data found for the specified devices and time range.")
            start, end = rng

        bucket_size = max(1, int((end - start) / num_buckets))

        query = f"""
            SELECT
                device_id,
                FLOOR((EXTRACT(EPOCH FROM timestamp) - %s) / %s) AS bucket,
                MIN(EXTRACT(EPOCH FROM timestamp)) AS bucket_start,
                AVG({metric}) AS avg_value
            FROM sensor_data
            WHERE (device_id = %s OR device_id = %s)
              AND EXTRACT(EPOCH FROM timestamp) >= %s
              AND EXTRACT(EPOCH FROM timestamp) <= %s
            GROUP BY device_id, bucket
            ORDER BY device_id, bucket_start
        """
        params = [start, bucket_size, device_id1, device_id2, start, end]
        cursor.execute(query, params)
        rows = cursor.fetchall()

        result = {
            "data": {
                f"device_{device_id1}": [],
                f"device_{device_id2}": [],
            },
            "message": None,
            "status": "success",
        }
        for row in rows:
            entry = {
                "timestamp": int(row["bucket_start"]),
                "value": float(row["avg_value"]) if row["avg_value"] is not None else None,
            }
            result["data"][f"device_{row['device_id']}"].append(entry)

        if num_buckets > total_raw_entries:
            result["message"] = f"Warning: The number of buckets ({num_buckets}) exceeds the total number of raw entries ({total_raw_entries}). Data may be averaged over larger intervals."

        log_event(
            logger,
            "INFO",
            "db.compare.bucketed.ok",
            duration_ms=t.stop_ms(),
            device_id1=device_id1,
            device_id2=device_id2,
            bucket_size=bucket_size,
            buckets=num_buckets,
            rows=len(rows),
            warned=bool(result["message"]),
        )
        cursor.close()
        conn.close()
        return result
    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.compare.timeout", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "compare_devices_over_time"}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.compare.operational_error", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "compare_devices_over_time"}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.compare.fail", duration_ms=t.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "compare_devices_over_time"}) from e



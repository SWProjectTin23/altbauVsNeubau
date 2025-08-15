# api/db_operations.py

import os
import datetime
from decimal import Decimal

import psycopg2
from psycopg2 import extras
from psycopg2 import OperationalError  # [errors] low-level DB operational failures
from psycopg2.extensions import QueryCanceledError  # [errors] statement timeout / canceled
from dotenv import load_dotenv

# [logging] bring in your log helpers
from common.logging_setup import setup_logger, log_event, DurationTimer
# [errors] unified error types exposed to the rest of the app
from common.exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseQueryTimeoutError,   # new
    DatabaseOperationalError,    # new
)

# [logging] each module registers its own logger
logger = setup_logger(service="api", module="db_operations")

# Load environment variables from the .env file
load_dotenv()

# Database configuration loaded from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432")  # Default to 5432 if not specified
}


# Function to serialize database rows for JSON compatibility
def serialize_row(row: dict) -> dict:
    """Converts Decimal and datetime for JSON compatibility."""
    result = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            result[k] = float(v)
        elif isinstance(v, (datetime.datetime, datetime.date)):
            result[k] = v.isoformat()
        else:
            result[k] = v
    return result


# Check if all required database configuration parameters are set
def check_db_config():
    missing = [k for k in ["host", "database", "user", "password"] if not DB_CONFIG[k]]
    if missing:
        msg = f"Missing DB config values: {', '.join(missing)}. Please check your .env file or environment variables."
        # [logging]
        log_event(logger, "ERROR", "db.config_missing", missing=",".join(missing))
        raise ValueError(msg)


# Function to get a database connection
def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    Returns a Connection object.
    Raises app-level Database* errors on failure.
    """
    check_db_config()

    timer = DurationTimer().start()  # [logging]
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=int(DB_CONFIG["port"])
        )
        # [logging]
        log_event(
            logger, "INFO", "db.conn_ok",
            duration_ms=timer.stop_ms(),
            host=DB_CONFIG["host"], db=DB_CONFIG["database"]
        )
        return conn

    except OperationalError as e:
        # connection-level operational failure
        log_event(
            logger, "ERROR", "db.conn_operational_error",
            duration_ms=timer.stop_ms(),
            host=DB_CONFIG["host"], db=DB_CONFIG["database"], error_type=e.__class__.__name__
        )
        raise DatabaseOperationalError("database operational error", details={"op": "connect"}) from e
    
    except psycopg2.Error as e:
        # other connection failures
        log_event(
            logger, "ERROR", "db.conn_fail",
            duration_ms=timer.stop_ms(),
            host=DB_CONFIG["host"], db=DB_CONFIG["database"], error_type=e.__class__.__name__
        )
        raise DatabaseConnectionError("database connection failed", details={"op": "connect"}) from e


# Check if a device exists in the database
def device_exists(device_id):
    """
    Checks if a device with the given ID exists in the database.
    Returns True if the device exists, False otherwise.
    """
    timer = DurationTimer().start()  # [logging]
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT EXISTS(SELECT 1 FROM sensor_data WHERE device_id = %s);"
            cursor.execute(query, (device_id,))
            result = cursor.fetchone()
            exists = result[0] if result is not None else False
            # [logging]
            log_event(
                logger, "INFO", "db.device_exists.ok",
                duration_ms=timer.stop_ms(),
                device_id=device_id, exists=bool(exists)
            )
            return exists
    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.device_exists.timeout",
                  duration_ms=timer.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "device_exists", "device_id": device_id}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.device_exists.operational_error",
                  duration_ms=timer.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "device_exists", "device_id": device_id}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.device_exists.fail",
                  duration_ms=timer.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "device_exists", "device_id": device_id}) from e
    finally:
        conn.close()


# Get available time ranges for all devices from the database
def get_all_device_time_ranges_from_db():
    """
    Fetches the available time ranges for all devices from the database.
    Returns a list of dictionaries with device_id, start, and end timestamps.
    """
    timer = DurationTimer().start()  # [logging]
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            query = """
                SELECT device_id, 
                MIN(EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT) AS start,
                MAX(EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT) AS end
                FROM sensor_data
                GROUP BY device_id
                ORDER BY device_id;
            """
            cursor.execute(query)
            time_ranges = cursor.fetchall()
            payload = [serialize_row(dict(row)) for row in time_ranges]
            # [logging]
            log_event(
                logger, "INFO", "db.time_ranges.ok",
                duration_ms=timer.stop_ms(),
                device_count=len(payload)
            )
            return payload
    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.time_ranges.timeout",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "get_all_device_time_ranges_from_db"}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.time_ranges.operational_error",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "get_all_device_time_ranges_from_db"}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.time_ranges.fail",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "get_all_device_time_ranges_from_db"}) from e
    finally:
        conn.close()


# Validate timestamps and range for two devices
def validate_timestamps_and_range(device_id1, device_id2, start, end):
    """
    Validates if the provided start and end Unix timestamps are valid
    and within the overlapping available data range for the given devices.

    Returns:
        tuple: (bool, str|None) True if valid, else False + error message.
    """
    # [logging] lightweight input event
    log_event(logger, "DEBUG", "db.validate_range.start",
              device_id1=device_id1, device_id2=device_id2, start=start, end=end)

    if start is None or end is None:
        return False, "Start and end timestamps must be provided."
    
    # Check if start is less than end
    if start >= end:
        return False, "Start timestamp must be less than end timestamp."

    time_ranges = get_all_device_time_ranges_from_db()
    if not time_ranges:
        return False, "No time ranges available for the devices."

    range1 = next((tr for tr in time_ranges if tr['device_id'] == device_id1), None)
    range2 = next((tr for tr in time_ranges if tr['device_id'] == device_id2), None)

    # Check if both devices have valid time ranges
    if not range1 or not range2:
        return False, f"No data found for device ID {device_id1} or {device_id2}."

    # Check if the provided range overlaps with the available data ranges
    if range1['end'] < start or range2['end'] < start:
        return False, "No overlapping data available for the specified time range."

    log_event(logger, "DEBUG", "db.validate_range.ok",
              device_id1=device_id1, device_id2=device_id2)
    return True, None


# Get sensor data by device ID and time range
def get_device_data_from_db(device_id, metric=None, start=None, end=None):
    """
    Fetches sensor data for a specific device within an optional time range.
    If metric is provided, filters by that metric.
    Returns a list of dictionaries with device data.
    """
    valid_metrics = ['humidity', 'temperature', 'pollen', 'particulate_matter']

    if metric and metric not in valid_metrics:
        raise ValueError(f"Invalid metric '{metric}'. Valid metrics: {', '.join(valid_metrics)}.")

    base_columns = [
        "device_id",
        "EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT AS unix_timestamp_seconds"
    ]

    if metric:
        select_columns = base_columns + [metric]
    else:
        select_columns = base_columns + valid_metrics

    query = f"""
        SELECT {', '.join(select_columns)}
        FROM sensor_data
        WHERE device_id = %s
    """

    # Prepare parameters for the query
    params = [device_id]
    conditions = []

    # Add conditions for start and end timestamps if provided
    if start:
        conditions.append("timestamp >= TO_TIMESTAMP(%s)::TIMESTAMPTZ")
        params.append(start)
    if end:
        conditions.append("timestamp <= TO_TIMESTAMP(%s)::TIMESTAMPTZ")
        params.append(end)
    if conditions:
        query += " AND " + " AND ".join(conditions)

    timer = DurationTimer().start()  # [logging]
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(query, tuple(params))
            data = cursor.fetchall()

            result = [serialize_row(dict(row)) for row in data]
            log_event(
                logger, "INFO", "db.device_data.ok",
                duration_ms=timer.stop_ms(),
                device_id=device_id, metric=metric or "ALL", row_count=len(result)
            )
            return result
    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.device_data.timeout",
                  duration_ms=timer.stop_ms(), device_id=device_id, metric=metric or "ALL",
                  error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "get_device_data_from_db"}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.device_data.operational_error",
                  duration_ms=timer.stop_ms(), device_id=device_id, metric=metric or "ALL",
                  error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "get_device_data_from_db"}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.device_data.fail",
                  duration_ms=timer.stop_ms(), device_id=device_id, metric=metric or "ALL",
                  error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "get_device_data_from_db"}) from e
    finally:
        conn.close()


# Get latest data for a device
def get_latest_device_data_from_db(device_id):
    """
    Fetches the latest sensor data for a specific device.
    Returns a dictionary with the latest data or None if no data is found.
    """
    timer = DurationTimer().start()  # [logging]
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:

            # Query to get the latest data for the specified device
            query = """
                SELECT device_id, 
                EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT AS unix_timestamp_seconds,
                humidity, temperature, pollen, particulate_matter
                FROM sensor_data
                WHERE device_id = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """
            cursor.execute(query, (device_id,))
            row = cursor.fetchone()

            if row:
                row_dict = serialize_row(dict(row))
                payload = {
                    "device_id": row_dict["device_id"],
                    "unix_timestamp_seconds": row_dict["unix_timestamp_seconds"],
                    "humidity": row_dict["humidity"],
                    "temperature": row_dict["temperature"],
                    "pollen": row_dict["pollen"],
                    "particulate_matter": row_dict["particulate_matter"]
                }
                log_event(
                    logger, "INFO", "db.latest.ok",
                    duration_ms=timer.stop_ms(),
                    device_id=device_id
                )
                return payload
            else:
                log_event(
                    logger, "INFO", "db.latest.empty",
                    duration_ms=timer.stop_ms(),
                    device_id=device_id
                )
                return []
    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.latest.timeout",
                  duration_ms=timer.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "get_latest_device_data_from_db"}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.latest.operational_error",
                  duration_ms=timer.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "get_latest_device_data_from_db"}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.latest.fail",
                  duration_ms=timer.stop_ms(), device_id=device_id, error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "get_latest_device_data_from_db"}) from e
    finally:
        conn.close()


# Comparison Between Devices over Time Range
def compare_devices_over_time(device_id1, device_id2, metric=None, start=None, end=None, num_buckets=None):
    """
    Compares the specified metric for two devices over a given time range.
    If no metric is specified, compares all metrics.
    Returns a dictionary with the comparison data.
    """
    timer = DurationTimer().start()  # [logging]
    log_event(logger, "DEBUG", "db.compare.start",
              device_id1=device_id1, device_id2=device_id2, metric=metric, start=start, end=end, num_buckets=num_buckets)

    if metric not in ['humidity', 'temperature', 'pollen', 'particulate_matter']:
        raise ValueError("Invalid metric. Must be one of: 'humidity', 'temperature', 'pollen', 'particulate_matter'.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)

    # Count the total number of raw entries for each device in the specified time range
    # This is used to check if num_buckets exceeds the total number of raw entries
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

        log_event(logger, "DEBUG", "db.compare.count",
                  total_raw_entries=total_raw_entries, num_buckets=num_buckets)

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
                    f"device_{device_id2}": []
                },
                "message": None,
                "status": "success"
            }
            for row in rows:
                entry = {
                    "timestamp": int(row["unix_timestamp_seconds"]),
                    "value": float(row[metric]) if row[metric] is not None else None
                }
                result["data"][f"device_{row['device_id']}"].append(entry)

            if num_buckets is not None and total_raw_entries is not None and num_buckets > total_raw_entries:
                result["message"] = f"Warning: The number of buckets ({num_buckets}) exceeds the total number of raw entries ({total_raw_entries})."

            log_event(
                logger, "INFO", "db.compare.all_data.ok",
                duration_ms=timer.stop_ms(),
                device_id1=device_id1, device_id2=device_id2,
                rows=len(rows),
                warned=bool(result["message"])
            )
            cursor.close()
            conn.close()
            return result

        # need start/end if bucketing
        if not start or not end:
            cursor.execute("""
                SELECT MIN(EXTRACT(EPOCH FROM timestamp)), MAX(EXTRACT(EPOCH FROM timestamp))
                FROM sensor_data
                WHERE device_id = %s OR device_id = %s
            """, (device_id1, device_id2))
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
                f"device_{device_id2}": []
            },
            "message": None,
            "status": "success"
        }
        for row in rows:
            entry = {
                "timestamp": int(row["bucket_start"]),
                "value": float(row["avg_value"]) if row["avg_value"] is not None else None
            }
            result["data"][f"device_{row['device_id']}"].append(entry)

        if num_buckets > total_raw_entries:
            result["message"] = f"Warning: The number of buckets ({num_buckets}) exceeds the total number of raw entries ({total_raw_entries}). Data may be averaged over larger intervals."

        log_event(
            logger, "INFO", "db.compare.bucketed.ok",
            duration_ms=timer.stop_ms(),
            device_id1=device_id1, device_id2=device_id2,
            bucket_size=bucket_size, buckets=num_buckets,
            rows=len(rows),
            warned=bool(result["message"])
        )
        cursor.close()
        conn.close()
        return result

    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.compare.timeout",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "compare_devices_over_time"}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.compare.operational_error",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "compare_devices_over_time"}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.compare.fail",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "compare_devices_over_time"}) from e


# GET thresholds from the database
def get_thresholds_from_db():
    """
    Fetches the thresholds for devices from the database.
    Returns a list of dictionaries with threshold data.
    """
    timer = DurationTimer().start()  # [logging]
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)

        query = "SELECT * FROM thresholds LIMIT 1;"
        cursor.execute(query)
        rows = cursor.fetchall()

        payload = [serialize_row(dict(row)) for row in rows]
        log_event(
            logger, "INFO", "db.thresholds.ok",
            duration_ms=timer.stop_ms(),
            row_count=len(payload)
        )
        cursor.close()
        return payload

    except QueryCanceledError as e:
        log_event(logger, "ERROR", "db.thresholds.timeout",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "get_thresholds_from_db"}) from e
    except OperationalError as e:
        log_event(logger, "ERROR", "db.thresholds.operational_error",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "get_thresholds_from_db"}) from e
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.thresholds.fail",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "get_thresholds_from_db"}) from e
    finally:
        if conn:
            conn.close()


# Update thresholds in the database
def update_thresholds_in_db(threshold_data):
    timer = DurationTimer().start()  # [logging]
    conn = None
    try:
        # Get a database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete existing thresholds to ensure only one row remains
        cur.execute("DELETE FROM thresholds;")

        # Insert the new thresholds
        insert_query = """
        INSERT INTO thresholds (
            temperature_min_hard, temperature_min_soft, temperature_max_soft, temperature_max_hard,
            humidity_min_hard, humidity_min_soft, humidity_max_soft, humidity_max_hard,
            pollen_min_hard, pollen_min_soft, pollen_max_soft, pollen_max_hard,
            particulate_matter_min_hard, particulate_matter_min_soft, particulate_matter_max_soft, particulate_matter_max_hard
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
        """

        # Execute the insert query with the provided threshold data
        cur.execute(insert_query, (
            threshold_data['temperature_min_hard'], threshold_data['temperature_min_soft'], threshold_data['temperature_max_soft'], threshold_data['temperature_max_hard'],
            threshold_data['humidity_min_hard'], threshold_data['humidity_min_soft'], threshold_data['humidity_max_soft'], threshold_data['humidity_max_hard'],
            threshold_data['pollen_min_hard'], threshold_data['pollen_min_soft'], threshold_data['pollen_max_soft'], threshold_data['pollen_max_hard'],
            threshold_data['particulate_matter_min_hard'], threshold_data['particulate_matter_min_soft'], threshold_data['particulate_matter_max_soft'], threshold_data['particulate_matter_max_hard']
        ))

        conn.commit()
        cur.close()
        log_event(logger, "INFO", "db.thresholds.update_ok", duration_ms=timer.stop_ms())
        return True

    except QueryCanceledError as e:
        if conn:
            conn.rollback()
        log_event(logger, "ERROR", "db.thresholds.update_timeout",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseQueryTimeoutError("query timeout", details={"op": "update_thresholds_in_db"}) from e
    except OperationalError as e:
        if conn:
            conn.rollback()
        log_event(logger, "ERROR", "db.thresholds.update_operational_error",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseOperationalError("database operational error", details={"op": "update_thresholds_in_db"}) from e
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        log_event(logger, "ERROR", "db.thresholds.update_fail",
                  duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
        raise DatabaseError("database error", details={"op": "update_thresholds_in_db"}) from e
    finally:
        if conn:
            conn.close()

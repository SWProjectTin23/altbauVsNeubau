import psycopg2
from psycopg2 import extras
import os
import datetime
from dotenv import load_dotenv

from decimal import Decimal
from decimal import Decimal

import logging
from exceptions import (
    ValidationError,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseTimeoutError,
)

logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

# Database configuration loaded from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432") # Default to 5432 if not specified
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
        raise DatabaseConnectionError(msg)


# Function to get a database connection
def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    Returns a Connection object.
    Raises psycopg2.Error on connection errors.
    """
    check_db_config()

    # Attempt to connect to the database
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=int(DB_CONFIG["port"]) 
        )
        return conn
    
    # Handle connection errors
    except psycopg2.errors.QueryCanceled as e:
        raise DatabaseTimeoutError("Database connection timed out")
    except psycopg2.OperationalError as e:
        raise DatabaseConnectionError(f"Operational error while connecting to the database: {e}")
    except psycopg2.Error as e:
        raise DatabaseError(e.pgerror or f"Unexpected database error: {e}")
# ...existing code...

# Check if a device exists in the database
def device_exists(device_id):
    """
    Checks if a device with the given ID exists in the database.
    Returns True if the device exists, False otherwise.
    """

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = "SELECT EXISTS(SELECT 1 FROM sensor_data WHERE device_id = %s);"
            cursor.execute(query, (device_id,))
            exists = cursor.fetchone()[0]
            return exists
    except psycopg2.Error as e:
        raise DatabaseError(e.pgerror or str(e))
    finally:
        if conn:
            conn.close()


# Get available time ranges for all devices from the database
# returns the earliest and latest timestamps for each device
def get_all_device_time_ranges_from_db():
    """
    Fetches the available time ranges for all devices from the database.
    Returns a list of dictionaries with device_id, start, and end timestamps.
    """

    conn = None
    try:
        conn = get_db_connection()
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
            return [serialize_row(dict(row)) for row in time_ranges]
    except psycopg2.Error as e:
        raise DatabaseError(e.pgerror or str(e))
    finally:
        if conn:
            conn.close()

# Validate timestamps and range for two devices
# Returns True if valid, else False + error message
# This function checks if the provided start and end timestamps are valid
# and if they overlap with the available data range for the given devices.
def validate_timestamps_and_range(device_id1, device_id2, start, end):
    """
    Validates if the provided start and end Unix timestamps are valid
    and within the overlapping available data range for the given devices.

    Returns:
        tuple: (bool, str|None) True if valid, else False + error message.
    """
    if start is None or end is None:
        return False, "Start and end timestamps must be provided."
    if start >= end:
        return False, "Start timestamp must be less than end timestamp."
    try:
        time_ranges = get_all_device_time_ranges_from_db()
    except DatabaseError as e:
        # Surface message upward; caller will serialize via global handler
        return False, str(e)

    if not time_ranges:
        return False, "No time ranges available for the devices."

    range1 = next((tr for tr in time_ranges if tr['device_id'] == device_id1), None)
    range2 = next((tr for tr in time_ranges if tr['device_id'] == device_id2), None)

    if not range1 or not range2:
        return False, f"No data found for device ID {device_id1} or {device_id2}."

    if range1['end'] < start or range2['end'] < start:
        return False, "No overlapping data available for the specified time range."

    return True, None

# Get sensor data by device ID and time range
# Returns all available data (by default) for a specific device
# Response format: [{device_id, humidity, temperature, pollen, particulate_matter, timestamp}, ...]
def get_device_data_from_db(device_id, metric=None, start=None, end=None):
    """
    Fetches sensor data for a specific device within an optional time range.
    If metric is provided, filters by that metric.
    Returns a list of dictionaries with device data.
    """

    valid_metrics = ['humidity', 'temperature', 'pollen', 'particulate_matter']
    if metric and metric not in valid_metrics:
        raise ValidationError(f"Invalid metric '{metric}'. Valid metrics: {', '.join(valid_metrics)}.")

    base_columns = [
        "device_id",
        "EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT AS unix_timestamp_seconds"
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

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(query, tuple(params))
            data = cursor.fetchall()
        result = []
        for row in data:
            row_dict = serialize_row(dict(row))
            result.append(row_dict)
        return result
    except psycopg2.Error as e:
        raise DatabaseError(e.pgerror or str(e))
    finally:
        if conn:
            conn.close()

# Get latest data for a device
def get_latest_device_data_from_db(device_id):
    """
    Fetches the latest sensor data for a specific device.
    Returns a dictionary with the latest data or None if no data is found.
    """

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
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
            s = serialize_row(dict(row))
            return {
                "device_id": s["device_id"],
                "unix_timestamp_seconds": s["unix_timestamp_seconds"],
                "humidity": s["humidity"],
                "temperature": s["temperature"],
                "pollen": s["pollen"],
                "particulate_matter": s["particulate_matter"]
            }
        return []
    except psycopg2.Error as e:
        raise DatabaseError(e.pgerror or str(e))
    finally:
        if conn:
            conn.close()


# Comparison Between Devices over Time Range
# Returns the selected metric of two devices over a given time range (by default all)
def compare_devices_over_time(device_id1, device_id2, metric=None, start=None, end=None, num_buckets=None):
    """
    Compares the specified metric for two devices over a given time range.
    If no metric is specified, compares all metrics.
    Returns a dictionary with the comparison data.
    """

    if metric not in ['humidity', 'temperature', 'pollen', 'particulate_matter']:
        raise ValidationError("Invalid metric. Must be one of: 'humidity', 'temperature', 'pollen', 'particulate_matter'.")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)

        count_query = """
            SELECT COUNT(*) FROM sensor_data
            WHERE (device_id = %s OR device_id = %s)
            AND EXTRACT(EPOCH FROM timestamp) >= %s
            AND EXTRACT(EPOCH FROM timestamp) <= %s;
        """
        cursor.execute(count_query, (device_id1, device_id2, start, end))
        total_raw_entries = cursor.fetchone()[0]

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
            cursor.close()
            conn.close()
            result = {f"device_{device_id1}": [], f"device_{device_id2}": []}
            for row in rows:
                entry = {
                    "timestamp": int(row["unix_timestamp_seconds"]),
                    "value": float(row[metric]) if row[metric] is not None else None
                }
                result[f"device_{row['device_id']}"].append(entry)
            if num_buckets and num_buckets > total_raw_entries:
                result["message"] = f"Warning: The number of buckets ({num_buckets}) exceeds the total number of raw entries ({total_raw_entries})."
            else:
                result["message"] = None
            result["status"] = "success"
            return result

        # determine time range if missing
        if not start or not end:
            cursor.execute("""
                SELECT MIN(EXTRACT(EPOCH FROM timestamp)), MAX(EXTRACT(EPOCH FROM timestamp))
                FROM sensor_data
                WHERE device_id = %s OR device_id = %s
            """, (device_id1, device_id2))
            start, end = cursor.fetchone()

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
        cursor.close()
        conn.close()

        result = {f"device_{device_id1}": [], f"device_{device_id2}": []}
        for row in rows:
            entry = {
                "timestamp": int(row["bucket_start"]),
                "value": float(row["avg_value"]) if row["avg_value"] is not None else None
            }
            result[f"device_{row['device_id']}"].append(entry)
        result["message"] = None
        result["status"] = "success"

        if num_buckets > total_raw_entries:
            result["message"] = f"Warning: The number of buckets ({num_buckets}) exceeds the total number of raw entries ({total_raw_entries}). Data may be averaged over larger intervals."
            logger.warning(result["message"])
        return result
    except psycopg2.Error as e:
        raise DatabaseError(e.pgerror or str(e))
    finally:
        # Close any leaked connection/cursor if earlier returns did not run finally
        try:
            if conn and not conn.closed:
                conn.close()
        except Exception:
            pass

# GET thresholds from the database
# Returns a dict of thresholds
def get_thresholds_from_db():
    """
    Fetches the thresholds for devices from the database.
    Returns a list of dictionaries with threshold data.
    """

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM thresholds LIMIT 1;")
            rows = cursor.fetchall()
            return [serialize_row(dict(row)) for row in rows]
    except psycopg2.Error as e:
        raise DatabaseError(e.pgerror or str(e))
    finally:
        if conn:
            conn.close()


# Update thresholds in the database
# Deletes existing thresholds and inserts new ones
def update_thresholds_in_db(threshold_data):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM thresholds;")
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
        cur.execute(insert_query, (
            threshold_data['temperature_min_hard'], threshold_data['temperature_min_soft'], threshold_data['temperature_max_soft'], threshold_data['temperature_max_hard'],
            threshold_data['humidity_min_hard'], threshold_data['humidity_min_soft'], threshold_data['humidity_max_soft'], threshold_data['humidity_max_hard'],
            threshold_data['pollen_min_hard'], threshold_data['pollen_min_soft'], threshold_data['pollen_max_soft'], threshold_data['pollen_max_hard'],
            threshold_data['particulate_matter_min_hard'], threshold_data['particulate_matter_min_soft'], threshold_data['particulate_matter_max_soft'], threshold_data['particulate_matter_max_hard']
        ))
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(e.pgerror or str(e))
    finally:
        if conn:
            conn.close()
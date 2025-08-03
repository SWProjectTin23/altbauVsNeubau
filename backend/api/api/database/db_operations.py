import psycopg2
from psycopg2 import extras
import os

from decimal import Decimal

from dotenv import load_dotenv
from decimal import Decimal

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


def serialize_row(row: dict) -> dict:
    """Konvertiert Decimal in float für JSON-Kompatibilität."""
    return {
        k: float(v) if isinstance(v, Decimal) else v
        for k, v in row.items()
    }


# Check if all required database configuration parameters are set
def check_db_config():
    missing = [k for k in ["host", "database", "user", "password"] if not DB_CONFIG[k]]
    if missing:
        msg = f"Missing DB config values: {', '.join(missing)}. Please check your .env file or environment variables."
        print(msg)
        raise ValueError(msg)


# Function to get a database connection
def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    Returns a Connection object.
    Raises psycopg2.Error on connection errors.
    """
    check_db_config()
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=int(DB_CONFIG["port"]) # Ensure port is an integer
        )
        return conn
    except psycopg2.Error as e:
        # Re-raise the connection error for handling by the caller.
        print(f"Error while connecting to the database: {e}")
        raise

# Check if a device exists in the database
def device_exists(device_id):
    """
    Checks if a device with the given ID exists in the database.
    Returns True if the device exists, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT EXISTS(SELECT 1 FROM sensor_data WHERE device_id = %s);"
    cursor.execute(query, (device_id,))
    exists = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return exists


# Get available time ranges for all devices from the database
# returns the earliest and latest timestamps for each device
# Response format: [{device_id, start, end}, ...]
def get_all_device_time_ranges_from_db():
    """
    Fetches the available time ranges for all devices from the database.
    Returns a list of dictionaries with device_id, start, and end timestamps.
    """
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
    finally:
        conn.close()
    return [serialize_row(dict(row)) for row in time_ranges]  # Convert rows to dictionaries

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
    
    # Fetch the time ranges for both devices
    time_ranges = get_all_device_time_ranges_from_db()
    if not time_ranges:
        return False, "No time ranges available for the devices."
    
    # Lookup the time ranges for the specified devices
    range1 = next((tr for tr in time_ranges if tr['device_id'] == device_id1), None)
    range2 = next((tr for tr in time_ranges if tr['device_id'] == device_id2), None)

    if not range1 or not range2:
        return False, f"No data found for device ID {device_id1} or {device_id2}."

    # Check for overlapping time ranges
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
        raise ValueError(f"Invalid metric '{metric}'. Valid metrics: {', '.join(valid_metrics)}.")
    
    # Build SELECT query dynamically based on the metric
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

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(query, tuple(params))
            data = cursor.fetchall()
    finally:
        conn.close()

    result = []
    for row in data:
        row_dict = serialize_row(dict(row))
        result.append(row_dict)

    return result  # Return the list of dictionaries with device data

# Get latest data for a device
# Response format: {device_id, humidity, temperature, pollen, particulate_matter, timestamp}
def get_latest_device_data_from_db(device_id):
    """
    Fetches the latest sensor data for a specific device.
    Returns a dictionary with the latest data or None if no data is found.
    """
    print(f"Fetching latest data for device ID: {device_id}")
    
    conn = get_db_connection()
    
    try:
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
    finally:
        conn.close()
    
    if row:
        return {
            "device_id": serialize_row(row)["device_id"],
            "unix_timestamp_seconds": serialize_row(row)["unix_timestamp_seconds"],
            "humidity": serialize_row(row)["humidity"],
            "temperature": serialize_row(row)["temperature"],
            "pollen": serialize_row(row)["pollen"],
            "particulate_matter": serialize_row(row)["particulate_matter"]
        }
    else:
        return []  # Return an empty list if no data is found


# Comparison Between Devices over Time Range
# Returns the selected metric of two devices over a given time range (by default all)
# http://localhost:5001/api/comparison?device_1=1&device_2=2&metric=pollen&start=1721745600&end=1721745660
# Parameters:
# - device_1: ID of the first device
# - device_2: ID of the second device
# - metric: Metric to compare (optional, defaults to all metrics)
# - start: Start timestamp (optional)
# - end: End timestamp (optional)
def compare_devices_over_time(device_id1, device_id2, metric=None, start=None, end=None):
    """
    Compares the selected metric of two devices over a given time range.
    Returns a list of dictionaries with the comparison data.
    """
    if metric not in ['humidity', 'temperature', 'pollen', 'particulate_matter']:
        raise ValueError("Invalid metric. Must be one of: 'humidity', 'temperature', 'pollen', 'particulate_matter'.")

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=extras.DictCursor)

    query = f"""
        SELECT device_id, 
        EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT AS unix_timestamp_seconds,
        {metric}
        FROM sensor_data
        WHERE (device_id = %s OR device_id = %s)
    """
    params = [device_id1, device_id2]

    if start:
        query += " AND timestamp >= TO_TIMESTAMP(%s)::TIMESTAMPTZ"
        params.append(start)

    if end:
        query += " AND timestamp <= TO_TIMESTAMP(%s)::TIMESTAMPTZ"
        params.append(end)

    query += " ORDER BY timestamp;"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    result = {f"device_{row['device_id']}": [] for row in rows}
    for row in rows:    
        value = row[metric]
        if isinstance(value, Decimal):
            value = float(value)
        result[f"device_{row['device_id']}"].append({
            "timestamp": row["unix_timestamp_seconds"],
            "value": value
        })
    print(rows) 

    return result
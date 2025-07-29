import psycopg2
from psycopg2 import extras
import os
from dotenv import load_dotenv

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
    cursor = conn.cursor(cursor_factory=extras.DictCursor)

    query = """
        SELECT 
        device_id, 
        MIN(timestamp) AS start, 
        MAX(timestamp) AS end,
        EXTRACT(EPOCH FROM MIN(timestamp))::BIGINT AS start_unix_seconds,
        EXTRACT(EPOCH FROM MAX(timestamp))::BIGINT AS end_unix_seconds
        FROM sensor_data
        GROUP BY device_id;
    """

    cursor.execute(query)
    time_ranges = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in time_ranges]  # Convert rows to dictionaries

def validate_timestamps_and_range(device_id1, device_id2, start_str, end_str):
    """
    Validates if the provided start and end Unix timestamps are valid
    and within the available data range for the given devices.

    Args:
        device_id1 (int): First device ID.
        device_id2 (int): Second device ID.
        start_str (str): Start timestamp as Unix string.
        end_str (str): End timestamp as Unix string.

    Returns:
        tuple: (bool, str) where bool is True for valid, False otherwise.
               str is an error message if invalid.
    """
    # Check if device IDs are valid
    if not device_exists(device_id1):
        return False, f"Device {device_id1} does not exist."
    if not device_exists(device_id2):
        return False, f"Device {device_id2} does not exist."

    # Convert start and end to integers, if provided
    try:
        start = int(start_str) if start_str else None
        end = int(end_str) if end_str else None
    except ValueError:
        return False, "Invalid timestamp format. Start and end must be integers."

    # Check if start is before end
    if start is not None and end is not None and start >= end:
        return False, "Start timestamp must be before end timestamp."

    # Get data ranges for all devices
    all_ranges = get_all_device_time_ranges_from_db()

    # If no ranges are found, return an error
    if not all_ranges:
        return False, "Could not retrieve available time ranges from the database. Database might be empty or unreachable."

    # Find the ranges for the specified devices
    range1 = next((r for r in all_ranges if r['device_id'] == device_id1), None)
    range2 = next((r for r in all_ranges if r['device_id'] == device_id2), None)

    # If either device does not have data, return an error
    if not range1:
        return False, f"No data found for device {device_id1} to validate time range."
    if not range2:
        return False, f"No data found for device {device_id2} to validate time range."

    # Determine the actual data range for both devices
    # Use the earliest start and latest end from both devices
    # This ensures we only consider the overlapping data range
    actual_data_start = max(range1['start_unix_seconds'], range2['start_unix_seconds'])
    actual_data_end = min(range1['end_unix_seconds'], range2['end_unix_seconds'])


    effective_start = start if start is not None else actual_data_start
    effective_end = end if end is not None else actual_data_end

    # Check if the requested range is within the actual data range
    if effective_start < actual_data_start or effective_end > actual_data_end:
        return False, (f"Requested time range [{start_str}, {end_str}] is out of bounds for devices. "
                      f"Available data for device {device_id1}: [{range1['start_unix_seconds']}, {range1['end_unix_seconds']}]. "
                      f"Available data for device {device_id2}: [{range2['start_unix_seconds']}, {range2['end_unix_seconds']}]. "
                      f"Common available range: [{actual_data_start}, {actual_data_end}]."
                      )
    # If all checks pass, return valid
    return True, None # Gültig, kein Fehler


# Get sensor data by device ID and time range
# Returns all available data (by default) for a specific device
# Response format: [{device_id, humidity, temperature, pollen, particulate_matter, timestamp}, ...]
def get_device_data_from_db(device_id, metric=None, start=None, end=None):
    """
    Fetches sensor data for a specific device within an optional time range.
    If metric is provided, filters by that metric.
    Returns a list of dictionaries with device data.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=extras.DictCursor)

    query = """
        SELECT
            device_id,
            timestamp,
            EXTRACT(EPOCH FROM timestamp)::BIGINT AS unix_timestamp_seconds,
            temperature,
            humidity,
            pollen,
            particulate_matter
            FROM sensor_data
            WHERE device_id = %s
        """
    params = [device_id]

    if start:
            query += " AND timestamp >= TO_TIMESTAMP(%s)::TIMESTAMPTZ"
            params.append(start)

    if end:
        query += " AND timestamp <= TO_TIMESTAMP(%s)::TIMESTAMPTZ"
        params.append(end)

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in data]  # Convert rows to dictionaries

# Get latest data for a device
# Response format: {device_id, humidity, temperature, pollen, particulate_matter, timestamp}
def get_latest_device_data_from_db(device_id):
    """
    Fetches the latest sensor data for a specific device.
    Returns a dictionary with the latest data or None if no data is found.
    """
    print(f"Fetching latest data for device ID: {device_id}")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=extras.DictCursor)

    query = """
    SELECT
        device_id,
        timestamp,
        -- Convert timestamp to UNIX seconds for compatibility
        EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT AS unix_timestamp_seconds,
        temperature,
        humidity,
        pollen,
        particulate_matter
    FROM sensor_data
    WHERE device_id = %s
    ORDER BY timestamp DESC
    LIMIT 1;
    """
    
    print(f"Executing query: {query} with params: {device_id}")

    cursor.execute(query, (device_id,))
    latest_data = cursor.fetchone()

    cursor.close()
    conn.close()

    return dict(latest_data) if latest_data else None  # Convert row to dictionary or return None if no data

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
        timestamp,
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
        result[f"device_{row['device_id']}"].append({
            "timestamp": row["timestamp"],
            "value": row[metric]
        })

    return result
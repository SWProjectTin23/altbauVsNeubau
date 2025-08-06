import psycopg2
from psycopg2 import extras
import os
import datetime
from dotenv import load_dotenv

from decimal import Decimal
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

    # Get a database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to check if the device exists
    query = "SELECT EXISTS(SELECT 1 FROM sensor_data WHERE device_id = %s);"
    cursor.execute(query, (device_id,)) # Execute the query 
    exists = cursor.fetchone()[0] # Fetch the result

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return exists # Return True if the device exists, False otherwise


# Get available time ranges for all devices from the database
# returns the earliest and latest timestamps for each device
def get_all_device_time_ranges_from_db():
    """
    Fetches the available time ranges for all devices from the database.
    Returns a list of dictionaries with device_id, start, and end timestamps.
    """

    # Get a database connection
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:

            # Query to get the start and end timestamps for each device
            query = """
                SELECT device_id, 
                MIN(EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT) AS start,
                MAX(EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT) AS end
                FROM sensor_data
                GROUP BY device_id
                ORDER BY device_id;
            """
            # Execute the query
            cursor.execute(query)
            # Fetch all time ranges
            time_ranges = cursor.fetchall()
    finally:
        conn.close() # Close the connection

    # Return the time ranges as a list of dictionaries
    # Each dictionary contains device_id, start, and end timestamps
    return [serialize_row(dict(row)) for row in time_ranges]  # Convert rows to dictionaries

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
    
    # Check if both start and end timestamps are provided
    if start is None or end is None:
        return False, "Start and end timestamps must be provided."
    
    # Check if start is less than end
    if start >= end:
        return False, "Start timestamp must be less than end timestamp."
    
    # Fetch the time ranges for both devices
    time_ranges = get_all_device_time_ranges_from_db()

    if not time_ranges:
        return False, "No time ranges available for the devices."
    
    # Lookup the time ranges for the specified devices
    range1 = next((tr for tr in time_ranges if tr['device_id'] == device_id1), None)
    range2 = next((tr for tr in time_ranges if tr['device_id'] == device_id2), None)

    # Check if both devices have valid time ranges
    if not range1 or not range2:
        return False, f"No data found for device ID {device_id1} or {device_id2}."

    # Check if the provided range overlaps with the available data ranges
    if range1['end'] < start or range2['end'] < start:
        return False, "No overlapping data available for the specified time range."

    # return True if all checks pass
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

    # Define valid metrics
    valid_metrics = ['humidity', 'temperature', 'pollen', 'particulate_matter']

    # Validate the metric if provided
    if metric and metric not in valid_metrics:
        raise ValueError(f"Invalid metric '{metric}'. Valid metrics: {', '.join(valid_metrics)}.")
    
    # Build SELECT query dynamically based on the metric
    base_columns = [
        "device_id",
        "EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT AS unix_timestamp_seconds"
    ]

    # If a metric is specified, include it in the SELECT clause
    # Otherwise, include all valid metrics
    if metric:
        select_columns = base_columns + [metric]
    else:
        select_columns = base_columns + valid_metrics

    # Construct the SQL query
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

    # Get a database connection
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(query, tuple(params))
            data = cursor.fetchall()
    finally:
        conn.close() # Close the connection

    result = []
    for row in data:
        row_dict = serialize_row(dict(row))
        result.append(row_dict)

    return result  # Return the list of dictionaries with device data

# Get latest data for a device
def get_latest_device_data_from_db(device_id):
    """
    Fetches the latest sensor data for a specific device.
    Returns a dictionary with the latest data or None if no data is found.
    """
    print(f"Fetching latest data for device ID: {device_id}")
    
    # Get a database connection
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

            # Execute the query with the device ID
            cursor.execute(query, (device_id,))
            row = cursor.fetchone() # Fetch the latest row
    finally:
        conn.close() # Close the connection

    # If a row is found, serialize it; otherwise, return an empty list
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
def compare_devices_over_time(device_id1, device_id2, metric=None, start=None, end=None, num_buckets=None):
    """
    Compares the specified metric for two devices over a given time range.
    If no metric is specified, compares all metrics.
    Returns a dictionary with the comparison data.
    """

    print(f"[DEBUG] compare_devices_over_time called with device_id1={device_id1}, device_id2={device_id2}, metric={metric}, start={start}, end={end}, num_buckets={num_buckets}")
   

    # Check if metric is specified
    if metric not in ['humidity', 'temperature', 'pollen', 'particulate_matter']:
        raise ValueError("Invalid metric. Must be one of: 'humidity', 'temperature', 'pollen', 'particulate_matter'.")

    # Get a database connection
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=extras.DictCursor) # Create a cursor with dictionary support

    # Count the total number of raw entries for each device in the specified time range
    # This is used to check if num_buckets exceeds the total number of raw entries
    count_query = """
        SELECT COUNT(*) FROM sensor_data
        WHERE (device_id = %s OR device_id = %s)
        AND EXTRACT(EPOCH FROM timestamp) >= %s
        AND EXTRACT(EPOCH FROM timestamp) <= %s;
        """
    count_params = (device_id1, device_id2, start, end)
    cursor.execute(count_query, count_params)
    total_raw_entries = cursor.fetchone()[0]
    print(f"[DEBUG] total_raw_entries in time range: {total_raw_entries}")
    print(f"[DEBUG] num_buckets: {num_buckets}")


    # If num_buckets is None, fetch all data for both devices
    if num_buckets is None or num_buckets > total_raw_entries:
        # Query to get all data for the specified devices and metric
        query = f"""
            SELECT device_id, 
            EXTRACT(EPOCH FROM timestamp AT TIME ZONE 'UTC')::BIGINT AS unix_timestamp_seconds,
            {metric}
            FROM sensor_data
            WHERE device_id IN (%s, %s)
        """

        print(f"[DEBUG] Fetching all data for devices {device_id1} and {device_id2} for metric '{metric}'")

        params = (device_id1, device_id2)

        # Add time range conditions if provided
        if start:
            query += " AND timestamp >= TO_TIMESTAMP(%s)::TIMESTAMPTZ"
            params += (start,)
        if end:
            query += " AND timestamp <= TO_TIMESTAMP(%s)::TIMESTAMPTZ"
            params += (end,)
        
        # Execute the query with the parameters
        cursor.execute(query, params)
        # Fetch all rows
        rows = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Format the result
        result = {f"device_{device_id1}": [], f"device_{device_id2}": []}
        for row in rows:
            entry = {
                "timestamp": int(row["unix_timestamp_seconds"]),
                "value": float(row[metric]) if row[metric] is not None else None
            }
            result[f"device_{row['device_id']}"].append(entry)
        if num_buckets > total_raw_entries:
            result["message"] = f"Warning: The number of buckets ({num_buckets}) exceeds the total number of raw entries ({total_raw_entries})."
        else:
            result["message"]= None
        result["status"] = "success"
        print(f"[DEBUG] Result with all data: {result}")
        return result # Return the result with all data

    # Determine time range
    if not start or not end:
        # If no start/end is specified, take the entire range of both devices
        cursor.execute("""
            SELECT MIN(EXTRACT(EPOCH FROM timestamp)), MAX(EXTRACT(EPOCH FROM timestamp))
            FROM sensor_data
            WHERE device_id = %s OR device_id = %s
        """, (device_id1, device_id2))
        start, end = cursor.fetchone()

    # Calculate bucket size
    bucket_size = max(1, int((end - start) / num_buckets))
    print(f"[DEBUG] Calculated bucket_size: {bucket_size}")

    # Query to get the average value of the metric for each device in time buckets
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

    # Execute the query with the parameters
    params = [start, bucket_size, device_id1, device_id2, start, end]
    cursor.execute(query, params)
    # Fetch all rows
    rows = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Format the result
    result = {f"device_{device_id1}": [], f"device_{device_id2}": []}
    for row in rows:
        entry = {
            "timestamp": int(row["bucket_start"]),
            "value": float(row["avg_value"]) if row["avg_value"] is not None else None
        }
        result[f"device_{row['device_id']}"].append(entry)
        result["message"]= None
        result["status"] = "success"

    if num_buckets > total_raw_entries:
        result["message"] = f"Warning: The number of buckets ({num_buckets}) exceeds the total number of raw entries ({total_raw_entries}). Data may be averaged over larger intervals."
        print(f"[WARN] {result['message']}")
    return result # Return the result with averaged data

# GET thresholds from the database
# Returns a dict of thresholds
def get_thresholds_from_db():
    """
    Fetches the thresholds for devices from the database.
    Returns a list of dictionaries with threshold data.
    """

    conn = None

    try:
        # Get a database connection
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor) # Create a cursor with dictionary support

        # Query to get the thresholds
        query = """
            SELECT * FROM thresholds LIMIT 1;  -- Assuming only one row of thresholds exists
        """
        
        # Execute the query
        cursor.execute(query)
        rows = cursor.fetchall()  # Fetch all rows

        cursor.close() # Close the cursor
        return [serialize_row(dict(row)) for row in rows]  # Convert rows to dictionaries

    # Handle database errors
    except psycopg2.Error as e:
        print(f"Database error in get_thresholds_from_db: {e}")
        raise
    finally:
        if conn:
            conn.close() # Close the connection


# Update thresholds in the database
# Deletes existing thresholds and inserts new ones
def update_thresholds_in_db(threshold_data):
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
            threshold_data['pollen_min_hard'], threshold_data['pollen_min_soft'], threshold_data['pollen_max_soft'],threshold_data['pollen_max_hard'],
            threshold_data['particulate_matter_min_hard'], threshold_data['particulate_matter_min_soft'], threshold_data['particulate_matter_max_soft'], threshold_data['particulate_matter_max_hard']
        ))

        # Commit the changes to the database
        conn.commit()
        # Close the cursor
        cur.close()
        return True # Return True if the update was successful
    
    # Handle database errors
    except psycopg2.Error as e:
        if conn:
            conn.rollback() # Rollback in case of an error
        print(f"Database error in update_thresholds_in_db: {e}")
        raise # Re-raise the exception to be caught by the API endpoint
    finally:
        if conn:
            conn.close() # Close the connection
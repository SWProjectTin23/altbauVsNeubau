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
if not all([DB_CONFIG["host"], DB_CONFIG["database"], DB_CONFIG["user"], DB_CONFIG["password"]]):
    raise ValueError("One or more essential database configuration parameters (HOST, NAME, USER, PASSWORD) are missing. Please check your .env file or environment variables.")

# Function to get a database connection
def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    Returns a Connection object.
    Raises psycopg2.Error on connection errors.
    """
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

# Function to fetch device data from the database
def get_device_data_from_db(device_id: int, metric: str, start: int = None, end: int = None) -> list:
    """
    Fetches device data for a specific device and metric from the PostgreSQL database.

    Args:
        device_id (int): The ID of the device.
        metric (str): The metric, e.g., 'temperature', 'humidity'. (Validated in the API).
        start (int, optional): Optional start Unix timestamp.
        end (int, optional): Optional end Unix timestamp.

    Returns:
        list: A list of dictionaries, where each dictionary contains 'timestamp' and 'value'.
              Example: [{'timestamp': 1678886400, 'value': 22.5}]

    Raises:
        psycopg2.Error: On database errors, which can be handled by the calling function.
    """
    conn = None
    try:
        conn = get_db_connection()
        # Use RealDictCursor to get results as dictionaries (column_name: value)
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor) 

        # The query is securely constructed. The metric name is inserted directly
        # because it's validated in the API logic and psycopg2 doesn't parameterize column names.
        query = f"SELECT timestamp, {metric} FROM device_data WHERE device_id = %s"
        params = [device_id]

        if start is not None:
            query += " AND timestamp >= %s"
            params.append(start)
        if end is not None:
            query += " AND timestamp <= %s"
            params.append(end)

        cursor.execute(query, params)
        data = cursor.fetchall()

        result = []
        for row in data:
            result.append({
                "timestamp": row["timestamp"],
                "value": row[metric] # Access via dynamic column name
            })
        return result

    except psycopg2.Error as e:
        # Re-raise the database error for further handling by the calling function.
        raise
    finally:
        # Ensure the database connection is always closed.
        if conn:
            conn.close()

# Function to fetch all data entries for a specific device
def get_all_device_data_from_db(device_id: int, start: int = None, end: int = None) -> list:
    """
    Fetches all data entries for a specific device within a given timestamp range
    from the PostgreSQL database.

    Args:
        device_id (int): The ID of the device.
        start (int, optional): Optional start Unix timestamp.
        end (int, optional): Optional end Unix timestamp.

    Returns:
        list: A list of dictionaries, where each dictionary represents a full data entry
              for the device (including timestamp, temperature, humidity, etc.).
              Example: [{'timestamp': 1678886400, 'temperature': 22.5, 'humidity': 55.0, ...}]

    Raises:
        psycopg2.Error: On database errors, which can be handled by the calling function.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        # Select all relevant columns. Exclude 'id' if it's just an internal primary key.
        # Adjust column names if they differ in your actual DB schema.
        query = "SELECT timestamp, temperature, humidity, pollen, particulate_matter FROM device_data WHERE device_id = %s"
        params = [device_id]

        if start is not None:
            query += " AND timestamp >= %s"
            params.append(start)
        if end is not None:
            query += " AND timestamp <= %s"
            params.append(end)
        
        # Optional: Order by timestamp
        query += " ORDER BY timestamp ASC"

        cursor.execute(query, params)
        data = cursor.fetchall()

        # fetchall() with RealDictCursor already returns a list of dictionaries,
        # so we can return it directly.
        return data

    except psycopg2.Error as e:
        raise
    finally:
        if conn:
            conn.close()

# Function to fetch the latest data entry for a specific device
def get_latest_device_data_from_db(device_id: int) -> dict | None:
    """
    Fetches the latest data entry for a specific device from the PostgreSQL database.

    Args:
        device_id (int): The ID of the device.

    Returns:
        dict | None: A dictionary representing the latest full data entry for the device,
                     or None if no data is found for the device.
                     Example: {'timestamp': 1678886400, 'temperature': 22.5, ...}

    Raises:
        psycopg2.Error: On database errors, which can be handled by the calling function.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        # Select all relevant columns, order by timestamp descending, and limit to 1
        query = """
            SELECT timestamp, temperature, humidity, pollen, particulate_matter
            FROM device_data
            WHERE device_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """
        params = [device_id]

        cursor.execute(query, params)
        latest_data = cursor.fetchone() # Use fetchone() to get a single row

        return latest_data # Will be a dict or None

    except psycopg2.Error as e:
        raise
    finally:
        if conn:
            conn.close()

# Function to check if a device exists in the database
def device_exists(device_id: int) -> bool:
    """
    Checks if a device with the given ID exists in the database.
    This assumes device_data table implies device existence.
    If you have a separate 'devices' table, it's better to check there.

    Args:
        device_id (int): The ID of the device to check.

    Returns:
        bool: True if the device exists, False otherwise.

    Raises:
        psycopg2.Error: On database errors.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Optimierte Abfrage: Prüft, ob ein beliebiger Eintrag für diese device_id existiert
        # Alternativ: SELECT 1 FROM devices WHERE id = %s LIMIT 1; if you have a devices table.
        query = "SELECT EXISTS(SELECT 1 FROM device_data WHERE device_id = %s LIMIT 1)"
        params = [device_id]

        cursor.execute(query, params)
        exists = cursor.fetchone()[0] # fetchone() returns a tuple, get the first element

        return exists

    except psycopg2.Error as e:
        print(f"Error checking device existence: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Function to get the time range for all devices
def get_all_device_time_ranges_from_db() -> dict:
    """
    Fetches the minimum and maximum timestamp for all device_ids present in the database.

    Returns:
        dict: A dictionary where keys are 'device_X' (e.g., 'device_1') and values
              are dictionaries containing 'start' (MIN timestamp) and 'end' (MAX timestamp).
              Example: {'device_1': {'start': 1721736000, 'end': 1721745000}}

    Raises:
        psycopg2.Error: On database errors.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        # SQL query to get MIN and MAX timestamp for each device_id
        query = """
            SELECT
                device_id,
                MIN(timestamp) AS start,
                MAX(timestamp) AS end
            FROM
                device_data
            GROUP BY
                device_id
            ORDER BY
                device_id ASC;
        """
        cursor.execute(query)
        data = cursor.fetchall()

        result = {}
        for row in data:
            result[f"device_{row['device_id']}"] = {
                "start": row["start"],
                "end": row["end"]
            }
        return result

    except psycopg2.Error as e:
        print(f"Error fetching device time ranges: {e}")
        raise
    finally:
        if conn:
            conn.close()
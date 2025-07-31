# backend/generate_test_data.py

import psycopg2
import random
import time
import os
from datetime import timedelta # Import for handling time intervals
from dotenv import load_dotenv
from datetime import datetime, timezone # Import for handling timestamps as datetime objects

# Load environment variables from the .env file
load_dotenv()

# --- Database Configuration ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"), # Use localhost for direct access from host
    "database": os.getenv("DB_NAME", "altbau_vs_neubau"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "port": os.getenv("DB_PORT", "5432")
}

# --- Test Data Parameters ---
NUM_DATA_POINTS = 1000
NUM_DEVICES = 2 # Generate data for device_id 1 and device_id 2

# Define a realistic time range (e.g., last 30 days from now)
# We'll use random timestamps within this range for each data point
END_DATETIME = datetime.now(timezone.utc) # Current UTC datetime object
# 30 days ago from now (in UTC)
START_DATETIME = END_DATETIME - timedelta(days=30) 

# Calculate the timestamp range in seconds since epoch for random generation
END_TIMESTAMP_SEC = int(END_DATETIME.timestamp())
START_TIMESTAMP_SEC = int(START_DATETIME.timestamp())

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=int(DB_CONFIG["port"]),
            sslmode="disable" # Ensure SSL is disabled if not configured on server
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        print("Please ensure your Docker database container is running and accessible.")
        print(f"Connection details used: Host={DB_CONFIG['host']}, Port={DB_CONFIG['port']}, User={DB_CONFIG['user']}, DB={DB_CONFIG['database']}")
        raise

def generate_data():
    """Generates a list of random sensor data points matching the new schema."""
    data = []
    for _ in range(NUM_DATA_POINTS):
        device_id = random.randint(1, NUM_DEVICES) # Assign to device 1 or 2
        
        # Generate a random Unix timestamp within the defined range
        random_timestamp_sec = random.randint(START_TIMESTAMP_SEC, END_TIMESTAMP_SEC)
        # Convert Unix timestamp to a timezone-aware datetime object (UTC)
        timestamp_dt = datetime.fromtimestamp(random_timestamp_sec, tz=timezone.utc)

        # Generate random values matching the DECIMAL and INT types
        temperature = round(random.uniform(15.0, 30.0), 2) # DECIMAL(5, 2)
        humidity = round(random.uniform(30.0, 70.0), 2)    # DECIMAL(5, 2)
        pollen = random.randint(0, 500)                    # INT
        particulate_matter = random.randint(0, 100)        # INT

        data.append((device_id, timestamp_dt, temperature, humidity, pollen, particulate_matter))
    return data

def insert_data(data_to_insert):
    """Inserts generated data into the PostgreSQL database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # IMPORTANT: Use the new table name 'sensor_data'
        # Ensure the column order matches the data tuple
        insert_query = """
            INSERT INTO sensor_data (device_id, timestamp, temperature, humidity, pollen, particulate_matter)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (device_id, timestamp) DO NOTHING; -- Prevents errors on duplicate primary keys
        """
        
        # Use executemany for efficient bulk insertion
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        print(f"Successfully inserted {cursor.rowcount} new data points into 'sensor_data' table.")

    except psycopg2.Error as e:
        print(f"Database error during insertion: {e}")
        if conn:
            conn.rollback() # Rollback in case of error
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Starting data generation...")
    generated_data = generate_data()
    print(f"Generated {len(generated_data)} test data points.")

    print("Attempting to insert data into the database...")
    insert_data(generated_data)
    print("Data insertion process completed.")
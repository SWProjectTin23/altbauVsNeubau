from prometheus_client import Gauge, start_http_server
from dotenv import load_dotenv
import time
import psycopg2
from datetime import datetime, timezone
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

sensor_delay = Gauge(
    'sensor_seconds_since_last_data',
    'Seconds since last sensor value',
    ['device_id']
)

DB = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'DB_NAME'),
    'user': os.getenv('DB_USER', 'DB_USER'),
    'password': os.getenv('DB_PASSWORD', 'DB_PASSWORD')
}

try:
    conn = psycopg2.connect(**DB)
    print("Connection successful")
    conn.close()
except Exception as e:
    print("Connection failed:", e)

def get_all_sensor_delays():
    delays = {}
    try:
        conn = psycopg2.connect(**DB)
        cur = conn.cursor()

        cur.execute("""
            SELECT device_id, MAX(timestamp) as last_seen 
            FROM sensor_data
            GROUP BY device_id
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        for device_id, last_seen in rows:
            if last_seen:
                delay = (now - last_seen).total_seconds()
            else:
                delay = 99999  # Kein Wert → extrem hoch
            delays[str(device_id)] = delay

    except Exception as e:
        print(f"Error fetching sensor delays: {e}")

    return delays

if __name__ == '__main__':
    start_http_server(9100)
    print("Exporter listening on port 9100")
    while True:
        delays = get_all_sensor_delays()
        for device_id, delay in delays.items():
            sensor_delay.labels(device_id=device_id).set(delay)
            print(f"Device {device_id}: {delay:.1f} seconds since last data")

        time.sleep(15)
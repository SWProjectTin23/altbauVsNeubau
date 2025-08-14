import logging
import psycopg2
from exceptions import DatabaseError

# mqtt_client.db_writer
logger = logging.getLogger(__name__)

def insert_sensor_data(conn, device_id, timestamp, *, temperature=None, humidity=None,
pollen=None, particulate_matter=None):
    """
    Insert a row into the sensor_data table. Default to None.
    """
    cursor = conn.cursor()
    try:
        insert_query = """
        INSERT INTO sensor_data (device_id, timestamp, temperature, humidity, pollen, particulate_matter)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (device_id, timestamp)
        DO UPDATE SET
            temperature = COALESCE(EXCLUDED.temperature, sensor_data.temperature),
            humidity = COALESCE(EXCLUDED.humidity, sensor_data.humidity),
            pollen = COALESCE(EXCLUDED.pollen, sensor_data.pollen),
            particulate_matter = COALESCE(EXCLUDED.particulate_matter, sensor_data.particulate_matter);
        """
        cursor.execute(insert_query, (device_id, timestamp, temperature, humidity, pollen, particulate_matter))
        conn.commit()
        
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(e.pgerror or str(e))
    finally:
        cursor.close()

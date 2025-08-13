import logging

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
        cursor.execute(insert_query, (
            device_id,
            timestamp,
            temperature,
            humidity,
            pollen,
            particulate_matter
        ))
        conn.commit()
        
        # Only log non-None values
        updated_fields = {}
        if temperature is not None:
            updated_fields["temperature"] = temperature
        if humidity is not None:
            updated_fields["humidity"] = humidity
        if pollen is not None:
            updated_fields["pollen"] = pollen
        if particulate_matter is not None:
            updated_fields["particulate_matter"] = particulate_matter

        if updated_fields:
            logger.info(
                "Sensor data written: device_id=%s, timestamp=%s, fields=%s",
                device_id, timestamp, updated_fields
            )
        else:
            logger.debug(
                "Insert attempted but no fields/metric were provided: device_id=%s, timestamp=%s",
                device_id, timestamp
            )

    except Exception as e:
        conn.rollback()
        logger.error("Database insert failed: device_id=%s, timestamp=%s, error=%s", device_id, timestamp, str(e))
    finally:
        cursor.close()

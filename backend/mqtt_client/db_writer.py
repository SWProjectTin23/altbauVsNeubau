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
        print(f"[DB] Eingefügt: device_id={device_id}, time={timestamp}")
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] Fehler beim Einfügen: {e}")
    finally:
        cursor.close()

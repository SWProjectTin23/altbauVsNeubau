CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    type VARCHAR(50)
);

COMMENT ON TABLE devices IS 'Table for storing device information';
COMMENT ON COLUMN devices.id IS 'Unique identifier for the device';
COMMENT ON COLUMN devices.name IS 'Name of the device';
COMMENT ON COLUMN devices.location IS 'Location where the device is installed';
COMMENT ON COLUMN devices.type IS 'Type of the device (e.g., sensor, actuator)


CREATE TABLE IF NOT EXISTS sensor_data (
    device_id INT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    pollen INT,
    particulate_matter INT,
    PRIMARY KEY (device_id, timestamp)

    CONSTRAINT fk_sensor_device
        FOREIGN KEY (device_id)
        REFERENCES devices(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

COMMENT ON TABLE sensor_data IS 'Table for storing sensor data from devices';
COMMENT ON COLUMN sensor_data.device_id IS 'ID of the device that collected the data';
COMMENT ON COLUMN sensor_data.timestamp IS 'Timestamp of the data collection';
COMMENT ON COLUMN sensor_data.temperature IS 'Temperature reading from the device';
COMMENT ON COLUMN sensor_data.humidity IS 'Humidity reading from the device';
COMMENT ON COLUMN sensor_data.pollen IS 'Pollen count reading from the device';
COMMENT ON COLUMN sensor_data.particulate_matter IS 'Particulate matter reading from the device';
COMMENT ON TABLE device_thresholds IS 'Table for storing thresholds for devices';

-- change table to hypertable
SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS device_thresholds (
    device_id INT NOT NULL PRIMARY KEY,
    temperature_min DECIMAL(5, 2),
    temperature_max DECIMAL(5, 2),
    humidity_min DECIMAL(5, 2),
    humidity_max DECIMAL(5, 2),
    pollen_max INT,
    particulate_matter_max INT,
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_threshold_device
        FOREIGN KEY (device_id)
        REFERENCES devices(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

COMMENT ON COLUMN device_thresholds.device_id IS 'ID of the device for which thresholds are set';
COMMENT ON COLUMN device_thresholds.temperature_min IS 'Minimum temperature threshold for the device';
COMMENT ON COLUMN device_thresholds.temperature_max IS 'Maximum temperature threshold for the device';
COMMENT ON COLUMN device_thresholds.humidity_min IS 'Minimum humidity threshold for the device';
COMMENT ON COLUMN device_thresholds.humidity_max IS 'Maximum humidity threshold for the device';
COMMENT ON COLUMN device_thresholds.pollen_max IS 'Maximum pollen count threshold for the device';
COMMENT ON COLUMN device_thresholds.particulate_matter_max IS 'Maximum particulate matter threshold for the device';
COMMENT ON COLUMN device_thresholds.last_updated IS 'Timestamp of the last update to the thresholds';
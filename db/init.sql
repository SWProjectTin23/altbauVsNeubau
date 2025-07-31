CREATE TABLE IF NOT EXISTS sensor_data (
    device_id INT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    pollen INT,
    particulate_matter INT,
    PRIMARY KEY (device_id, timestamp)
);

COMMENT ON TABLE sensor_data IS 'Table for storing sensor data from devices';
COMMENT ON COLUMN sensor_data.device_id IS 'ID of the device that collected the data';
COMMENT ON COLUMN sensor_data.timestamp IS 'Timestamp of the data collection';
COMMENT ON COLUMN sensor_data.temperature IS 'Temperature reading from the device';
COMMENT ON COLUMN sensor_data.humidity IS 'Humidity reading from the device';
COMMENT ON COLUMN sensor_data.pollen IS 'Pollen count reading from the device';
COMMENT ON COLUMN sensor_data.particulate_matter IS 'Particulate matter reading from the device';

-- change table to hypertable
SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS device_thresholds (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    temperature_min DECIMAL(5, 2),
    temperature_max DECIMAL(5, 2),
    humidity_min DECIMAL(5, 2),
    humidity_max DECIMAL(5, 2),
    pollen_min INT,
    pollen_max INT,
    particulate_matter_min INT,
    particulate_matter_max INT,
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE device_thresholds IS 'Table for storing thresholds for devices';
COMMENT ON COLUMN device_thresholds.id IS 'Unique identifier for the device thresholds';
COMMENT ON COLUMN device_thresholds.temperature_min IS 'Minimum temperature threshold for the device';
COMMENT ON COLUMN device_thresholds.temperature_max IS 'Maximum temperature threshold for the device';
COMMENT ON COLUMN device_thresholds.humidity_min IS 'Minimum humidity threshold for the device';
COMMENT ON COLUMN device_thresholds.humidity_max IS 'Maximum humidity threshold for the device';
COMMENT ON COLUMN device_thresholds.pollen_min IS 'Minimum pollen count threshold for the device';
COMMENT ON COLUMN device_thresholds.pollen_max IS 'Maximum pollen count threshold for the device';
COMMENT ON COLUMN device_thresholds.particulate_matter_max IS 'Maximum particulate matter threshold for the device';
COMMENT ON COLUMN device_thresholds.last_updated IS 'Timestamp of the last update to the thresholds';
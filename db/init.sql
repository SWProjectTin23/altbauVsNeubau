CREATE TABLE IF NOT EXISTS sensor_data (
    device_id INT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    pollen INT,
    particulate_matter INT,
    PRIMARY KEY (device_id, timestamp)
);

-- change table to hypertable
SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS thresholds (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    temperature_min_soft DECIMAL(5, 2),
    temperature_max_soft DECIMAL(5, 2),
    temperature_min_hard DECIMAL(5, 2),
    temperature_max_hard DECIMAL(5, 2),
    humidity_min_soft DECIMAL(5, 2),
    humidity_max_soft DECIMAL(5, 2),
    humidity_min_hard DECIMAL(5, 2),
    humidity_max_hard DECIMAL(5, 2),
    pollen_min_soft INT,
    pollen_max_soft INT,
    pollen_min_hard INT,
    pollen_max_hard INT,
    particulate_matter_min_soft INT,
    particulate_matter_max_soft INT,
    particulate_matter_min_hard INT,
    particulate_matter_max_hard INT,
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
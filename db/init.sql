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


-- DEVICE 1
INSERT INTO sensor_data (device_id, timestamp, temperature, humidity, pollen, particulate_matter) VALUES
(1, NOW() - INTERVAL '5 hours', 22.5, 45.0, 50, 12),
(1, NOW() - INTERVAL '4 hours', 23.0, 47.5, 55, 14),
(1, NOW() - INTERVAL '3 hours', 24.1, 50.0, 60, 15),
(1, NOW() - INTERVAL '2 hours', 25.2, 52.0, 70, 18),
(1, NOW() - INTERVAL '1 hour', 26.5, 55.5, 80, 20);

-- DEVICE 2
INSERT INTO sensor_data (device_id, timestamp, temperature, humidity, pollen, particulate_matter) VALUES
(2, NOW() - INTERVAL '5 hours', 19.0, 35.0, 20, 5),
(2, NOW() - INTERVAL '4 hours', 20.2, 37.5, 25, 7),
(2, NOW() - INTERVAL '3 hours', 21.3, 40.0, 30, 9),
(2, NOW() - INTERVAL '2 hours', 22.0, 42.0, 40, 11),
(2, NOW() - INTERVAL '1 hour', 23.1, 44.5, 45, 13);

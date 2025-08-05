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


DELETE FROM thresholds;
INSERT INTO thresholds (temperature_min_soft, temperature_max_soft, temperature_min_hard, temperature_max_hard,
                        humidity_min_soft, humidity_max_soft, humidity_min_hard, humidity_max_hard,
                        pollen_min_soft, pollen_max_soft, pollen_min_hard, pollen_max_hard,
                        particulate_matter_min_soft, particulate_matter_max_soft, particulate_matter_min_hard, particulate_matter_max_hard) VALUES
(18.00, 28.00, 15.00, 32.00,
 40.00, 80.00, 30.00, 70.00,
 10, 70, 5, 80,
 20, 80, 10, 60);

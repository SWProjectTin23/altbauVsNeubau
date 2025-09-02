# Database Architecture Documentation

## Overview
This document outlines the database schema designed to store and manage environmental sensor data and their corresponding warning thresholds. The architecture leverages TimescaleDB, an extension for PostgreSQL, to efficiently handle time-series data, making it ideal for continuous sensor readings.

The database consists of several primary tables: `sensor_data` for storing raw sensor readings over time, `thresholds` for defining configurable warning and critical limits, and additional tables for alerting logic (`alert_emails`, `alert_cooldowns`).

## Initialization & Docker Compose Integration

The database is provisioned using the official TimescaleDB Docker image.  
In the `docker-compose.yml`, the database service is defined as follows:

```yaml
db:
  image: timescale/timescaledb:latest-pg14
  container_name: altbau_vs_neubau_db
  environment:
    - POSTGRES_USER=${DB_USER}
    - POSTGRES_PASSWORD=${DB_PASSWORD}
    - POSTGRES_DB=${DB_NAME}
  ports:
    - "5432:5432"
  volumes:
    - ./db/init.sql:/docker-entrypoint-initdb.d/01_init.sql:ro
    - ./db/availability_sensor.sql:/docker-entrypoint-initdb.d/02_availability_sensor.sql:ro
    - db_data:/var/lib/postgresql/data
  networks:
    - pg-network
  healthcheck:
    test: ["CMD-SHELL", "psql -U ${DB_USER} -d ${DB_NAME} -c 'SELECT 1;' || exit 1"]
    interval: 5s
    timeout: 3s
    retries: 10
    start_period: 60s
```

**Important:**  
The `init.sql` script is only executed **once** when the database container is created for the first time (i.e., when the volume `db_data` is empty).  
If you restart or recreate the container and the volume already exists, PostgreSQL will **not** re-run the initialization scripts.  
Any schema changes or new tables must be created manually using SQL commands.

## 1. sensor_data Table

This table is the core of the time-series data storage. It's designed to capture readings from various devices at specific timestamps.

### Purpose
Stores historical and real-time sensor measurements, including temperature, humidity, pollen count, and particulate matter levels, associated with a specific device and timestamp.

```sql
CREATE TABLE IF NOT EXISTS sensor_data (
    device_id INT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    pollen INT,
    particulate_matter INT,
    PRIMARY KEY (device_id, timestamp)
);

-- Convert to hypertable for TimescaleDB
SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);
```

### Key Characteristics
- `device_id` (INT, NOT NULL): Unique identifier for the sensor device. Part of the composite primary key.
- `timestamp` (TIMESTAMPTZ, NOT NULL): The exact time the sensor reading was taken, including timezone information. Also part of the composite primary key and the time-series dimension for TimescaleDB.
- `temperature`, `humidity` (DECIMAL(5, 2)): Sensor readings with two decimal places.
- `pollen`, `particulate_matter` (INT): Integer sensor readings.
- Primary Key: Composite on `(device_id, timestamp)` ensures one reading per device per moment.

## 2. thresholds Table

This table provides a flexible mechanism to define and manage warning and critical limits for the sensor readings.

### Purpose
Stores configurable "soft" (warning) and "hard" (critical) thresholds for each environmental parameter. These values can be used by the application to trigger alerts or visualize data against defined limits.

### Schema
```sql
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
```

### Key Characteristics

- *_min_soft / *_max_soft: Lower and upper bounds for "soft" warnings.
- *_min_hard / *_max_hard: Lower and upper bounds for "hard" critical alerts.
- `last_updated`: Timestamp of last modification.

## 3. alert_emails Table

Stores email address for alert notifications, including confirmation status and tokens for double-opt-in.

```sql
CREATE TABLE IF NOT EXISTS alert_emails (
    email VARCHAR(255) NOT NULL,
    confirmed BOOLEAN DEFAULT FALSE,
    confirmation_token VARCHAR(64),
    PRIMARY KEY (email)
);
```

## 4. alert_cooldowns Table

Tracks cooldowns for alert notifications to avoid spamming users.

```sql
CREATE TABLE IF NOT EXISTS alert_cooldowns (
    device VARCHAR(50) NOT NULL,
    metric VARCHAR(50) NOT NULL,
    mail_type VARCHAR(10) NOT NULL,
    last_sent TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (device, metric, mail_type)
);
```

## Data Initialization

The `init.sql` script also inserts default threshold values:

```sql
DELETE FROM thresholds;
INSERT INTO thresholds (temperature_min_hard, temperature_min_soft, temperature_max_soft, temperature_max_hard,
                        humidity_min_hard, humidity_min_soft, humidity_max_soft, humidity_max_hard,
                        pollen_min_hard, pollen_min_soft, pollen_max_soft, pollen_max_hard,
                        particulate_matter_min_hard, particulate_matter_min_soft, particulate_matter_max_soft, particulate_matter_max_hard) VALUES
(15.00, 18.00, 26.00, 32.00,
 30.00, 40.00, 60.00, 80.00,
 0, 5, 30, 80,
 0, 20, 50, 70);
```

## Manual Schema Changes

**Note:**  
If you need to add, remove, or modify tables after the initial container creation, you must do so manually using SQL commands (e.g., via `psql` or a database GUI).  
Re-running the container will **not** apply changes from `init.sql` unless the database volume is deleted and recreated.

## Visual Representation of the Database Structure

![Database schema](../images/db_diagramm.svg)

## Summary of Docker Compose Integration

- The database is deployed as a TimescaleDB container.
- Initialization scripts are only run once, on first volume creation.
- All other services (API, MQTT, Frontend, Monitoring) connect to the database via the defined Docker network (`pg-network`).
- Persistent data is stored in the `db_data` volume.
- Healthchecks ensure the database is ready before dependent services start.
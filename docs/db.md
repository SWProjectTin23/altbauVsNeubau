# Database Architekture Documentation

## Overview
This document outlines the database schema designed to store and manage environmental sensor data and their corresponding warning thresholds. The architecture leverages TimescaleDB, an extension for PostgreSQL, to efficiently handle time-series data, making it ideal for continuous sensor readings.

The database consists of two primary tables: sensor_data for storing raw sensor readings over time, and thresholds for defining configurable warning and critical limits for these readings.

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
```

### Key Characteristics
- device_id (INT, NOT NULL): Unique identifier for the sensor device. This is part of the composite primary key.
- timestamp (TIMESTAMPTZ, NOT NULL): The exact time the sensor reading was taken, including timezone information. This is also part of the composite primary key and is the time-series dimension for TimescaleDB.
- temperature (DECIMAL(5, 2)): Temperature reading, allowing for two decimal places.
- humidity (DECIMAL(5, 2)): Humidity reading, allowing for two decimal places.
- pollen (INT): Pollen count.
- particulate_matter (INT): Particulate matter (e.g., PM2.5, PM10) reading.
- Primary Key: A composite primary key on (device_id, timestamp) ensures that each device has only one reading per specific moment in time.

### TimescaleDB Integration
The sensor_data table is converted into a hypertable using the following command:

```sql
SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);
```

This conversion optimizes the table for time-series data by partitioning it based on the timestamp column, significantly improving query performance for time-based operations (e.g., aggregations over time ranges, data retention policies).

## 2. thresholds Table
This table provides a flexible mechanism to define and manage warning and critical limits for the sensor readings.

### Purpose
Stores configurable "soft" (warning) and "hard" (critical) thresholds for each environmental parameter. These values can be used by the application to trigger alerts or visualize data against defined limits.

### Schema
```sql
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
```

### Key Characteristics

* id (INT, PRIMARY KEY, GENERATED ALWAYS AS IDENTITY): A unique identifier for each set of thresholds. GENERATED ALWAYS AS IDENTITY ensures automatic, sequential ID generation.
* *_min_soft / *_max_soft: Define the lower and upper bounds for "soft" warnings. Readings outside this range might trigger a minor alert.
* *_min_hard / *_max_hard: Define the lower and upper bounds for "hard" critical alerts. Readings outside this range indicate a significant issue.
* temperature, humidity (DECIMAL(5, 2)): Thresholds for temperature and humidity, with two decimal places.
* pollen, particulate_matter (INT): Thresholds for pollen and particulate matter, as integer values.
* last_updated (TIMESTAMPTZ, DEFAULT CURRENT_TIMESTAMP): Automatically records the last time this specific set of thresholds was modified.

## Visual Representation of the Database Structure
To further illustrate the database architecture, you can insert a graphic here that depicts the relationships between the tables. Since I cannot directly generate or embed images, you can use a placeholder here and add the graphic manually.

![Databank schema](./images/db_diagramm.svg)
# 9. Introduction of a Dedicated Devices Table (devices)

Date: 2025-07-30

## Status

Accepted

## Context

Currently, sensor data is stored in the sensor_data table, and thresholds for this data are in the device_thresholds table. Both tables include a device_id. There's a need to improve data integrity and ensure that only device_ids that genuinely exist are used. With the current structure, where device_id in sensor_data is part of a composite primary key ((device_id, timestamp)), it's not possible to establish a foreign key from device_thresholds to sensor_data. This leads to potential inconsistencies (e.g., thresholds for non-existent devices) and complicates central device management.

### Alternatives Considered
**Keeping only two tables:** This simpler approach avoids the overhead of a third table. However, it means the database cannot enforce referential integrity between device_ids in sensor_data and device_thresholds. Data consistency would rely entirely on application-level logic, increasing the risk of orphaned or invalid entries, especially as the system scales or multiple applications interact with the database.

## Decision

We will introduce a third table named devices.

* The devices table will be the unique source for all device_ids in the database.
* device_id will be the primary key in the devices table.
* Both the sensor_data and device_thresholds tables will include a foreign key referencing devices.device_id.
* These foreign keys will be configured with ON DELETE CASCADE and ON UPDATE CASCADE.

## Consequences

* **Database Schema Change:** The database schema will need to be extended with a new table, and existing tables will be updated with foreign keys. This requires a migration strategy if the database is already in production.
* **Application Logic:** The application logic for creating and deleting devices must be adapted to first create entries in the devices table before sensor data can be sent or thresholds can be set.
* **Performance:** There will be a minor impact due to additional join operations for queries that require device information, but this is typically offset by indexing and outweighed by the improved data integrity.
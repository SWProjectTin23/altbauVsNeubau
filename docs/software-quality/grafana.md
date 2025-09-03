# 📖 Documentation: Sensor Data Monitoring with Grafana & TimescaleDB

## 1. Overview
This project provides a monitoring stack for IoT sensor data. It ingests sensor readings via MQTT, stores them in a TimescaleDB (PostgreSQL with time-series extensions), and visualizes data in Grafana.  

The focus of the dashboards is on **availability analysis** – comparing the expected number of sensor messages with the actual count and highlighting data gaps.  
Additionally, the system shows **per-sensor availability** (temperature, humidity, pollen, particulate matter) per device.

---

## 2. Data Source Configuration
Grafana is preconfigured with a PostgreSQL datasource pointing to TimescaleDB.

**`grafana/provisioning/datasources/datasource.yaml`:**

```yaml
apiVersion: 1

datasources:
  - name: TimescaleDB
    type: postgres
    access: proxy
    url: db:5432
    user: ${DB_USER}
    secureJsonData:
      password: ${DB_PASSWORD}
    jsonData:
      database: ${DB_NAME}
      sslmode: disable
      postgresVersion: 14
      timescaledb: true
```

- **Datasource name**: `TimescaleDB`  
- **UID**: `timescaledb` (used inside dashboards)  
- **Authentication**: via environment variables `${DB_USER}` and `${DB_PASSWORD}`

---

## 3. Availability Dashboard
The `Availability.json` file defines a Grafana dashboard that tracks sensor data availability.

### Panels
1. **Expected Values (per device)**  
   ```sql
   SELECT expected_total AS value 
   FROM v_totals_since_start_by_device 
   WHERE device_id = <id>;
   ```
   - Shows how many messages *should* have been received since the start.

2. **Actual Values (per device)**  
   ```sql
   SELECT actual_total AS value 
   FROM v_totals_since_start_by_device 
   WHERE device_id = <id>;
   ```
   - Displays the number of messages that were actually ingested.

3. **Availability Gauge**  
   ```sql
   SELECT availability_pct AS value 
   FROM v_totals_since_start_by_device 
   WHERE device_id = <id>;
   ```
   - Visualizes the percentage of received messages (`actual / expected`).  
   - Thresholds:  
     - <70% = red  
     - ≥70% = green  

4. **Per-Sensor Table (per device & sensor)**  
   ```sql
   SELECT device_id, sensor, expected_total, actual_count, availability_pct
   FROM v_counts_since_start_by_device_and_sensor
   ORDER BY device_id, sensor;
   ```
   - Shows expected vs. actual counts and availability percentage for each individual sensor column.  

5. **Gap Table**  
   ```sql
   SELECT device_id, gap_start, gap_end, gap_duration 
   FROM v_sensor_gaps 
   ORDER BY device_id, gap_start;
   ```
   - Lists all detected communication gaps longer than 10 minutes.  
   - `gap_duration` is displayed in seconds.

### Layout
- Top rows: Device 1 & Device 2 – Expected, Actual, Availability  
- Middle: Per-Sensor availability table  
- Bottom: Table with gap events across all devices  

---

## 4. Database Views
The dashboard depends on the following **database views** (must be created in SQL scripts):

- **`v_totals_since_start_by_device`**  
  Provides `expected_total`, `actual_total`, and `availability_pct` per device.  
  - `expected_total`: Expected number of rows based on device frequency.  
  - `actual_total`: Count of rows actually inserted.  
  - `availability_pct`: `(actual_total / expected_total) * 100`.

- **`v_counts_since_start_by_device_and_sensor`**  
  Provides `expected_total`, `actual_count`, and `availability_pct` per sensor column (temperature, humidity, pollen, particulate_matter).  

- **`v_sensor_gaps`**  
  Lists communication gaps longer than 10 minutes with start/end timestamps and duration.

---

## 5. Usage Instructions
1. Start the stack:
   ```bash
   docker compose up -d
   ```
2. Open Grafana: [http://localhost:3003](http://localhost:3003)  
3. Open the dashboard **“Sensor Availability”**.  
4. Observe per-device and per-sensor availability and data gaps.

---

## 6. Maintenance Notes
- Ensure TimescaleDB hypertables and indexes are created:
  ```sql
  SELECT create_hypertable('sensor_data', 'ts', if_not_exists => TRUE);
  CREATE INDEX IF NOT EXISTS idx_sensor_ts ON sensor_data (ts DESC);
  ```
- Check service health in **Uptime Kuma** at [http://localhost:3002](http://localhost:3002).

---

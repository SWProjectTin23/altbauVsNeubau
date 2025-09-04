# Uptime Kuma Setup & Monitor Import



## Overview

This document explains how to set up Uptime Kuma in an environment where:
- The database is **not mounted** (data is not persistent).
- No status page is used.
- Monitor configuration is restored manually from a JSON backup (`Uptime_Kuma.json`).

---

## Step 1: Start the Container

Deploy Uptime Kuma (e.g., via Docker or docker-compose). Since the database is not persisted, each container restart starts with a clean state.

---

## Step 2: Create Admin User

1. Open the Uptime Kuma web interface (default: `http://localhost:3001` or mapped port).  
2. On first launch, you will be prompted to **create a new user** (username + password).  
3. Save these credentials in a secure location (e.g., password manager, team vault).  
   > Without persistence, this step is required every time you restart the container.

---

## Step 3: Import Monitor Configuration

1. Log in with the user created above.  
2. In the left sidebar, click on your **user name**.  
3. Select **Settings**.  
4. Open the **Backup** tab.  
5. Click **Restore Backup**, then upload the JSON file:  
   - `Uptime_Kuma.json`  

This file contains all defined monitors.

---

## Step 4: Verify Monitors

After import, you should see the following monitors in the dashboard:

| Monitor Name  | Type  | Target                        |
|---------------|-------|-------------------------------|
| Frontend      | HTTP  | `http://frontend:80`          |
| Backend-API   | HTTP  | `http://backend-api:5000/`    |
| Database      | TCP   | `db:5432`                     |
| MQTT          | TCP   | `isd-gerold.de:1883`          |
| Grafana       | HTTP  | `http://grafana:3000`         |
| Prometheus    | HTTP  | `http://prometheus:9090`      |
| MQTT Backup   | TCP   | `hrschmllr.de:1883`           |
| Loki          | HTTP  | `http://loki:3100/ready`      |

---

## Step 5: Start Monitoring

- Once imported, all monitors can be started.  
- You can view real-time status, uptime history, and response times in the dashboard.  
- If needed, adjust intervals, retries, or notification settings manually for each monitor.

---

## Notes

- Since the database is not persisted:
  - User credentials and monitor configuration must be restored after **every restart**.  
  - Always keep the latest backup JSON available.  

---

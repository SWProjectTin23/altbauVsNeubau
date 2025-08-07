# Uptime Monitoring Documentation

## Overview

This document describes the current uptime monitoring setup, including which services are being monitored, the tools in use, and the availability of a centralized monitoring dashboard.

## Monitoring Tools

### Uptime Kuma (internal)
- Self-hosted monitoring tool deployed via Docker.
- Monitors internal services that are not publicly accessible.
- Accessible internally via: `http://localhost:3002` (or equivalent internal network address).
- Status page available at: `http://localhost:3002/status/dashboard`
- Stores monitoring history and configuration in a local SQLite database (`kuma.db`).
- **Important:** By default, `kuma.db` is stored inside the container and is not persistent unless explicitly mounted. All configuration and monitoring data will be lost if the container is removed. Regular export is required.
- Alerts configured via Telegram and/or email.

### Uptime Robot (external)
- SaaS-based monitoring service.
- Used to verify availability of publicly exposed endpoints.
- Sends alerts via email.

## Monitored Services

| Service                  | Type         | Monitored by       | URL / Host                          |
|--------------------------|--------------|--------------------|-------------------------------------|
| Frontend (Web App)       | HTTP         | Kuma | http://localhost:3000  |
| Backend API              | HTTP         | Kuma | http://localhost:5001  |
| Database (TimescaleDB)   | TCP          | Kuma               | tcp://localhost:5432               |
| Uptime Kuma      | HTTP         | Uptime Robot | http://localhost:3002  |

> Note: Internal services are only monitored by Uptime Kuma. Kuma is monitored externally by Uptime Robot.

## Dashboard

A web-based dashboard is provided via Uptime Kuma, giving real-time and historical views of:
- Service availability (up/down)
- Response time trends
- Outage history
- Uptime percentages per service

URL (internal): `http://localhost:3002`  
Status Page: `http://localhost:3002/status/dashboard`  
Access is restricted to trusted internal users or secured via reverse proxy authentication if exposed externally.


## Exporting the Uptime Kuma Database

To back up or move the internal monitoring configuration and history stored in the `kuma.db` database, run the following command from your host system (replace `uptime-kuma` with your container name if different):

```bash
docker cp uptime-kuma:/app/data/kuma.db ~/Desktop/kuma.db

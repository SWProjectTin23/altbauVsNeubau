# Loki & Promtail Logging Setup

This document describes how to set up a **Loki + Promtail logging stack** using **Docker Compose**.  
Additionally, a pre-configured **Grafana dashboard (`logging-overview.json`)** is provided to visualize log levels and messages.

---



## Services Overview

### Loki
[Loki](https://grafana.com/oss/loki/) is a log aggregation system by Grafana, optimized for storing and querying logs.  

**Docker Compose Service:**
```yaml
loki:
  image: grafana/loki:2.9.6
  command: -config.file=/etc/loki/config.yml
  ports:
    - "3100:3100"
  volumes:
    - ./loki/loki-config.yml:/etc/loki/config.yml:ro 
    - loki-data:/loki
  networks:
    - pg-network
  restart: unless-stopped
```

**Details:**
- **Image:** `grafana/loki:2.9.6`  
- **Port:** Exposes `3100` → [http://localhost:3100](http://localhost:3100)  
- **Config file:** Mounted from `./loki/loki-config.yml`  
- **Storage:** Uses `loki-data` volume for persistence  
- **Network:** Connected to `pg-network`  
- **Restart policy:** Restart unless stopped  

---

### Promtail
[Promtail](https://grafana.com/docs/loki/latest/clients/promtail/) is an agent that collects logs and ships them to Loki.  

**Docker Compose Service:**
```yaml
promtail:
  image: grafana/promtail:2.9.6
  command: -config.file=/etc/promtail/config.yml
  volumes:
    - ./loki/promtail-config.yml:/etc/promtail/config.yml:ro 
    - /var/run/docker.sock:/var/run/docker.sock:ro           
    - promtail-data:/tmp
  depends_on:
    - loki
  networks:
    - pg-network
  restart: unless-stopped
```

**Details:**
- **Image:** `grafana/promtail:2.9.6`  
- **Config file:** Mounted from `./loki/promtail-config.yml`  
- **Docker socket:** `/var/run/docker.sock` → reads logs from all containers  
- **Temporary data:** Uses `promtail-data` volume  
- **Dependency:** Starts only after Loki is running  
- **Restart policy:** Restart unless stopped  

---



---

## Grafana Dashboard: Logging Overview

The provided `Logging.json` is a **Grafana dashboard** that visualizes logs from Loki.

### Features
- **Log Level Counters:**
  - Critical
  - Error
  - Warning
  - Info
- **Totals Table:** Displays aggregated log level counts  
- **Log Explorer:** Lists detailed Critical / Error / Warning messages with labels  
- **Environment Selector (`$env`):** Filter logs by environment  
- **Auto-refresh:** Updates every 10 seconds  

### Import Instructions
1. Open Grafana → [http://localhost:3000](http://localhost:3000)  
2. Navigate to **Dashboards → Import**  






---

## Conclusion

With this setup you get:
- A **Loki instance** for log storage  
- A **Promtail agent** collecting container logs  
- A **Grafana dashboard** for monitoring & exploration  

This provides a robust logging infrastructure for your Docker environment.  

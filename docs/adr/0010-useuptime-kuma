# 10. Introduction of Uptime Kuma and Uptime Robot for Service Availability Monitoring

**Date:** 2025-08-07

## Status

Accepted

## Context

Currently, there is no consistent or centralized method in place for monitoring the availability of internal and external services (e.g., APIs, frontend, MQTT, database). Outages may go unnoticed or are only discovered reactively. A reliable monitoring solution is required to detect downtimes early, notify the team, and provide historical uptime tracking.

The chosen solution should:
- Be easy to deploy and maintain
- Support internal and external monitoring
- Include alerting and a web-based status overview
- Be lightweight and suitable for integration into our Dockerized infrastructure

### Alternatives Considered

**1. Elasticsearch**  
Elasticsearch was considered as a logging and monitoring backend by storing availability checks and analyzing them via queries or dashboards. However, Elasticsearch is a heavyweight solution that consumes significant resources (CPU, memory, disk), especially in smaller deployments. For the relatively simple use case of availability monitoring, it is unnecessarily complex and resource-intensive.

**2. JMeter with Grafana**  
JMeter is a powerful tool for performance and load testing. It could be scheduled to perform uptime checks and push results into a time-series database (e.g., InfluxDB), visualized through Grafana. However, JMeter is not designed for continuous availability monitoring. It's best suited for short-term performance testing. The setup would also require additional components, increasing maintenance overhead.

**3. Uptime Robot (alone)**  
Uptime Robot is a reliable external SaaS uptime monitoring service. It works well for public endpoints but cannot access services running on local networks or behind firewalls. Therefore, it is insufficient as a standalone monitoring solution.

## Decision

We will use **Uptime Kuma** for internal monitoring and **Uptime Robot** for external validation.

- **Uptime Kuma** is a self-hosted, Docker-based uptime monitoring tool that supports HTTP(s), TCP, ping, and more. It will be deployed internally and used to monitor all local services.
- **Uptime Robot** will be used in parallel to perform external monitoring of publicly reachable endpoints (e.g., production APIs, website).
- Alerts from both systems will be configured via email and Telegram where possible.

## Consequences

- **Full Coverage:** We gain visibility into both internal and external service availability.
- **Simple Maintenance:** Uptime Kuma is lightweight and runs as a single Docker container with persistent storage (`kuma.db`).
- **Low Overhead:** No need for complex data pipelines, custom scripting, or multi-container observability stacks.
- **Alerting and Dashboard:** Web UI and real-time alerts are available without additional tools.
- **Security Considerations:** Internal access to Uptime Kuma will be restricted to trusted networks or secured via reverse proxy.

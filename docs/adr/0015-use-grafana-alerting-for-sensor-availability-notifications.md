# Use Grafana Alerting for Sensor Availability Notifications

**Date:** 2025-08-20

## Status

Accepted

## Context

Continuous monitoring of sensor data availability is essential for system reliability. While Grafana dashboards (see [ADR-14](0014-use-grafana-for-sensor-uptime-monitoring.md)) provide real-time visibility, operators also need **proactive notifications** when sensors go offline or data gaps occur.

Sensor availability is determined by an **external service** (`exporter.py`), which exposes Prometheus metrics (`sensor_seconds_since_last_data`) for each individual sensor. This allows us to monitor the availability of every single sensor in the system.

Several alerting solutions were considered:

### Alternatives Considered

**1. Custom Notification Service:**  
A bespoke service could monitor TimescaleDB and send alerts via email or messaging platforms. This approach offers flexibility but requires additional development, integration, and maintenance.

**2. Prometheus Alertmanager:**  
Prometheus Alertmanager is widely used for metric-based alerting. However, our main sensor data source is TimescaleDB, and integrating Alertmanager would add complexity.

**3. Grafana Unified Alerting:**  
Grafana’s built-in alerting system supports multiple datasources, including Prometheus and PostgreSQL. It allows rule-based notifications, integrates with dashboards, and supports email, Slack, and other channels.

## Decision

We will use **Grafana Unified Alerting** for sensor availability notifications.

- Sensor availability is monitored by the external service `exporter.py`, which provides Prometheus metrics for each sensor.
- Alert rules are defined in Grafana based on these metrics (e.g., `sensor_seconds_since_last_data`).
- The availability of **each individual sensor** is checked, and alerts are triggered if any sensor becomes unavailable.
- Configure email notifications for responsible operators.
- Integrate alert summaries directly into dashboard panels for context.
- Provision alerting resources via code for reproducibility and version control.

This approach leverages our existing Grafana deployment (see [ADR-14](0014-use-grafana-for-sensor-uptime-monitoring.md)), minimizes operational overhead, and provides a unified monitoring and alerting experience.

## Consequences

* **Consistent User Experience:** Operators use a single interface for both dashboards and notifications.
* **Scalable:** Alerting rules and contact points can be extended as requirements evolve.
* **Maintainable:** Alerting configuration is versioned and provisioned alongside dashboards.
* **Granular Monitoring:** The availability of every individual sensor is tracked and alerted on, improving reliability and transparency.
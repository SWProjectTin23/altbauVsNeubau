# 10. Use Grafana Loki for logging

**Date:** 2025-08-08

## Status

Accepted

## Context

Our project consists of a React frontend, a Flask backend, and a PostgreSQL database. As we prepare for production deployment, we want to introduce centralized logging to capture errors, warnings, and important system events in a consistent and queryable manner.

The goal is to implement a lightweight, extensible logging solution that can run both locally and in the cloud. The solution should collect logs from the Flask backend and provide centralized search and visualization capabilities.

### Alternatives Considered

**1. Sentry (Self-hosted):**  
Sentry offers powerful error tracking and performance monitoring. However, the self-hosted version is relatively heavy (multiple services, large Docker images, complex setup), making it an overkill for our current needs.

**2. ELK Stack (Elasticsearch, Logstash, Kibana):**  
A well-established logging stack with powerful capabilities. However, it is resource-intensive and complex to operate. Elasticsearch requires significant memory and storage, and Logstash adds additional overhead.

**3. JSON Logging + External Tools:**  
Structured logging with JSON enables better machine parsing, but for our current needs (quick setup, human-readable logs, small team), plain text is more practical. JSON logging remains a viable upgrade path if structured querying becomes necessary.

## Decision

We will implement a logging stack based on:

- **Flask** writing log messages to a local file (`app.log`) in **plain text format**
- **Promtail**, which reads the log file and attaches metadata (labels)
- **Grafana Loki**, which receives and stores the logs for indexed, time-based querying
- **Grafana**, used to visualize and explore the logs via a web UI


## Consequences

* **Low Complexity:** The setup is lightweight, easy to run locally, and does not require complex infrastructure like Elasticsearch or Kubernetes.
* **Fast Log Search:** Loki enables fast text-based search across logs using labels and timestamps directly within Grafana.
* **Limited Structure:** Plain text logs are easy for developers to read but provide limited capabilities for structured analysis. This can be mitigated later by switching to JSON.
* **Scalability:** The system can be extended to include additional services or logging sources without major architectural changes.
* **Unified Monitoring Platform:** Since we are already using Grafana, we can later integrate metrics and tracing alongside logs in a single interface.

## Extension: Frontend Logging (React)

Although the initial logging stack covers only the Flask backend, it's also important to capture logs from the React frontend.

### Goals for Frontend Logging

- Capture JavaScript runtime errors
- Log user actions or client-side events (optional)
- Report performance issues (optional)

### Decision

The React frontend will send relevant logs to the Flask backend via HTTP. Flask will then write these logs to the same local log file (`app.log`) used by backend logs. Promtail will continue to read from this file and forward all logs to Loki.

- A simple logging function in React will capture errors (e.g. via `window.onerror` or a custom logger).
- Logs are sent to an endpoint like `POST /frontend-log` on the Flask server.
- The Flask endpoint will parse and log the message (with proper labels like `[FE]` or `source=frontend`).
- Promtail will include these in its scrape targets, so frontend logs appear in Grafana.

### Alternatives Considered

**Direct Loki Push from React:** Requires Loki to be exposed or proxied, plus authentication, which adds security and complexity concerns. This was rejected in favor of a simpler backend relay.

**Using an external tool (e.g. Sentry, LogRocket):** More powerful for production debugging, but heavier and often cloud-bound. Our stack prioritizes self-hosting and simplicity.

### Consequences

- **Unified Logging:** Both backend and frontend logs will be searchable in the same Grafana interface.
- **Simple Setup:** No additional infrastructure required.
- **Extensible:** If needed, we can later structure frontend logs as JSON or include user/session metadata.

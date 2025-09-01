# Use MQTT as Communication Protocol

**Date:** 2025-07-25

## Status

Accepted (externally specified)

## Context

In this project, microcontrollers (e.g., Arduino MKR WiFi 1010) send sensor data to a central backend. The transmission uses the MQTT protocol and a predefined JSON format containing timestamped measurement values and metadata such as firmware version and startup time:

```json
{
  "timestamp": "1753098733",
  "value": 23.4,
  "sequence": 123,
  "meta": {
    "firmware": "v1.2.3",
    "startup": "1753098730"
  }
}
```

The MQTT topic structure is also specified externally and follows this pattern:

```
dhbw/ai/si2023/<group-number>/<sensor-type>/<sensor-id>
```

The use of MQTT was mandated by external stakeholders and is considered a project requirement.

## Alternatives Considered

No internal alternatives were evaluated, as MQTT was preselected and imposed externally.

## Decision

We will use **MQTT** as the communication protocol between Arduino-based sensors and the backend system.

## Consequences

- MQTT is lightweight, well-suited for IoT scenarios, and broadly supported in the Python ecosystem.
- The predefined message format and topic structure simplify integration on both sender and receiver sides.
- Security considerations (such as authentication and TLS encryption) may need to be added separately, as MQTT does not enforce them by default.

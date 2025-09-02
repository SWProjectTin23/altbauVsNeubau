# Arduino Code Documentation

This document describes the structure and functionality of the Arduino scripts in the **altbauVsNeubau** project.

## Overview

The Arduino scripts are responsible for collecting sensor data and sending it to the central backend via the MQTT protocol.

## Main Functions

- **Sensor Initialization:** All connected sensors are initialized in the `setup()` block (`tempsensorStartup()`, `humiditySensorStartup()`).
- **WiFi Connection:** The board connects to the configured WiFi network.
- **MQTT Connection:** Establishes and maintains a connection to the MQTT broker.
- **Data Acquisition:** In the `loop()` block, sensor values are read regularly (fine dust, temperature, humidity).
- **Message Format:** The sensor values are formatted as a JSON object (see [ADR 0008](../adr/0008-MQTT-communication-protocol.md)).
- **Publishing:** The JSON message is published to a project-specific MQTT topic.

## Example MQTT Message

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

## Important Files

- `arduino_sensor.ino`: Main program, contains setup and loop logic.
- `sensor_reader.cpp`: Sensor reading and averaging logic for fine dust, temperature, and humidity.
- `WifiUtils.cpp` and `MQTTUtils.cpp`: Handle WiFi and MQTT communication.
- `secrets.h`: Contains credentials for WiFi and MQTT (excluded from the repository via `.gitignore`).

## Notes

- **Credentials:** WiFi and MQTT credentials should never be published in the repository. The `secrets.h` file is excluded via `.gitignore`.
- **Adding New Sensors:** Please follow the existing structure and message format when integrating new sensors.

Example `secrets.h`:
```cpp
#ifndef SECRETS_H
#define SECRETS_H

#define WIFI_SSID "WIFI_SSID"
#define WIFI_PASS "WIFI_PASS"
#define MQTT_SERVER "MQTT_SERVER" 
#define MQTT_PORT "MQTT_PORT"
#define MQTT_SERVER2 "MQTT_SERVER2"
#define MQTT_PORT2 "MQTT_PORT2"
#define DEVICE_ID "DEVICE_ID"
#endif

```


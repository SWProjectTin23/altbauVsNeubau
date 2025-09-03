# Alerting Documentation

## Overview

This project uses Grafana's unified alerting system to monitor the availability of **all sensors** (not just Arduino devices). Alerts are triggered when any sensor has not sent data for a defined period. Notifications are sent via email to the configured recipients.

***

## Alert Rule

- **Location:** `grafana/provisioning/alerting/alert-rules.yaml`
- **Rule Name:** Sensor-offline
- **Condition:** The alert triggers if `sensor_seconds_since_last_data` for any sensor (any device and any sensor type) exceeds **600 seconds** (10 minutes).
- **Interval:** The rule is evaluated every 30 seconds.
- **Summary Message:**  
  The alert email contains the device ID, sensor type, and the number of seconds since the last data was received:
  ```
  Folgende Sensoren sind offline:
    Gerät: {{ .labels.device_id }}, Sensor: {{ .labels.sensor_type }}, Zeit: {{ .value }} Sekunden
  ```
  This ensures the exact offline duration for each sensor is shown in the notification.

***

## Contact Points

- **Location:** `grafana/provisioning/alerting/contact-points.yaml`
- **Default Email Receiver:**  
  - Recipients:  
    - hirschmillert.tin23@student.dhbw-heidenheim.de  
    - geroldj.tin23@student.dhbw-heidenheim.de
  - Multiple recipients are supported.
  - Notifications are sent for both firing and resolved alerts.

***

## Data Sources

- **Prometheus:**  
  Used for querying the metric `sensor_seconds_since_last_data` for all sensors.

***

## Dashboard Integration

- **Location:** `grafana/provisioning/dashboards/ArduinoAvailability.json`
- **Panels:**  
  - Stat and time series panels visualize the offline time for each sensor and device.
  - Thresholds are set to highlight sensors offline for more than 600 seconds.

***

## Customization

- **Threshold:**  
  Adjust the `params` value in the alert rule to change the offline threshold (default: 600 seconds).
- **Notification Message:**  
  Edit the `summary` field in the alert rule to customize the email content.

***

## Troubleshooting

- Ensure Prometheus is scraping the correct metrics for all sensors.
- Check that the email addresses in `contact-points.yaml` are valid.
- Verify that the alert rule is enabled and not paused.

***

## References

- [Grafana Alerting Documentation](https://grafana.com/docs/grafana/latest/alerting/)
- [Provisioning Alerting Resources](https://grafana.com/docs/grafana/latest/administration/provisioning/#alerting)
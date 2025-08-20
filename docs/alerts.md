# Alerting Documentation

## Overview

This project uses Grafana's unified alerting system to monitor the availability of Arduino devices. Alerts are triggered when a device has not sent data for a defined period. Notifications are sent via email to the configured recipients.

---

## Alert Rule

- **Location:** `grafana/provisioning/alerting/alert-rules.yaml`
- **Rule Name:** Arduino offline
- **Condition:** The alert triggers if `sensor_seconds_since_last_data` for any device exceeds 240 seconds.
- **Interval:** The rule is evaluated every 10 seconds.
- **Summary Message:**  
  The alert email contains the device ID and the number of seconds since the last data was received:
  ```
  Arduino {{ $labels.device_id }} offline seit {{ $values.C }} Sekunden
  ```
  This ensures the exact offline duration is shown in the notification.

---

## Contact Points

- **Location:** `grafana/provisioning/alerting/contact-points.yaml`
- **Default Email Receiver:**  
  - Recipients:  
    - hirschmillert.tin23@student.dhbw-heidenheim.de  
    - Gerold.tin23@student.dhbw-heidenheim.de
  - Multiple recipients are supported.
  - Notifications are sent for both firing and resolved alerts.

---

## Data Sources

- **Prometheus:**  
  Used for querying the metric `sensor_seconds_since_last_data`.

---

## Dashboard Integration

- **Location:** `grafana/provisioning/dashboards/ArduinoAvailability.json`
- **Panels:**  
  - Stat and time series panels visualize the offline time for each Arduino device.
  - Thresholds are set to highlight devices offline for more than 240 seconds.

---

## Customization

- **Threshold:**  
  Adjust the `params` value in the alert rule to change the offline threshold.
- **Notification Message:**  
  Edit the `summary` field in the alert rule to customize the email content.

---

## Troubleshooting

- Ensure Prometheus is scraping the correct metrics.
- Check that the email addresses in `contact-points.yaml` are valid.
- Verify that the alert rule is enabled and not paused.

---

## References

- [Grafana Alerting Documentation](https://grafana.com/docs/grafana/latest/alerting/)
- [Provisioning Alerting Resources](https://grafana.com/docs/grafana/latest/administration/provisioning/#alerting)

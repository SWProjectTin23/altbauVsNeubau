# Alerting Logic Documentation

## Overview

The alerting system ensures that users are notified via email when sensor values exceed configured thresholds.  
To prevent spam, a **state-based cooldown** is implemented:  
- Only one alert email is sent while the value remains outside the threshold.
- The cooldown is reset only when the value returns to the normal range.

## How It Works

1. **Frontend triggers `/send_alert_mail`** for every new value.
2. **Backend checks thresholds:**
   - If the value exceeds a "hard" or "soft" threshold, it checks if an alert is already active for that metric and device.
   - If no alert is active, an email is sent and the alert is marked as active (in the database).
   - If an alert is already active, no email is sent (cooldown).
3. **Cooldown reset:**
   - When the value returns to the normal range (i.e., within all thresholds), the alert is reset.
   - The next time the value exceeds a threshold, a new email will be sent.

## Email Content

- **Subject:**  
  `[HARD] Alert: Device Altbau - Temperatur`
- **Body:**  
  ```
  ALERT (HARD)

  Affected Device: Altbau
  Sensor/Metric: Temperatur

  Current Value: 35 °C

  Thresholds:
    Red Low: 10°C
    Yellow Low: 15°C
    Yellow High: 30°C
    Red High: 32°C

  The current value for Temperatur has exceeded the HARD threshold.
  Please check the air quality and ventilate the rooms or take further action if necessary.
  ```

## Example Workflow

1. Value rises above `redHigh` (e.g., 35 > 32):  
   → Email is sent, alert is active.
2. Value remains above `redHigh` (e.g., 36):  
   → No email sent, cooldown active.
3. Value drops below `redHigh` (e.g., 30):  
   → Cooldown is reset.
4. Value rises above `redHigh` again (e.g., 33):  
   → New email is sent.

## Logging

The backend logs every alert event:
- When an email is sent: `alert_mail.sent`
- When the cooldown is active: `alert_mail.cooldown_active`
- When the cooldown is reset: `alert_mail.reset`
- On errors or missing parameters: `alert_mail.missing_parameters`, `alert_mail.unknown_metric`, `alert_mail.process_error`

---

## Notes

- The alerting logic is **state-based**, not time-based.
- The frontend should call `/send_alert_mail` for every value update to ensure correct cooldown handling.
- All thresholds and alert email addresses can be managed via the API.

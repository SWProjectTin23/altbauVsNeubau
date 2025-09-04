# API Overview
This document describes the available REST API endpoints for the sensor backend.

Endpoints are under development and may change as needed.

## Base URL
`http://localhost:5001/api/`

---

## Endpoints

### 1. Get available time range

**GET** `/devices/range`

- Returns the earliest and latest available timestamps for all devices.

#### Example:
`http://localhost:5001/api/devices/range`

#### Success Response:
```json
{
  "status": "success",
  "data": [
    {
      "device_id": 1,
      "start": 1721736000,
      "end": 1721745000
    },
    {
      "device_id": 2,
      "start": 1721736300,
      "end": 1721744700
    }
  ]
}
```
#### No Data Response:
```json
{
  "status": "success",
  "message": "No time ranges found for any devices.",
  "data": []
}
```
#### Error Response:
```json
{
  "status": "error",
  "message": "A database error occurred while processing your request."
}
```

---

### 2. Get sensor data by device ID and time range

**GET** `/devices/<int:device_id>/data`

- Returns all available data for a specific device.
- Optional: time filters via query parameters.

#### Path Parameter:
- `device_id`: integer ID of the sensor device

#### Query Parameters:
- `start` *(optional)*: start timestamp in UNIX format
- `end` *(optional)*: end timestamp in UNIX format

#### Example:
`http://localhost:5001/api/devices/1/data?start=1721736000&end=1721745660`

#### Success Response:
```json
{
  "device_id": 1,
  "start": 1721736000,
  "end": 1721745660,
  "status": "success",
  "data": [
    {
      "device_id": 1,
      "humidity": 45.2,
      "particulate_matter": 28,
      "pollen": 10,
      "temperature": 22.1,
      "timestamp": 1721745600
    },
    {
      "device_id": 1,
      "humidity": 45.5,
      "particulate_matter": 30,
      "pollen": 11,
      "temperature": 22.3,
      "timestamp": 1721745660
    }
  ],
  "message": null
}
```
#### No Data Response:
```json
{
  "device_id": 1,
  "start": 1721736000,
  "end": 1721745660,
  "status": "success",
  "data": [],
  "message": "No data available for device 1 in the specified range."
}
```
#### Device Not Found Response:
```json
{
  "status": "error",
  "message": "Device with ID 999 does not exist."
}
```
#### Error Response:
```json
{
  "status": "error",
  "message": "A database error occurred while processing your request."
}
```

---

### 3. Get Latest Data for a Device

**GET** `/devices/<int:device_id>/latest`

- Returns the most recent data entry for a specific device.

#### Path Parameter:
- `device_id`: integer ID of the sensor device

#### Example:
`http://localhost:5001/api/devices/1/latest`

#### Success Response:
```json
{
  "status": "success",
  "data": {
    "device_id": 1,
    "humidity": 45.5,
    "particulate_matter": 30,
    "pollen": 11,
    "temperature": 22.3,
    "timestamp": 1721745660
  },
  "message": null
}
```
#### No Data Response:
```json
{
  "status": "success",
  "data": [],
  "message": "No data available for device 1."
}
```
#### Device Not Found Response:
```json
{
  "status": "error",
  "message": "Device with ID 999 does not exist."
}
```
#### Error Response:
```json
{
  "status": "error",
  "message": "A database error occurred while processing your request."
}
```

---

### 4. Comparison Between Devices over Time Range (Aggregated)

**GET** `/comparison`

- Returns the selected metric of two devices over a given time range.
- The data is aggregated in buckets (e.g., 100 average values per device) for efficient charting.

Note: If a device currently sends no data for the requested time range, its array will be empty. In that case no buckets with "value" entries are returned for that device (the frontend must handle empty arrays).


#### Query Parameters
- `device_1`: ID of first device (e.g., `1`)
- `device_2`: ID of second device (e.g., `2`)
- `metric`: one of `temperature`, `humidity`, `pollen`, `particulate_matter`
- `start`: Unix timestamp (optional)
- `end`: Unix timestamp (optional)
- `buckets`: *(optional, default: 300)* Number of buckets (average values) to return per device

#### Example:
`http://localhost:5001/api/comparison?device_1=1&device_2=2&metric=pollen&start=1721745600&end=1721745660&buckets=100`

#### Success Response:
```json
{
  "device_1": [
    { "timestamp": 1721745600, "value": 10 },
    { "timestamp": 1721745660, "value": 11 }
  ],
  "device_2": []],
  "metric": "pollen",
  "start": 1721745600,
  "end": 1721745660,
  "status": "success",
  "message": null
}
```
- Each array contains up to `buckets` entries, each representing the average value for that time bucket.

#### No Data Response:
```json
{
  "device_1": [],
  "device_2": [],
  "metric": "pollen",
  "start": 1721745600,
  "end": 1721745660,
  "status": "success",
  "message": "No data found for the specified devices and metric."
}
```
#### Error Responses:
```json
{
  "status": "error",
  "message": "Metric must be specified."
}
```
```json
{
  "status": "error",
  "message": "Both device IDs must be provided."
}
```
```json
{
  "status": "error",
  "message": "Invalid time range: <error description>"
}
```
```json
{
  "status": "error",
  "message": "An unexpected error occurred while processing your request."
}
```

---

### 5. Manage Thresholds
This endpoint allows you to retrieve and update the soft and hard thresholds for different sensor metrics (temperature, humidity, pollen, particulate matter).

**GET `/thresholds` - Returns the currently configured thresholds.**

#### Example
`http://localhost:5001/api/thresholds`

#### Success Response:
```json
{
  "status": "success",
  "data": {
    "temperature_min_soft": 12.0,
    "temperature_max_soft": 25.0,
    "temperature_min_hard": 15.0,
    "temperature_max_hard": 30.0,
    "humidity_min_soft": 10.0,
    "humidity_max_soft": 70.0,
    "humidity_min_hard": 20.0,
    "humidity_max_hard": 80.0,
    "pollen_min_soft": 5,
    "pollen_max_soft": 50,
    "pollen_min_hard": 10,
    "pollen_max_hard": 100,
    "particulate_matter_min_soft": 1,
    "particulate_matter_max_soft": 50,
    "particulate_matter_min_hard": 5,
    "particulate_matter_max_hard": 100
  },
  "message": "Thresholds retrieved successfully."
}
```

#### No Data Response:
```json
{
  "status": "success",
  "data": [],
  "message": "No thresholds available."
}
```

### Error Response:
```json
{
  "status": "error",
  "message": "A database error occurred while processing your request."
}
```
```json
{
  "status": "error",
  "message": "An unexpected error occurred while processing your request."
}
```
**POST `/thresholds`

#### The request body should be an JSON object containing the threshold values. All keys are required.
* `temperature_min_soft` (float): Soft minimum temperature threshold.
* `temperature_max_soft` (float): Soft maximum temperature threshold.
* `temperature_min_hard` (float): Hard minimum temperature threshold.
* `temperature_max_hard` (float): Hard maximum temperature threshold.
* `humidity_min_soft` (float): Soft minimum humidity threshold.
* `humidity_max_soft` (float): Soft maximum humidity threshold.
* `humidity_min_hard` (float): Hard minimum humidity threshold.
* `humidity_max_hard` (float): Hard maximum humidity threshold.
* `pollen_min_soft` (int): Soft minimum pollen threshold.
* `pollen_max_soft` (int): Soft maximum pollen threshold.
* `pollen_min_hard` (int): Hard minimum pollen threshold.
* `pollen_max_hard` (int): Hard maximum pollen threshold.
* `particulate_matter_min_soft` (int): Soft minimum particulate matter threshold.
* `particulate_matter_max_soft` (int): Soft maximum particulate matter threshold.
* `particulate_matter_min_hard` (int): Hard minimum particulate matter threshold.
* `particulate_matter_max_hard` (int): Hard maximum particulate matter threshold.

##### Validation Rules:
* For each metric, the `min_soft` value must be less than `max_soft`.
* For each metric, the `min_hard` value must be less than `max_hard`.
* For each metric, the `min_hard` value must be less than or equal to `min_soft`.
* For each metric, the `max_hard` value must be greater than or equal to `max_soft`.

#### Example Request Body:

```json
{
  "temperature_min_soft": 12.0,
  "temperature_max_soft": 25.0,
  "temperature_min_hard": 10.0,
  "temperature_max_hard": 28.0,
  "humidity_min_soft": 30.0,
  "humidity_max_soft": 60.0,
  "humidity_min_hard": 25.0,
  "humidity_max_hard": 65.0,
  "pollen_min_soft": 10,
  "pollen_max_soft": 70,
  "pollen_min_hard": 5,
  "pollen_max_hard": 80,
  "particulate_matter_min_soft": 5,
  "particulate_matter_max_soft": 40,
  "particulate_matter_min_hard": 2,
  "particulate_matter_max_hard": 50
}
```

#### Success Response:

```json
{
  "status": "success",
  "message": "Thresholds updated successfully."
}
```

#### Error Responses:

```json
{
  "status": "error",
  "message": "Invalid input data. Expecting a Dictionary."
}
```
```json
{
  "status": "error",
  "message": "Missing required key: 'temperature_min_soft'."
}
```
```json
{
  "status": "error",
  "message": "Value for 'temperature_min_soft' cannot be None."
}
```
```json
{
  "status": "error",
  "message": "Invalid value for 'temperature_min_soft': 'abc'. Expected type float."
}
```
```json
{
  "status": "error",
  "message": "Minimum value for 'temperature_min_soft' must be less than maximum value for 'temperature_max_soft'."
}
```
```json
{
  "status": "error",
  "message": "Hard threshold 'temperature_max_hard' must be greater than soft threshold 'temperature_max_soft'."
}
```
```json
{
  "status": "error",
  "message": "A database error occurred while processing your request."
}
```
```json
{
  "status": "error",
  "message": "An unexpected error occurred while processing your request."
}
```

## 6. Aler Email Management

### **GET `/alert_email`**

Returns the currently configured alert email address for the thresholds.

**Example:**
`http://localhost:5001/api/alert_email`

**Success Response:**
```json
{
  "status": "success",
  "email": "your-alert@example.com"
}
```
**Error Response:**
```json
{
  "status": "error",
  "message": "No mail found."
}
```

---

### **POST `/alert_email`**

Sets or updates the alert email address for thresholds

**Request Body:**
```json
{
  "alert_email": "your-alert@example.com"
}
```

**Success Response:**
```json
{
  "status": "success",
  "message": "Alert email saved."
}
```
**Error Response:**
```json
{
  "status": "error",
  "message": "Mail is missing."
}
```

---

## 7. Send Alert Mail (Threshold Alerting)

### **POST `/send_alert_mail`**

Triggers the alerting logic for a given metric and device.  
This endpoint is called by the frontend whenever a new sensor value is received.

**Request Body:**
```json
{
  "metric": "Temperatur",
  "value": 35,
  "thresholds": {
    "Temperatur": {
      "redLow": 10,
      "yellowLow": 15,
      "yellowHigh": 30,
      "redHigh": 32
    }
  },
  "device": "Altbau"
}
```

**Success Responses:**
- If a new alert is triggered:
  ```json
  {
    "status": "success",
    "message": "hart-Mail sent"
  }
  ```
- If the alert is still active (cooldown):
  ```json
  {
    "status": "success",
    "message": "hart-Mail already active"
  }
  ```
- If the value is back in the normal range (cooldown reset):
  ```json
  {
    "status": "success",
    "message": "No Threshold Exceeded"
  }
  ```

**Error Response:**
```json
{
  "status": "error",
  "message": "Missing parameters"
}
```

---
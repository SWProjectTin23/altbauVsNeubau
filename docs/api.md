
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


### 4. Comparison Between Devices over Time Range

**GET** `/comparison`

- Returns the selected metric of two devices over a given time range.

#### Query Parameters
- `device_1`: ID of first device (e.g., `1`)
- `device_2`: ID of second device (e.g., `2`)
- `metric`: one of `temperature`, `humidity`, `pollen`, `particulate_matter`
- `start`: Unix timestamp (optional)
- `end`: Unix timestamp (optional)

#### Example:
`http://localhost:5001/api/comparison?device_1=1&device_2=2&metric=pollen&start=1721745600&end=1721745660`

#### Success Response:
```json
{
  "device_1": [
    { "timestamp": 1721745600, "value": 10 },
    { "timestamp": 1721745660, "value": 11 }
  ],
  "device_2": [
    { "timestamp": 1721745600, "value": 8 },
    { "timestamp": 1721745660, "value": 9 }
  ],
  "metric": "pollen",
  "start": 1721745600,
  "end": 1721745660,
  "status": "success",
  "message": null
}
```
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
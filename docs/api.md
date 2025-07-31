# API Overview
This document describes the available REST API endpoints for the sensor backend.

The endpoints are still under development and may change according to the need.

Timestampes are displayed in ISO 8601 date format.

## Base URL
`http://localhost:5001/api/`

---

## Endpoints

### 1. Get available time range

**GET** `/devices/range`

- Returns the earliest and latest available timestamps across **all devices**.

#### Example: 
`http://localhost:5001/api/devices/range`

#### Response Format:
```json
[
  {
    "Device ID 1": {
      "end": "2025-07-27T23:00:00+00:00",
      "start": "2025-07-21T00:00:00+00:00"
    }
  },
  {
    "Device ID 2": {
      "end": "2025-07-27T23:00:00+00:00",
      "start": "2025-07-21T00:00:00+00:00"
    }
  }
]


```

### 2. Get sensor data by device ID and time range

**GET** `/devices/<int:device_id>/data`

- Returns all available data (by default) for a specific device. 
- Also accepts time filters.

#### Path Parameter:
- `device_id`: integer ID of the sensor device

#### Query Parameters:
- `start` *(optional)*: start timestamp in  UNIX format
- `end` *(optional)*: end timestamp in UNIX format

#### Example:
`http://localhost:5001/api/devices/1/data?start=2025-07-22T08:00:00Z&end=2025-07-23T08:00:00Z`

#### Response Format:
```json
{
  "data": [
    {
      "humidity": 31.93,
      "particulate_matter": 20,
      "pollen": 54,
      "temperature": 21.04,
      "timestamp": "2025-07-22T08:00:00+00:00"
    },
    {
      "humidity": 34.9,
      "particulate_matter": 16,
      "pollen": 87,
      "temperature": 24.76,
      "timestamp": "2025-07-22T09:00:00+00:00"
    },
    ...
  ],
  "device_id": 1
}
```

### 3. Get Latest Data for a Device

**GET** `/devices/<int:device_id>/latest`

- Returns the most recent data entry for a specific device.

#### Path Parameter:
- `device_id`: integer ID of the sensor device

#### Example:
`http://localhost:5001/api/devices/1/latest`

#### Response Format:
```json
{
    "device_id": 1,
    "data": [
        {
            "timestamp": "2025-07-27T23:00:00+00:00",
            "temperature": 24.79,
            "humidity": 38.64,
            "pollen": 124,
            "particulate_matter": 19
        }
    ]
}

```

### 4. Comparison Between Devices over Time Range

**GET** `/comparison`

- Returns the selected metric of two devices over a given time range (by default all).

#### Query Parameters
**Parameters (query):**

- `device_1`: ID of first device (e.g., `1`)  
- `device_2`: ID of second device (e.g., `2`) 
- `metric`: one of `temperature`, `humidity`, `pollen`, `particulate_matter`
- `start`: Unix timestamp (optional)
- `end`: Unix timestamp (optional)

#### Example: 
`http://localhost:5001/api/comparison?device_1=1&device_2=2&metric=pollen&start=2025-07-22T08:00:00Z&end=2025-07-23T08:00:00Z`

#### Response Format:
```json
{
  "device_1": [
    {
      "timestamp": "2025-07-22T08:00:00+00:00",
      "value": 54.0
    },
    {
      "timestamp": "2025-07-22T09:00:00+00:00",
      "value": 87.0
    },
    ...
  ],
  "device_2": [
    {
      "timestamp": "2025-07-22T08:00:00+00:00",
      "value": 131.0
    },
    {
      "timestamp": "2025-07-22T09:00:00+00:00",
      "value": 179.0
    },
    ...
  ]
}



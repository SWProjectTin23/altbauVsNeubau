# API Overview
This document describes the available REST API endpoints for the sensor backend.

The endpoints are still under development and may change according to the need.

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
        "device_1":
            {
                "end":1721745000,
                "start":1721736000
            },
        "device_2":
            {
                "end":1721744700,
                "start":1721736300
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
`http://localhost:5001/api/devices/1/data?start=1721736000&end=1721745660`

#### Response Format:
```json
[
  [
    {
        "device_id":1,
        "humidity":45.2,"particulate_matter":28,
        "pollen":10,
        "temperature":22.1,"timestamp":1721745600
    },
    {
        "device_id":1,
        "humidity":45.5,"particulate_matter":30,
        "pollen":11,
        "temperature":22.3,"timestamp":1721745660
    },
    ...
  ]
]
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
    "device_id":1,
    "humidity":45.5,
    "particulate_matter":30,
    "pollen":11,
    "temperature":22.3,"timestamp":1721745660
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
`http://localhost:5001/api/comparison?device_1=1&device_2=2&metric=pollen&start=1721745600&end=1721745660`

#### Response Format:
```json
{
    "device_1":
        [
            {
                "timestamp":1721745600,
                "value":10
            },
            {
                "timestamp":1721745660,
                "value":11
            }
        ],
    "device_2":
        [
            {
                "timestamp":1721745600,
                "value":8
            },
            {
                "timestamp":1721745660,
                "value":9
            }
            ]
}



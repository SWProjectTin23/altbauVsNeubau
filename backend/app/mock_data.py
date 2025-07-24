def get_mock_data():
    return {
        1: [
            {
                "device_id": 1,
                "timestamp": 1721745600,  # 2025-07-23 14:00:00 UTC
                "temperature": 22.1,
                "humidity": 45.2,
                "pollen": 10,
                "particulate_matter": 28
            },
            {
                "device_id": 1,
                "timestamp": 1721745660,
                "temperature": 22.3,
                "humidity": 45.5,
                "pollen": 11,
                "particulate_matter": 30
            }
        ],
        2: [
            {
                "device_id": 2,
                "timestamp": 1721745600,
                "temperature": 23.4,
                "humidity": 42.0,
                "pollen": 8,
                "particulate_matter": 25
            },
            {
                "device_id": 2,
                "timestamp": 1721745660,
                "temperature": 23.7,
                "humidity": 42.6,
                "pollen": 9,
                "particulate_matter": 27
            }
        ]
    }

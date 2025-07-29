import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_device_data_range(client):
    response = client.get("/api/devices/1/data?start=1721736000&end=1721745660")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    data = response.get_json()
    assert len(data) > 0
    # list[dic[str, int|float]]
    required_keys = {"device_id", "timestamp", "humidity", "temperature", "pollen", "particulate_matter"}
    for entry in data:
        assert required_keys.issubset(entry.keys())
        assert entry["device_id"] == 1

def test_time_range(client):
    response = client.get("/api/devices/range")
    assert response.status_code == 200
    data = response.get_json()

    # Assert that data is a list and not empty
    assert isinstance(data, list)
    assert len(data) > 0

    # We need to find the device data within the list
    # Let's create a dictionary for easier lookup by device_id
    devices_by_id = {device['device_id']: device for device in data}

    # Check for device_1 (device_id: 1)
    assert 1 in devices_by_id, "Device with ID 1 not found in the response"
    device_1_data = devices_by_id[1]
    assert isinstance(device_1_data, dict)
    required_keys = {"start", "end"}
    assert required_keys.issubset(device_1_data.keys()), f"Device 1 data missing required keys: {required_keys - device_1_data.keys()}"

    # Check for device_2 (device_id: 2)
    assert 2 in devices_by_id, "Device with ID 2 not found in the response"
    device_2_data = devices_by_id[2]
    assert isinstance(device_2_data, dict)
    assert required_keys.issubset(device_2_data.keys()), f"Device 2 data missing required keys: {required_keys - device_2_data.keys()}"
        
def test_device_latest(client):
    response = client.get("/api/devices/1/latest")
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    data = response.get_json()
    assert len(data) > 0
    # dic[str, int|float ]
    required_keys = {"device_id", "timestamp", "humidity", "temperature", "pollen", "particulate_matter"}
    assert required_keys.issubset(data.keys())
    assert data["device_id"] == 1

def test_comparison(client):
    response = client.get(
        "/api/comparison?device_1=1&device_2=2&metric=temperature&start=1721736000&end=1721745660"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert "device_1" in data
    assert "device_2" in data
    # dict[str, list[dict[str, int|float]]]
    for device_id in ["device_1", "device_2"]:
        device_data = data[device_id]
        assert isinstance(device_data, list)
        for entry in device_data:
            assert "timestamp" in entry
            assert "value" in entry
            assert isinstance(entry["timestamp"], int)
            assert isinstance(entry["value"], (int, float))
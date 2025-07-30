import psycopg2

# Test cases for the comparison endpoint in the API

def test_comparison_endpoint_basic(client, mocker):
    # Mock the database operations
    mocker.patch('app.api.comparison.compare_devices_over_time', return_value={
        'device_1': [{'timestamp': 1609459200, 'value': 20.5}],
        'device_2': [{'timestamp': 1609459200, 'value': 20.2}]
    })
    response = client.get('/api/comparison?device_1=1&device_2=2&metric=temperature')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'device_1' in json_data
    assert 'device_2' in json_data
    assert json_data['metric'] == 'temperature'

def test_comparison_endpoint_missing_metric(client):
    response = client.get('/api/comparison?device_1=1&device_2=2')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Metric must be specified.'

def test_comparison_endpoint_missing_device_ids(client):
    response = client.get('/api/comparison?metric=temperature')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Both device IDs must be provided.'

# Test case for device data
def test_device_data_basic(client, mocker):
    mocker.patch('app.api.device_data.device_exists', return_value=True)
    mocker.patch('app.api.device_data.get_device_data_from_db', return_value=[{"timestamp": "2025-07-30", "value": 42}])
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, dict)
    assert len(json_data) == 6
    assert json_data['data'][0]['timestamp'] == "2025-07-30"
    assert json_data['data'][0]['value'] == 42

def test_device_data_missing_device(client, mocker):
    mocker.patch('app.api.device_data.device_exists', return_value=False)
    
    response = client.get('/api/devices/999/data')
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Device with ID 999 does not exist.'

def test_device_data_no_data(client, mocker):
    mocker.patch('app.api.device_data.device_exists', return_value=True)
    mocker.patch('app.api.device_data.get_device_data_from_db', return_value=[])
    
    response = client.get('/api/devices/1/data?start=0&end=1000')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['data'] == []
    assert json_data['message'] == 'No data available for device 1 in the specified range.'

def test_device_data_database_error(client, mocker):
    mocker.patch('app.api.device_data.device_exists', return_value=True)
    mocker.patch('app.api.device_data.get_device_data_from_db', side_effect=psycopg2.Error("Database error"))
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'A database error occurred while processing your request.'

def test_device_data_value_error(client, mocker):
    mocker.patch('app.api.device_data.device_exists', return_value=True)
    mocker.patch('app.api.device_data.get_device_data_from_db', side_effect=ValueError("Invalid value"))
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Invalid value'

def test_device_data_unexpected_error(client, mocker):
    mocker.patch('app.api.device_data.device_exists', return_value=True)
    mocker.patch('app.api.device_data.get_device_data_from_db', side_effect=Exception("Unexpected error"))
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'An unexpected error occurred.'


# Test cases for the device latest endpoint
def test_device_latest_basic(client, mocker):
    mocker.patch('app.api.device_latest.device_exists', return_value=True)
    mocker.patch('app.api.device_latest.get_latest_device_data_from_db', return_value={"timestamp": "2025-07-30", "value": 42})
    
    response = client.get('/api/devices/1/latest')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['data']['timestamp'] == "2025-07-30"
    assert json_data['data']['value'] == 42

def test_device_latest_missing_device(client, mocker):
    mocker.patch('app.api.device_latest.device_exists', return_value=False)
    
    response = client.get('/api/devices/999/latest')
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Device with ID 999 does not exist.'

def test_device_latest_no_data(client, mocker):
    mocker.patch('app.api.device_latest.device_exists', return_value=True)
    mocker.patch('app.api.device_latest.get_latest_device_data_from_db', return_value=None)
    
    response = client.get('/api/devices/1/latest')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['data'] == []
    assert json_data['message'] == 'No data available for device 1.'

def test_device_latest_database_error(client, mocker):
    mocker.patch('app.api.device_latest.device_exists', return_value=True)
    mocker.patch('app.api.device_latest.get_latest_device_data_from_db', side_effect=psycopg2.Error("Database error"))
    
    response = client.get('/api/devices/1/latest')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'A database error occurred while processing your request.'

def test_device_latest_value_error(client, mocker):
    mocker.patch('app.api.device_latest.device_exists', return_value=True)
    mocker.patch('app.api.device_latest.get_latest_device_data_from_db', side_effect=ValueError("Invalid value"))
    
    response = client.get('/api/devices/1/latest')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Invalid value'

def test_device_latest_unexpected_error(client, mocker):
    mocker.patch('app.api.device_latest.device_exists', return_value=True)
    mocker.patch('app.api.device_latest.get_latest_device_data_from_db', side_effect=Exception("Unexpected error"))
    
    response = client.get('/api/devices/1/latest')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'An unexpected error occurred while processing your request.'

# Test cases for the time range endpoint
def test_time_range_basic(client, mocker):
    mocker.patch('app.api.range.get_all_device_time_ranges_from_db', return_value=[
        {"device_id": 1, "start": 1609459200, "end": 1612137600},
        {"device_id": 2, "start": 1609459200, "end": 1612137600}
    ])
    
    response = client.get('/api/range')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert len(json_data['data']) == 2

def test_time_range_no_data(client, mocker):
    mocker.patch('app.api.range.get_all_device_time_ranges_from_db', return_value=[])
    
    response = client.get('/api/range')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == 'No time ranges found for any devices.'
    assert json_data['data'] == []

def test_time_range_database_error(client, mocker):
    mocker.patch('app.api.range.get_all_device_time_ranges_from_db', side_effect=psycopg2.Error("Database error"))
    
    response = client.get('/api/range')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'A database error occurred while processing your request.'

def test_time_range_unexpected_error(client, mocker):
    mocker.patch('app.api.range.get_all_device_time_ranges_from_db', side_effect=Exception("Unexpected error"))
    
    response = client.get('/api/range')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'An unexpected error occurred.'
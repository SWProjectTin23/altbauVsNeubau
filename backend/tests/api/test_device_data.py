import psycopg2

def test_device_data_basic(client, mocker):
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', return_value=[{"timestamp": "2025-07-30", "value": 42}])
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, dict)
    assert len(json_data) == 6
    assert json_data['data'][0]['timestamp'] == "2025-07-30"
    assert json_data['data'][0]['value'] == 42

def test_device_data_missing_device(client, mocker):
    mocker.patch('api.device_data.device_exists', return_value=False)
    
    response = client.get('/api/devices/999/data')
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Device with ID 999 does not exist.'

def test_device_data_no_data(client, mocker):
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', return_value=[])
    
    response = client.get('/api/devices/1/data?start=0&end=1000')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['data'] == []
    assert json_data['message'] == 'No data available for device 1 in the specified range.'

def test_device_data_database_error(client, mocker):
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', side_effect=psycopg2.Error("Database error"))
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'A database error occurred while processing your request.'

def test_device_data_value_error(client, mocker):
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', side_effect=ValueError("Invalid value"))
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Invalid value'

def test_device_data_unexpected_error(client, mocker):
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', side_effect=Exception("Unexpected error"))
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'An unexpected error occurred.'
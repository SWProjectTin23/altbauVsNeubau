import psycopg2

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
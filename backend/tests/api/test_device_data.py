import psycopg2
from common.exceptions import DatabaseError, DatabaseOperationalError, DatabaseQueryTimeoutError
from unittest.mock import patch

def mock_token_required(f):
    return f

@patch("api.device_data.DeviceData.method_decorators", [mock_token_required])
def test_device_data_basic(client, mocker):
    mock_log = mocker.patch('api.device_data.log_event')
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', return_value=[{"timestamp": "2025-07-30", "value": 42}])
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, dict)
    assert len(json_data) == 6
    assert json_data['data'][0]['timestamp'] == "2025-07-30"
    assert json_data['data'][0]['value'] == 42
    assert ("INFO", "device_data.ok") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.device_data.DeviceData.method_decorators", [mock_token_required])
def test_device_data_missing_device(client, mocker):
    mock_log = mocker.patch('api.device_data.log_event')
    mocker.patch('api.device_data.device_exists', return_value=False)
    
    response = client.get('/api/devices/999/data')
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Device with ID 999 does not exist.'
    assert ("WARNING", "device_data.not_found") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.device_data.DeviceData.method_decorators", [mock_token_required])
def test_device_data_no_data(client, mocker):
    mock_log = mocker.patch('api.device_data.log_event')
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', return_value=[])
    
    response = client.get('/api/devices/1/data?start=0&end=1000')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['data'] == []
    assert json_data['message'] == 'No data available for device 1 in the specified range.'
    assert ("INFO", "device_data.empty") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.device_data.DeviceData.method_decorators", [mock_token_required])
def test_device_data_database_error(client, mocker):
    mock_log = mocker.patch('api.device_data.log_event')
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', side_effect=psycopg2.Error("Database error"))
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'A database error occurred while processing your request.'
    assert ("ERROR", "device_data.db_psycopg2_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.device_data.DeviceData.method_decorators", [mock_token_required])
def test_device_data_value_error(client, mocker):
    mock_log = mocker.patch('api.device_data.log_event')
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', side_effect=ValueError("Invalid value"))
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Invalid value'
    assert ("WARNING", "device_data.bad_request") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.device_data.DeviceData.method_decorators", [mock_token_required])
def test_device_data_unexpected_error(client, mocker):
    mock_log = mocker.patch('api.device_data.log_event')
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', side_effect=Exception("Unexpected error"))
    
    response = client.get('/api/devices/1/data')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'An unexpected error occurred.'
    assert ("ERROR", "device_data.unhandled_exception") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.device_data.DeviceData.method_decorators", [mock_token_required])
def test_device_data_db_timeout_maps_504_and_logs(client, mocker):
    mock_log = mocker.patch('api.device_data.log_event')
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', side_effect=DatabaseQueryTimeoutError('timeout'))
    resp = client.get('/api/devices/1/data')
    assert resp.status_code == 504
    assert resp.get_json()['message'] == 'database query timeout'
    assert ("ERROR", "device_data.db_query_timeout") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.device_data.DeviceData.method_decorators", [mock_token_required])
def test_device_data_db_operational_maps_503_and_logs(client, mocker):
    mock_log = mocker.patch('api.device_data.log_event')
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', side_effect=DatabaseOperationalError('down'))
    resp = client.get('/api/devices/1/data')
    assert resp.status_code == 503
    assert resp.get_json()['message'] == 'database temporarily unavailable'
    assert ("ERROR", "device_data.db_operational_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.device_data.DeviceData.method_decorators", [mock_token_required])
def test_device_data_db_generic_maps_500_and_logs(client, mocker):
    mock_log = mocker.patch('api.device_data.log_event')
    mocker.patch('api.device_data.device_exists', return_value=True)
    mocker.patch('api.device_data.get_device_data_from_db', side_effect=DatabaseError('db'))
    resp = client.get('/api/devices/1/data')
    assert resp.status_code == 500
    assert resp.get_json()['message'] == 'A database error occurred while processing your request.'
    assert ("ERROR", "device_data.db_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
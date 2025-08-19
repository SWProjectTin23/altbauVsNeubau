import psycopg2
from common.exceptions import DatabaseError, DatabaseOperationalError, DatabaseQueryTimeoutError

def test_device_latest_basic(client, mocker):
    mock_log = mocker.patch('api.device_latest.log_event')
    mocker.patch('api.device_latest.device_exists', return_value=True)
    mocker.patch('api.device_latest.get_latest_device_data_from_db', return_value={"timestamp": "2025-07-30", "value": 42})
    
    response = client.get('/api/devices/1/latest')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['data']['timestamp'] == "2025-07-30"
    assert json_data['data']['value'] == 42
    assert ("INFO", "device_latest.ok") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

def test_device_latest_missing_device(client, mocker):
    mock_log = mocker.patch('api.device_latest.log_event')
    mocker.patch('api.device_latest.device_exists', return_value=False)
    
    response = client.get('/api/devices/999/latest')
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Device with ID 999 does not exist.'
    assert ("WARNING", "device_latest.not_found") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

def test_device_latest_no_data(client, mocker):
    mock_log = mocker.patch('api.device_latest.log_event')
    mocker.patch('api.device_latest.device_exists', return_value=True)
    mocker.patch('api.device_latest.get_latest_device_data_from_db', return_value=None)
    
    response = client.get('/api/devices/1/latest')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['data'] == []
    assert json_data['message'] == 'No data available for device 1.'
    assert ("INFO", "device_latest.empty") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

def test_device_latest_database_error(client, mocker):
    mock_log = mocker.patch('api.device_latest.log_event')
    mocker.patch('api.device_latest.device_exists', return_value=True)
    mocker.patch('api.device_latest.get_latest_device_data_from_db', side_effect=psycopg2.Error("Database error"))
    
    response = client.get('/api/devices/1/latest')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'A database error occurred while processing your request.'
    assert ("ERROR", "device_latest.db_psycopg2_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

def test_device_latest_value_error(client, mocker):
    mock_log = mocker.patch('api.device_latest.log_event')
    mocker.patch('api.device_latest.device_exists', return_value=True)
    mocker.patch('api.device_latest.get_latest_device_data_from_db', side_effect=ValueError("Invalid value"))
    
    response = client.get('/api/devices/1/latest')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Invalid value'
    assert ("WARNING", "device_latest.bad_request") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

def test_device_latest_unexpected_error(client, mocker):
    mock_log = mocker.patch('api.device_latest.log_event')
    mocker.patch('api.device_latest.device_exists', return_value=True)
    mocker.patch('api.device_latest.get_latest_device_data_from_db', side_effect=Exception("Unexpected error"))
    
    response = client.get('/api/devices/1/latest')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'An unexpected error occurred while processing your request.'
    assert ("ERROR", "device_latest.unhandled_exception") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_device_latest_db_timeout_maps_504_and_logs(client, mocker):
    mock_log = mocker.patch('api.device_latest.log_event')
    mocker.patch('api.device_latest.device_exists', return_value=True)
    mocker.patch('api.device_latest.get_latest_device_data_from_db', side_effect=DatabaseQueryTimeoutError('timeout'))
    resp = client.get('/api/devices/1/latest')
    assert resp.status_code == 504
    assert resp.get_json()['message'] == 'database query timeout'
    assert ("ERROR", "device_latest.db_query_timeout") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_device_latest_db_operational_maps_503_and_logs(client, mocker):
    mock_log = mocker.patch('api.device_latest.log_event')
    mocker.patch('api.device_latest.device_exists', return_value=True)
    mocker.patch('api.device_latest.get_latest_device_data_from_db', side_effect=DatabaseOperationalError('down'))
    resp = client.get('/api/devices/1/latest')
    assert resp.status_code == 503
    assert resp.get_json()['message'] == 'database temporarily unavailable'
    assert ("ERROR", "device_latest.db_operational_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_device_latest_db_generic_maps_500_and_logs(client, mocker):
    mock_log = mocker.patch('api.device_latest.log_event')
    mocker.patch('api.device_latest.device_exists', return_value=True)
    mocker.patch('api.device_latest.get_latest_device_data_from_db', side_effect=DatabaseError('db'))
    resp = client.get('/api/devices/1/latest')
    assert resp.status_code == 500
    assert resp.get_json()['message'] == 'database error'
    assert ("ERROR", "device_latest.db_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
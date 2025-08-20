import psycopg2
from common.exceptions import DatabaseError, DatabaseOperationalError, DatabaseQueryTimeoutError

def test_time_range_basic(client, mocker):
    mock_log = mocker.patch('api.range.log_event')
    mocker.patch('api.range.get_all_device_time_ranges_from_db', return_value=[
        {"device_id": 1, "start": 1609459200, "end": 1612137600},
        {"device_id": 2, "start": 1609459200, "end": 1612137600}
    ])
    
    response = client.get('/api/range')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert len(json_data['data']) == 2
    assert ("INFO", "time_range.ok") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

def test_time_range_no_data(client, mocker):
    mock_log = mocker.patch('api.range.log_event')
    mocker.patch('api.range.get_all_device_time_ranges_from_db', return_value=[])
    
    response = client.get('/api/range')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == 'No time ranges found for any devices.'
    assert json_data['data'] == []
    assert ("INFO", "time_range.empty") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

def test_time_range_database_error(client, mocker):
    mock_log = mocker.patch('api.range.log_event')
    mocker.patch('api.range.get_all_device_time_ranges_from_db', side_effect=psycopg2.Error("Database error"))
    
    response = client.get('/api/range')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'A database error occurred while processing your request.'
    assert ("ERROR", "range.db_psycopg2_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

def test_time_range_unexpected_error(client, mocker):
    mock_log = mocker.patch('api.range.log_event')
    mocker.patch('api.range.get_all_device_time_ranges_from_db', side_effect=Exception("Unexpected error"))
    
    response = client.get('/api/range')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'An unexpected error occurred.'
    assert ("ERROR", "time_range.unhandled_exception") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_time_range_db_timeout_maps_504_and_logs(client, mocker):
    mock_log = mocker.patch('api.range.log_event')
    mocker.patch('api.range.get_all_device_time_ranges_from_db', side_effect=DatabaseQueryTimeoutError('timeout'))
    resp = client.get('/api/range')
    assert resp.status_code == 504
    assert resp.get_json()['message'] == 'database query timeout'
    assert ("ERROR", "time_range.db_query_timeout") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_time_range_db_operational_maps_503_and_logs(client, mocker):
    mock_log = mocker.patch('api.range.log_event')
    mocker.patch('api.range.get_all_device_time_ranges_from_db', side_effect=DatabaseOperationalError('down'))
    resp = client.get('/api/range')
    assert resp.status_code == 503
    assert resp.get_json()['message'] == 'database temporarily unavailable'
    assert ("ERROR", "time_range.db_operational_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_time_range_db_generic_maps_500_and_logs(client, mocker):
    mock_log = mocker.patch('api.range.log_event')
    mocker.patch('api.range.get_all_device_time_ranges_from_db', side_effect=DatabaseError('db'))
    resp = client.get('/api/range')
    assert resp.status_code == 500
    assert resp.get_json()['message'] == 'database error'
    assert ("ERROR", "time_range.db_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
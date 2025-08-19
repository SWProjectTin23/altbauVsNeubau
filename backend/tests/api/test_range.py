import psycopg2

def test_time_range_basic(client, mocker):
    mocker.patch('api.range.get_all_device_time_ranges_from_db', return_value=[
        {"device_id": 1, "start": 1609459200, "end": 1612137600},
        {"device_id": 2, "start": 1609459200, "end": 1612137600}
    ])
    
    response = client.get('/api/range')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert len(json_data['data']) == 2

def test_time_range_no_data(client, mocker):
    mocker.patch('api.range.get_all_device_time_ranges_from_db', return_value=[])
    
    response = client.get('/api/range')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == 'No time ranges found for any devices.'
    assert json_data['data'] == []

def test_time_range_database_error(client, mocker):
    mocker.patch('api.range.get_all_device_time_ranges_from_db', side_effect=psycopg2.Error("Database error"))
    
    response = client.get('/api/range')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'A database error occurred while processing your request.'

def test_time_range_unexpected_error(client, mocker):
    mocker.patch('api.range.get_all_device_time_ranges_from_db', side_effect=Exception("Unexpected error"))
    
    response = client.get('/api/range')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'An unexpected error occurred.'
def test_comparison_endpoint_basic(client, mocker):
    # Mock the database operations
    mocker.patch('api.comparison.compare_devices_over_time', return_value={
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
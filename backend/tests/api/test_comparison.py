from common.exceptions import (
    DatabaseError,
    DatabaseOperationalError,
    DatabaseQueryTimeoutError,
    AppError,
)


def test_comparison_endpoint_basic(client, mocker):
    # Mock the database operation to return the current shape
    mocker.patch('api.comparison.compare_devices_over_time', return_value={
        'data': {
            'device_1': [{'timestamp': 1609459200, 'value': 20.5}],
            'device_2': [{'timestamp': 1609459200, 'value': 20.2}],
        },
        'message': None,
        'status': 'success',
    })
    response = client.get('/api/comparison?device_1=1&device_2=2&metric=temperature')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'device_1' in json_data and isinstance(json_data['device_1'], list)
    assert 'device_2' in json_data and isinstance(json_data['device_2'], list)
    assert json_data['metric'] == 'temperature'
    assert 'start' in json_data and 'end' in json_data

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
    assert json_data['message'] == 'At least one device ID must be provided.'


def test_comparison_endpoint_nonpositive_device_id_1(client):
    response = client.get('/api/comparison?device_1=0&metric=temperature')
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Device ID 1 must be a positive integer.'


def test_comparison_endpoint_nonpositive_device_id_2(client):
    response = client.get('/api/comparison?device_2=0&metric=temperature')
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Device ID 2 must be a positive integer.'


def test_comparison_endpoint_time_range_validation_error(client, mocker):
    mocker.patch('api.comparison.validate_timestamps_and_range', return_value=(False, 'Start timestamp must be less than end timestamp.'))
    resp = client.get('/api/comparison?device_1=1&metric=temperature&start=10&end=5')
    assert resp.status_code == 400
    assert resp.get_json()['message'].startswith('Invalid time range:')


def test_comparison_endpoint_empty_data_success_message(client, mocker):
    mocker.patch('api.comparison.compare_devices_over_time', return_value={
        'data': {'device_1': [], 'device_2': []},
        'message': None,
        'status': 'success',
    })
    resp = client.get('/api/comparison?device_1=1&device_2=2&metric=temperature')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['status'] == 'success'
    assert body['message'] == 'No data found for the specified devices and metric.'


def test_comparison_endpoint_db_timeout_maps_504(client, mocker):
    mocker.patch('api.comparison.compare_devices_over_time', side_effect=DatabaseQueryTimeoutError('timeout'))
    resp = client.get('/api/comparison?device_1=1&metric=temperature')
    assert resp.status_code == 504
    assert resp.get_json()['message'] == 'database query timeout'


def test_comparison_endpoint_db_operational_maps_503(client, mocker):
    mocker.patch('api.comparison.compare_devices_over_time', side_effect=DatabaseOperationalError('down'))
    resp = client.get('/api/comparison?device_1=1&metric=temperature')
    assert resp.status_code == 503
    assert resp.get_json()['message'] == 'database temporarily unavailable'


def test_comparison_endpoint_db_generic_maps_500(client, mocker):
    mocker.patch('api.comparison.compare_devices_over_time', side_effect=DatabaseError('oops'))
    resp = client.get('/api/comparison?device_1=1&metric=temperature')
    assert resp.status_code == 500
    assert resp.get_json()['message'] == 'database error'


def test_comparison_endpoint_value_error_maps_400(client, mocker):
    mocker.patch('api.comparison.compare_devices_over_time', side_effect=ValueError('bad metric'))
    resp = client.get('/api/comparison?device_1=1&metric=temperature')
    assert resp.status_code == 400
    assert resp.get_json()['message'] == 'bad metric'


def test_comparison_endpoint_app_error_maps_500(client, mocker):
    mocker.patch('api.comparison.compare_devices_over_time', side_effect=AppError('app layer fail'))
    resp = client.get('/api/comparison?device_1=1&metric=temperature')
    assert resp.status_code == 500
    assert resp.get_json()['message'] == 'app layer fail'
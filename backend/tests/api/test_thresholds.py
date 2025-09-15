import json
import psycopg2
from common.exceptions import DatabaseError
from unittest.mock import patch

def mock_token_required(f):
    return f

@patch("api.thresholds.Thresholds.method_decorators", [mock_token_required])
def test_get_thresholds_success(client, mocker):
    mock_log = mocker.patch('api.thresholds.log_event')
    """
    Test the successful retrieval of thresholds.
    """
    mocker.patch(
        'api.thresholds.get_thresholds_from_db',
        return_value={
            "temperature_min_soft": 12.0,
            "temperature_max_soft": 25.0,
            "temperature_min_hard": 15.0,
            "temperature_max_hard": 30.0,
        }
    )

    response = client.get('/api/thresholds')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert isinstance(data['data'], dict)
    assert data['message'] == "Thresholds retrieved successfully."
    assert ("INFO", "thresholds.get.ok") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.thresholds.Thresholds.method_decorators", [mock_token_required])
def test_get_thresholds_no_data(client, mocker):
    mock_log = mocker.patch('api.thresholds.log_event')
    """
    Test the case where no thresholds are available.
    """
    mocker.patch('api.thresholds.get_thresholds_from_db', return_value=[])
    response = client.get('/api/thresholds')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data'] == []
    assert data['message'] == 'No thresholds available.'
    assert ("INFO", "thresholds.get.empty") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.thresholds.Thresholds.method_decorators", [mock_token_required])
def test_get_thresholds_database_error(client, mocker):
    mock_log = mocker.patch('api.thresholds.log_event')
    """
    Test the case where a database error occurs while retrieving thresholds.
    """
    mocker.patch('api.thresholds.get_thresholds_from_db', side_effect=psycopg2.Error("Database error"))
    response = client.get('/api/thresholds')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert data['message'] == 'A database error occurred while processing your request.'
    assert ("ERROR", "thresholds.get.db_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.thresholds.Thresholds.method_decorators", [mock_token_required])
def test_get_thresholds_unexpected_error(client, mocker):
    mock_log = mocker.patch('api.thresholds.log_event')
    """
    Test the case where an unexpected error occurs while retrieving thresholds.
    """
    mocker.patch('api.thresholds.get_thresholds_from_db', side_effect=Exception("Unexpected error"))
    response = client.get('/api/thresholds')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert data['message'] == 'An unexpected error occurred while processing your request.'
    assert ("ERROR", "thresholds.get.unhandled_exception") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.thresholds.Thresholds.method_decorators", [mock_token_required])
def test_post_thresholds_success(client, mocker):
    mock_log = mocker.patch('api.thresholds.log_event')
    """
    Test the successful posting of thresholds.
    """
    threshold_data = {
        "temperature_min_hard": 12.0,
        "temperature_min_soft": 15.0,
        "temperature_max_soft": 25.0,
        "temperature_max_hard": 30.0,
        "humidity_min_hard": 10.0,
        "humidity_min_soft": 20.0,
        "humidity_max_soft": 70.0,
        "humidity_max_hard": 80.0,
        "pollen_min_hard": 1,
        "pollen_min_soft": 5,
        "pollen_max_soft": 50,
        "pollen_max_hard": 100,
        "particulate_matter_min_hard": 1,
        "particulate_matter_min_soft": 5,
        "particulate_matter_max_soft": 50,
        "particulate_matter_max_hard": 100
    }
    
    mocker.patch('api.thresholds.update_thresholds_in_db', return_value=None)
    
    response = client.post('/api/thresholds', json=threshold_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['message'] == "Thresholds updated successfully."
    assert ("INFO", "thresholds.post.ok") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.thresholds.Thresholds.method_decorators", [mock_token_required])
def test_post_thresholds_validation_error(client, mocker):
    mock_log = mocker.patch('api.thresholds.log_event')
    """
    Test the case where validation fails due to minimum value being greater than maximum value.
    """
    threshold_data = {
        "temperature_min_hard": 15.0,
        "temperature_min_soft": 30.0,
        "temperature_max_soft": 25.0,
        "temperature_max_hard": 28.0,
        "humidity_min_hard": 10.0,
        "humidity_min_soft": 20.0,
        "humidity_max_soft": 70.0,
        "humidity_max_hard": 80.0,
        "pollen_min_soft": 10,
        "pollen_max_soft": 50,
        "pollen_min_hard": 5,
        "pollen_max_hard": 100,
        "particulate_matter_min_soft": 5,
        "particulate_matter_max_soft": 50,
        "particulate_matter_min_hard": 1,
        "particulate_matter_max_hard": 100
    }

    mocker.patch('api.thresholds.update_thresholds_in_db', return_value=None)
    
    response = client.post('/api/thresholds', json=threshold_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert data['message'] == "'temperature_min_soft' must be less than 'temperature_max_hard'."
    # One of the validation log events should be present
    assert any(c.args[2].startswith("thresholds.post.") and c.args[1] == "WARNING" for c in mock_log.call_args_list)

@patch("api.thresholds.Thresholds.method_decorators", [mock_token_required])
def test_post_thresholds_hard_soft_error(client, mocker):
    mock_log = mocker.patch('api.thresholds.log_event')
    """
    Test the case where hard thresholds are not greater than soft thresholds.
    """
    threshold_data = {
        "temperature_min_hard": 15.0,
        "temperature_min_soft": 10.0,
        "temperature_max_soft": 25.0,
        "temperature_max_hard": 20.0,  # Hard threshold not greater than soft
        "humidity_min_hard": 10.0,
        "humidity_min_soft": 20.0,
        "humidity_max_soft": 70.0,
        "humidity_max_hard": 80.0,
        "pollen_min_hard": 10,
        "pollen_min_soft": 5,
        "pollen_max_soft": 50,
        "pollen_max_hard": 100,
        "particulate_matter_min_hard": 5,
        "particulate_matter_min_soft": 1,
        "particulate_matter_max_soft": 50,
        "particulate_matter_max_hard": 100
    }
    
    response = client.post('/api/thresholds', json=threshold_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert data['message'] == "'temperature_min_hard' must be less than 'temperature_min_soft'."
    assert any(c.args[2].startswith("thresholds.post.") and c.args[1] == "WARNING" for c in mock_log.call_args_list)

@patch("api.thresholds.Thresholds.method_decorators", [mock_token_required])
def test_post_thresholds_db_error_maps_500_and_logs(client, mocker):
    mock_log = mocker.patch('api.thresholds.log_event')
    threshold_data = {
        "temperature_min_hard": 12.0,
        "temperature_min_soft": 15.0,
        "temperature_max_soft": 25.0,
        "temperature_max_hard": 30.0,
        "humidity_min_hard": 10.0,
        "humidity_min_soft": 20.0,
        "humidity_max_soft": 70.0,
        "humidity_max_hard": 80.0,
        "pollen_min_hard": 1,
        "pollen_min_soft": 5,
        "pollen_max_soft": 50,
        "pollen_max_hard": 100,
        "particulate_matter_min_hard": 1,
        "particulate_matter_min_soft": 5,
        "particulate_matter_max_soft": 50,
        "particulate_matter_max_hard": 100
    }
    mocker.patch('api.thresholds.update_thresholds_in_db', side_effect=psycopg2.Error('db'))
    resp = client.post('/api/thresholds', json=threshold_data)
    assert resp.status_code == 500
    assert resp.get_json()['message'] == 'A database error occurred while processing your request.'
    assert ("ERROR", "thresholds.post.db_error") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]

@patch("api.thresholds.Thresholds.method_decorators", [mock_token_required])
def test_post_thresholds_unexpected_error_maps_500_and_logs(client, mocker):
    mock_log = mocker.patch('api.thresholds.log_event')
    threshold_data = {
        "temperature_min_hard": 12.0,
        "temperature_min_soft": 15.0,
        "temperature_max_soft": 25.0,
        "temperature_max_hard": 30.0,
        "humidity_min_hard": 10.0,
        "humidity_min_soft": 20.0,
        "humidity_max_soft": 70.0,
        "humidity_max_hard": 80.0,
        "pollen_min_hard": 1,
        "pollen_min_soft": 5,
        "pollen_max_soft": 50,
        "pollen_max_hard": 100,
        "particulate_matter_min_hard": 1,
        "particulate_matter_min_soft": 5,
        "particulate_matter_max_soft": 50,
        "particulate_matter_max_hard": 100
    }
    mocker.patch('api.thresholds.update_thresholds_in_db', side_effect=Exception('boom'))
    resp = client.post('/api/thresholds', json=threshold_data)
    assert resp.status_code == 500
    assert resp.get_json()['message'] == 'An unexpected error occurred while processing your request.'
    assert ("ERROR", "thresholds.post.unhandled_exception") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
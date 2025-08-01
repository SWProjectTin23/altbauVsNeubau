import json
import psycopg2

def test_get_thresholds_success(client, mocker):
    """
    Test the successful retrieval of thresholds.
    """
    mocker.patch(
        'app.api.thresholds.get_thresholds_from_db',
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

def test_get_thresholds_no_data(client, mocker):
    """
    Test the case where no thresholds are available.
    """
    mocker.patch('app.api.thresholds.get_thresholds_from_db', return_value=[])
    response = client.get('/api/thresholds')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data'] == []
    assert data['message'] == 'No thresholds available.'

def test_get_thresholds_database_error(client, mocker):
    """
    Test the case where a database error occurs while retrieving thresholds.
    """
    mocker.patch('app.api.thresholds.get_thresholds_from_db', side_effect=psycopg2.Error("Database error"))
    response = client.get('/api/thresholds')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert data['message'] == 'A database error occurred while processing your request.'

def test_get_thresholds_unexpected_error(client, mocker):
    """
    Test the case where an unexpected error occurs while retrieving thresholds.
    """
    mocker.patch('app.api.thresholds.get_thresholds_from_db', side_effect=Exception("Unexpected error"))
    response = client.get('/api/thresholds')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert data['message'] == 'An unexpected error occurred while processing your request.'

def test_post_thresholds_success(client, mocker):
    """
    Test the successful posting of thresholds.
    """
    threshold_data = {
        "temperature_min_soft": 12.0,
        "temperature_max_soft": 25.0,
        "temperature_min_hard": 15.0,
        "temperature_max_hard": 30.0,
        "humidity_min_soft": 10.0,
        "humidity_max_soft": 70.0,
        "humidity_min_hard": 20.0,
        "humidity_max_hard": 80.0,
        "pollen_min_soft": 5,
        "pollen_max_soft": 50,
        "pollen_min_hard": 10,
        "pollen_max_hard": 100,
        "particulate_matter_min_soft": 1,
        "particulate_matter_max_soft": 50,
        "particulate_matter_min_hard": 5,
        "particulate_matter_max_hard": 100
    }
    
    mocker.patch('app.api.thresholds.update_thresholds_in_db', return_value=None)
    
    response = client.post('/api/thresholds', json=threshold_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['message'] == "Thresholds updated successfully."

def test_post_thresholds_validation_error(client, mocker):
    """
    Test the case where validation fails due to minimum value being greater than maximum value.
    """
    threshold_data = {
        "temperature_min_soft": 30.0,
        "temperature_max_soft": 25.0,
        "temperature_min_hard": 15.0,
        "temperature_max_hard": 30.0,
        "humidity_min_soft": 10.0,
        "humidity_max_soft": 70.0,
        "humidity_min_hard": 20.0,
        "humidity_max_hard": 80.0,
        "pollen_min_soft": 5,
        "pollen_max_soft": 50,
        "pollen_min_hard": 10,
        "pollen_max_hard": 100,
        "particulate_matter_min_soft": 1,
        "particulate_matter_max_soft": 50,
        "particulate_matter_min_hard": 5,
        "particulate_matter_max_hard": 100
    }
    
    response = client.post('/api/thresholds', json=threshold_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert data['message'] == "Minimum value for 'temperature_min_soft' must be less than maximum value for 'temperature_max_soft'."

def test_post_thresholds_hard_soft_error(client, mocker):
    """
    Test the case where hard thresholds are not greater than soft thresholds.
    """
    threshold_data = {
        "temperature_min_soft": 10.0,
        "temperature_max_soft": 25.0,
        "temperature_min_hard": 15.0,
        "temperature_max_hard": 20.0,  # Hard threshold not greater than soft
        "humidity_min_soft": 10.0,
        "humidity_max_soft": 70.0,
        "humidity_min_hard": 20.0,
        "humidity_max_hard": 80.0,
        "pollen_min_soft": 5,
        "pollen_max_soft": 50,
        "pollen_min_hard": 10,
        "pollen_max_hard": 100,
        "particulate_matter_min_soft": 1,
        "particulate_matter_max_soft": 50,
        "particulate_matter_min_hard": 5,
        "particulate_matter_max_hard": 100
    }
    
    response = client.post('/api/thresholds', json=threshold_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert data['message'] == "Hard threshold 'temperature_max_hard' must be greater than soft threshold 'temperature_max_soft'."
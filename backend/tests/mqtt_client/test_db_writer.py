from mqtt_client.db_writer import insert_sensor_data
from common.exceptions import DatabaseError

def test_insert_sensor_data_complete_data(mocker):
    # Shared device ID and timestamp for all inserts
    device_id = 2
    timestamp = "2025-08-06T13:00:00Z"

    # Mock database connection and cursor
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Simulate a complete insert call
    insert_sensor_data(
        mock_conn, 
        device_id, 
        timestamp, 
        temperature=21.3, 
        humidity=55, 
        pollen=123, 
        particulate_matter=78
    )

    # Ensure that execute, commit, and cursor.close were called once
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

    # Validate the parameters passed to the execute call
    expected_query = """
    INSERT INTO sensor_data (device_id, timestamp, temperature, humidity, pollen, particulate_matter)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (device_id, timestamp)
    DO UPDATE SET 
        temperature = EXCLUDED.temperature,
        humidity = EXCLUDED.humidity,
        pollen = EXCLUDED.pollen,
        particulate_matter = EXCLUDED.particulate_matter;
    """
    expected_params = (device_id, timestamp, 21.3, 55, 123, 78)
    mock_cursor.execute.assert_called_with(expected_query, expected_params)

def test_insert_sensor_data_incomplete_data(mocker):
    # Shared device ID and timestamp for all inserts
    device_id = 2
    timestamp = "2025-08-06T13:00:00Z"

    # Mock database connection
    mock_conn = mocker.MagicMock()

    # Attempt to insert incomplete data and expect an exception
    try:
        insert_sensor_data(mock_conn, device_id, timestamp, temperature=21.3, humidity=55)
    except DatabaseError as e:
        assert str(e) == "Incomplete sensor data: all sensor values must be provided"

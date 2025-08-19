import pytest
from mqtt_client.db_writer import insert_sensor_data
from common.exceptions import DatabaseError, DatabaseTimeoutError, DatabaseConnectionError

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
        temperature = COALESCE(EXCLUDED.temperature, sensor_data.temperature),
        humidity = COALESCE(EXCLUDED.humidity, sensor_data.humidity),
        pollen = COALESCE(EXCLUDED.pollen, sensor_data.pollen),
        particulate_matter = COALESCE(EXCLUDED.particulate_matter, sensor_data.particulate_matter);
    """
    expected_params = (device_id, timestamp, 21.3, 55, 123, 78)
    mock_cursor.execute.assert_called_with(expected_query, expected_params)

def test_insert_sensor_data_incomplete_data(mocker):
    device_id = 2
    timestamp = "2025-08-06T13:00:00Z"
    mock_conn = mocker.MagicMock()

    with pytest.raises(DatabaseError) as ei:
        insert_sensor_data(
            mock_conn,
            device_id,
            timestamp
        )
        # no required metrics
    assert "Incomplete sensor data: all sensor values must be provided" in str(ei.value)

    # no insert
    mock_conn.cursor.assert_not_called()
    mock_conn.commit.assert_not_called()
    mock_conn.rollback.assert_not_called()

def test_commit_failure_rolls_back_and_raises_generic(mocker):
    """if commit() fails, rollback and raise DatabaseError。"""
    device_id = 4
    timestamp = "2025-08-06T15:00:00Z"

    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit.side_effect = Exception("commit timed out")

    with pytest.raises(DatabaseError):
        insert_sensor_data(
            mock_conn,
            device_id,
            timestamp,
            temperature=1.1,
            humidity=2.2,
            pollen=3,
            particulate_matter=4,
        )

    mock_conn.rollback.assert_called_once()
    mock_cursor.close.assert_called_once()

@pytest.mark.parametrize(
    "driver_msg,expected_exc",
    [
        ("timeout while writing", DatabaseTimeoutError),
        ("could not connect to server", DatabaseConnectionError),
        ("some random db error", DatabaseError),
    ],
)
def test_driver_errors_mapped_and_rollback(mocker, driver_msg, expected_exc):
    device_id = 3
    timestamp = "2025-08-06T14:00:00Z"

    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception(driver_msg)

    with pytest.raises(expected_exc):
        insert_sensor_data(
            mock_conn,
            device_id,
            timestamp,
            temperature=10.0,
            humidity=20.0,
            pollen=30,
            particulate_matter=40,
        )

    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()
    mock_cursor.close.assert_called_once()

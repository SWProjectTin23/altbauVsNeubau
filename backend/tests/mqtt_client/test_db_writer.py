import pytest
from mqtt_client.db_writer import insert_sensor_data
from common.exceptions import DatabaseError, DatabaseTimeoutError, DatabaseConnectionError


def test_insert_sensor_data_complete_data(mocker):
    device_id = 2
    timestamp = "2025-08-06T13:00:00Z"

    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_cursor.rowcount = 1
    mock_conn.cursor.return_value = mock_cursor

    result = insert_sensor_data(
        mock_conn,
        device_id,
        timestamp,
        temperature=21.3,
        humidity=55,
        pollen=123,
        particulate_matter=78,
    )

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

    # Validate parameters (avoid brittle exact query string match)
    _, params = mock_cursor.execute.call_args[0]
    assert params == (device_id, timestamp, 21.3, 55, 123, 78)

    # Validate return payload
    assert result["device_id"] == device_id
    assert result["timestamp"] == timestamp
    assert result["updated_fields"] == {
        "temperature": 21.3,
        "humidity": 55,
        "pollen": 123,
        "particulate_matter": 78,
    }
    assert result["rows_affected"] == 1


def test_insert_sensor_data_allows_partial_data(mocker):
    device_id = 2
    timestamp = "2025-08-06T13:00:00Z"
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_cursor.rowcount = 1
    mock_conn.cursor.return_value = mock_cursor

    result = insert_sensor_data(
        mock_conn,
        device_id,
        timestamp,
        temperature=21.3,  # other fields omitted on purpose
    )

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

    _, params = mock_cursor.execute.call_args[0]
    assert params == (device_id, timestamp, 21.3, None, None, None)

    assert result["updated_fields"] == {
        "temperature": 21.3,
        "humidity": None,
        "pollen": None,
        "particulate_matter": None,
    }


def test_commit_failure_rolls_back_and_maps_timeout(mocker):
    device_id = 4
    timestamp = "2025-08-06T15:00:00Z"

    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit.side_effect = Exception("commit timed out")

    with pytest.raises(DatabaseTimeoutError):
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


def test_rollback_failure_is_swallowed_and_original_error_mapped(mocker):
    device_id = 5
    timestamp = "2025-08-06T16:00:00Z"

    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("unhandled db error")
    mock_conn.rollback.side_effect = Exception("rollback failed")

    with pytest.raises(DatabaseError):
        insert_sensor_data(
            mock_conn,
            device_id,
            timestamp,
            temperature=9.9,
        )

    mock_conn.commit.assert_not_called()
    mock_cursor.close.assert_called_once()

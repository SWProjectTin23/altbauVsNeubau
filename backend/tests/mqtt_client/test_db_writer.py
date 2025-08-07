from mqtt_client.db_writer import insert_sensor_data

def test_insert_sensor_data_all_metrics(mocker):
    # Shared device ID and timestamp for all inserts
    device_id = 2
    timestamp = "2025-08-06T13:00:00Z"

    # Mock database connection and cursor
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Simulate four separate insert calls, each with only one metric field
    insert_sensor_data(mock_conn, device_id, timestamp, temperature=21.3)
    insert_sensor_data(mock_conn, device_id, timestamp, humidity=55)
    insert_sensor_data(mock_conn, device_id, timestamp, pollen=123)
    insert_sensor_data(mock_conn, device_id, timestamp, particulate_matter=78)

    # Ensure that execute, commit, and cursor.close were called four times
    assert mock_cursor.execute.call_count == 4
    assert mock_conn.commit.call_count == 4
    assert mock_cursor.close.call_count == 4

    # Validate the parameters passed to each execute call
    expected_calls = [
        (device_id, timestamp, 21.3, None, None, None),
        (device_id, timestamp, None, 55, None, None),
        (device_id, timestamp, None, None, 123, None),
        (device_id, timestamp, None, None, None, 78),
    ]
    actual_calls = mock_cursor.execute.call_args_list

    for call, expected in zip(actual_calls, expected_calls):
        # Extract SQL parameter tuple from call arguments
        actual_args = call[0][1]
        assert actual_args == expected

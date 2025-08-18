from mqtt_client.handler import handle_metric

def valid_payload():
    return {
        "value": 22.5,
        "timestamp": "1722945600",
        "meta": {
            "device_id": 1
        }
    }

def test_valid_metric_calls_insert(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    handle_metric("temperature", "dhbw/ai/si2023/01/temperature/01", payload, mock_conn)

    mock_insert.assert_called_once()
    args, kwargs = mock_insert.call_args
    assert args[0] == mock_conn
    assert args[1] == 1  # device_id
    assert kwargs["temperature"] == 22.5

def test_missing_device_id_does_not_call_insert(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    del payload["meta"]["device_id"]

    handle_metric("temperature", "dhbw/ai/si2023/01/temperature/01", payload, mock_conn)
    mock_insert.assert_not_called()

def test_unknown_metric_does_not_call_insert(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    handle_metric("unknown_metric", "dhbw/ai/si2023/01/temperature/01", payload, mock_conn)
    mock_insert.assert_not_called()

def test_non_numeric_value_does_not_call_insert(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    payload["value"] = "not-a-number"

    handle_metric("temperature", "sdhbw/ai/si2023/01/temperature/01", payload, mock_conn)
    mock_insert.assert_not_called()

def test_value_out_of_range_does_not_call_insert(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    payload["value"] = 1000  # too high for temperature (0–40)

    handle_metric("temperature", "dhbw/ai/si2023/01/temperature/01", payload, mock_conn)
    mock_insert.assert_not_called()
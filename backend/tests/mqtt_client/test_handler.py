from datetime import datetime
import pytest
from mqtt_client.handler import handle_metric
from common.exceptions import DatabaseTimeoutError, DatabaseError

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
    mock_log = mocker.patch("mqtt_client.handler.log_event")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    handle_metric("temperature", "dhbw/ai/si2023/01/temperature/01", payload, mock_conn)

    mock_insert.assert_called_once()
    args, kwargs = mock_insert.call_args
    assert args[0] == mock_conn
    assert args[1] == 1  # device_id
    assert kwargs["temperature"] == 22.5
    # timestamp (positional arg index 2) should be a datetime
    assert isinstance(args[2], datetime)

    # success log emitted
    levels_events = [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
    assert ("INFO", "msg_processed") in levels_events

def test_missing_device_id(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_log = mocker.patch("mqtt_client.handler.log_event")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    del payload["meta"]["device_id"]

    handle_metric("temperature", "dhbw/ai/si2023/01/temperature/01", payload, mock_conn)
    mock_insert.assert_not_called()
    # warning path
    levels_events = [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
    assert ("WARNING", "value_out_of_range") in levels_events

def test_unknown_metric(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_log = mocker.patch("mqtt_client.handler.log_event")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    handle_metric("unknown_metric", "dhbw/ai/si2023/01/temperature/01", payload, mock_conn)
    mock_insert.assert_not_called()
    levels_events = [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
    assert ("WARNING", "value_out_of_range") in levels_events

def test_non_numeric_value(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_log = mocker.patch("mqtt_client.handler.log_event")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    payload["value"] = "not-a-number"

    handle_metric("temperature", "sdhbw/ai/si2023/01/temperature/01", payload, mock_conn)
    mock_insert.assert_not_called()
    levels_events = [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
    assert ("WARNING", "value_out_of_range") in levels_events

def test_value_out_of_range(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_log = mocker.patch("mqtt_client.handler.log_event")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    payload["value"] = 1000  # too high for temperature (0–40)

    handle_metric("temperature", "dhbw/ai/si2023/01/temperature/01", payload, mock_conn)
    mock_insert.assert_not_called()
    # reason should be min_max_check for out-of-range
    found = False
    for c in mock_log.call_args_list:
        if c.args[1] == "INFO" and c.args[2] == "value_out_of_range":
            if c.kwargs.get("reason") == "min_max_check":
                found = True
                break
    assert found


def test_integer_metric_accepts_float_int_value(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    payload["value"] = 12.0
    handle_metric("pollen", "dhbw/ai/si2023/01/pollen/01", payload, mock_conn)

    mock_insert.assert_called_once()
    _, kwargs = mock_insert.call_args
    assert kwargs["pollen"] == 12


def test_integer_metric_rejects_non_integer_float(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data")
    mock_log = mocker.patch("mqtt_client.handler.log_event")
    mock_conn = mocker.MagicMock()

    payload = valid_payload()
    payload["value"] = 12.3
    handle_metric("pollen", "dhbw/ai/si2023/01/pollen/01", payload, mock_conn)

    mock_insert.assert_not_called()
    # schema_mismatch for this validation failure
    found = False
    for c in mock_log.call_args_list:
        if c.args[1] == "WARNING" and c.args[2] == "value_out_of_range":
            if c.kwargs.get("reason") == "schema_mismatch":
                found = True
                break
    assert found


def test_db_timeout_error_is_logged(mocker):
    mock_insert = mocker.patch("mqtt_client.handler.insert_sensor_data", side_effect=DatabaseTimeoutError("timeout"))
    mock_log = mocker.patch("mqtt_client.handler.log_event")
    mock_conn = mocker.MagicMock()

    handle_metric("temperature", "topic", valid_payload(), mock_conn)

    # error path with reason timeout
    found = False
    for c in mock_log.call_args_list:
        if c.args[1] == "ERROR" and c.args[2] == "db_write_failed" and c.kwargs.get("reason") == "timeout":
            found = True
            break
    assert found


def test_db_generic_error_is_logged(mocker):
    mocker.patch("mqtt_client.handler.insert_sensor_data", side_effect=DatabaseError("db fail"))
    mock_log = mocker.patch("mqtt_client.handler.log_event")
    mock_conn = mocker.MagicMock()

    handle_metric("temperature", "topic", valid_payload(), mock_conn)

    found = False
    for c in mock_log.call_args_list:
        if c.args[1] == "ERROR" and c.args[2] == "db_write_failed" and c.kwargs.get("reason") == "db_error":
            found = True
            break
    assert found


def test_unexpected_error_is_logged(mocker):
    mocker.patch("mqtt_client.handler.insert_sensor_data", side_effect=Exception("boom"))
    mock_log = mocker.patch("mqtt_client.handler.log_event")
    mock_conn = mocker.MagicMock()

    handle_metric("temperature", "topic", valid_payload(), mock_conn)

    found = False
    for c in mock_log.call_args_list:
        if c.args[1] == "ERROR" and c.args[2] == "unhandled_exception" and c.kwargs.get("reason") == "unexpected":
            found = True
            break
    assert found
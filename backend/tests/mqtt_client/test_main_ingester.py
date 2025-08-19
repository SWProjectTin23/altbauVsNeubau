from unittest.mock import MagicMock
from mqtt_client.main_ingester import on_connect, on_disconnect, on_message, connect_db


def test_on_connect_success_subscribes(mocker):
    mock_client = MagicMock()
    mock_log = mocker.patch("mqtt_client.main_ingester.log_event")
    
    # Patch config variables
    mocker.patch("mqtt_client.main_ingester.MQTT_BASE_TOPIC", "test/topic")
    mocker.patch("mqtt_client.main_ingester.QOS", 1)

    on_connect(mock_client, {}, {}, 0)

    mock_client.subscribe.assert_called_once_with("test/topic/+/+", 1)
    # Logs INFO mqtt_connected
    levels_events = [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
    assert ("INFO", "mqtt_connected") in levels_events


def test_on_connect_failure(mocker):
    mock_client = MagicMock()
    mock_log = mocker.patch("mqtt_client.main_ingester.log_event")
    mocker.patch("mqtt_client.main_ingester.MQTT_BASE_TOPIC", "test/topic")
    mocker.patch("mqtt_client.main_ingester.QOS", 1)
    on_connect(mock_client, {}, {}, 1)

    mock_client.subscribe.assert_not_called()
    levels_events = [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
    assert ("ERROR", "mqtt_connected") in levels_events


def test_on_disconnect_logs_clean_vs_unexpected(mocker):
    mock_log = mocker.patch("mqtt_client.main_ingester.log_event")
    client = MagicMock()

    on_disconnect(client, {}, 0)
    on_disconnect(client, {}, 5)

    # Expect one INFO clean and one WARNING unexpected
    assert ("INFO", "mqtt_disconnected") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
    assert ("WARNING", "mqtt_disconnected") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_on_message_valid_payload_calls_handler(mocker):
    mock_msg = MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/01/ikea/01"
    mock_msg.payload = b'{"value": 6, "timestamp": "1722945600", "meta": {"device_id": 1}}'

    mock_handle = mocker.patch("mqtt_client.main_ingester.handle_metric")
    db_conn = MagicMock()
    userdata = {"db_connection": db_conn}

    on_message(MagicMock(), userdata, mock_msg)

    mock_handle.assert_called_once()
    metric, topic, payload, conn = mock_handle.call_args[0]
    assert metric == "pollen"
    assert topic == mock_msg.topic
    assert conn == db_conn


def test_on_message_unknown_metric_skips(mocker):
    mock_msg = MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/01/ikea/99"  # invalid id
    mock_msg.payload = b'{"value": 6, "timestamp": "1722945600", "meta": {"device_id": 1}}'

    mock_handle = mocker.patch("mqtt_client.main_ingester.handle_metric")
    mock_log = mocker.patch("mqtt_client.main_ingester.log_event")
    on_message(MagicMock(), {"db_connection": MagicMock()}, mock_msg)

    mock_handle.assert_not_called()
    # schema mismatch log
    assert ("WARNING", "value_out_of_range") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_on_message_short_topic_logs_schema_mismatch(mocker):
    mock_msg = MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/ikea"  # too short
    mock_msg.payload = b"{}"

    mock_handle = mocker.patch("mqtt_client.main_ingester.handle_metric")
    mock_log = mocker.patch("mqtt_client.main_ingester.log_event")

    on_message(MagicMock(), {"db_connection": MagicMock()}, mock_msg)

    mock_handle.assert_not_called()
    assert ("WARNING", "value_out_of_range") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_on_message_bad_json_logs_and_skips(mocker):
    mock_msg = MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/01/ikea/01"
    mock_msg.payload = b"{not-json}"

    mock_handle = mocker.patch("mqtt_client.main_ingester.handle_metric")
    mock_log = mocker.patch("mqtt_client.main_ingester.log_event")

    on_message(MagicMock(), {"db_connection": MagicMock()}, mock_msg)

    mock_handle.assert_not_called()
    assert ("WARNING", "value_out_of_range") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_on_message_handler_raises_is_caught_and_logged(mocker):
    mock_msg = MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/01/ikea/01"
    mock_msg.payload = b'{"value": 6, "timestamp": "1722945600", "meta": {"device_id": 1}}'

    mocker.patch("mqtt_client.main_ingester.handle_metric", side_effect=Exception("boom"))
    mock_log = mocker.patch("mqtt_client.main_ingester.log_event")

    on_message(MagicMock(), {"db_connection": MagicMock()}, mock_msg)

    assert ("ERROR", "unhandled_exception") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
    

def test_connect_db_success(mocker):
    mock_psycopg = mocker.patch("mqtt_client.main_ingester.psycopg2.connect")
    mock_conn = MagicMock()
    mock_psycopg.return_value = mock_conn
    mock_log = mocker.patch("mqtt_client.main_ingester.log_event")

    # Patch config variables
    mocker.patch("mqtt_client.main_ingester.DB_HOST", "localhost")
    mocker.patch("mqtt_client.main_ingester.DB_NAME", "testdb")
    mocker.patch("mqtt_client.main_ingester.DB_USER", "user")
    mocker.patch("mqtt_client.main_ingester.DB_PASSWORD", "pass")
    mocker.patch("mqtt_client.main_ingester.DB_PORT", 5432)

    conn = connect_db()

    assert conn == mock_conn
    mock_psycopg.assert_called_once()
    # autocommit is disabled
    assert mock_conn.autocommit == False
    # info log
    assert ("INFO", "db_connected") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]


def test_connect_db_failure(mocker):
    mocker.patch("mqtt_client.main_ingester.psycopg2.connect", side_effect=Exception("fail"))
    mock_log = mocker.patch("mqtt_client.main_ingester.log_event")

    # Patch config variables
    mocker.patch("mqtt_client.main_ingester.DB_HOST", "localhost")
    mocker.patch("mqtt_client.main_ingester.DB_NAME", "testdb")
    mocker.patch("mqtt_client.main_ingester.DB_USER", "user")
    mocker.patch("mqtt_client.main_ingester.DB_PASSWORD", "pass")
    mocker.patch("mqtt_client.main_ingester.DB_PORT", 5432)

    conn = connect_db()

    assert conn is None
    assert ("ERROR", "db_connect_failed") in [(c.args[1], c.args[2]) for c in mock_log.call_args_list]
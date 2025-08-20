from unittest.mock import MagicMock
from mqtt_client.main_ingester import on_connect, on_message, connect_db


def test_on_connect_success_subscribes(mocker):
    mock_client = MagicMock()
    
    # Patch config variables
    mocker.patch("mqtt_client.main_ingester.MQTT_BASE_TOPIC", "test/topic")
    mocker.patch("mqtt_client.main_ingester.QOS", 1)

    on_connect(mock_client, {}, {}, 0)

    mock_client.subscribe.assert_called_once_with("test/topic/+/+", 1)


def test_on_connect_failure(mocker):
    mock_client = MagicMock()
    mocker.patch("mqtt_client.main_ingester.MQTT_BASE_TOPIC", "test/topic")
    mocker.patch("mqtt_client.main_ingester.QOS", 1)
    on_connect(mock_client, {}, {}, 1)

    mock_client.subscribe.assert_not_called()


def test_on_message_valid_payload_calls_handler(mocker):
    mock_msg = MagicMock()
    mock_msg.topic = "dhbw/ai/si2023/01/ikea/01"
    mock_msg.payload = b'{"value": 6, "timestamp": "1722945600", "meta": {"device_id": 1}}'

    mock_handle = mocker.patch("mqtt_client.main_ingester.handle_metric")
    db_conn = MagicMock()
    db_conn.closed = False  # Simulate open connection
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
    db_conn = MagicMock()
    on_message(MagicMock(), {"db_connection": db_conn}, mock_msg)

    mock_handle.assert_not_called()
    

def test_connect_db_success(mocker):
    mock_psycopg = mocker.patch("mqtt_client.main_ingester.psycopg2.connect")
    mock_conn = MagicMock()
    mock_psycopg.return_value = mock_conn

    # Patch config variables
    mocker.patch("mqtt_client.main_ingester.DB_HOST", "localhost")
    mocker.patch("mqtt_client.main_ingester.DB_NAME", "testdb")
    mocker.patch("mqtt_client.main_ingester.DB_USER", "user")
    mocker.patch("mqtt_client.main_ingester.DB_PASSWORD", "pass")
    mocker.patch("mqtt_client.main_ingester.DB_PORT", 5432)

    conn = connect_db()

    assert conn == mock_conn
    mock_psycopg.assert_called_once()


def test_connect_db_failure(mocker):
    mocker.patch("mqtt_client.main_ingester.psycopg2.connect", side_effect=Exception("fail"))

    # Patch config variables
    mocker.patch("mqtt_client.main_ingester.DB_HOST", "localhost")
    mocker.patch("mqtt_client.main_ingester.DB_NAME", "testdb")
    mocker.patch("mqtt_client.main_ingester.DB_USER", "user")
    mocker.patch("mqtt_client.main_ingester.DB_PASSWORD", "pass")
    mocker.patch("mqtt_client.main_ingester.DB_PORT", 5432)

    conn = connect_db()

    assert conn is None
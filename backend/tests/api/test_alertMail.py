from api.db import get_db_connection
from unittest.mock import MagicMock
import psycopg2

def test_get_alertMail_success(client, mocker):

    """
    Tests the GET endpoint /api/alert_email for a successful email retrieval.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('api.alertMail.get_db_connection', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ("test@example.com",)
    response = client.get('/api/alert_email')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['email'] == 'test@example.com'
    mock_cursor.execute.assert_called_once_with("SELECT email FROM alert_emails LIMIT 1")
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

def test_get_alertMail_not_found(client, mocker):
    """
    Tests the GET endpoint /api/alert_email when no email is found.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('api.alertMail.get_db_connection', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    response = client.get('/api/alert_email')
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'No mail found.'
    mock_cursor.execute.assert_called_once_with("SELECT email FROM alert_emails LIMIT 1")
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

def test_get_alertMail_database_error(client, mocker):
    """
    Tests the GET endpoint /api/alert_email in case of a database error.
    """
    mocker.patch('api.alertMail.get_db_connection', side_effect=psycopg2.Error("Database connection failed"))

    response = client.get('/api/alert_email')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Database connection failed' in json_data['message']

def test_post_alertMail_success(client, mocker):
    """
    Tests the POST endpoint /api/alert_email for a successful email saving.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('api.alertMail.get_db_connection', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    email_data = {"alert_email": "new_email@example.com"}
    response = client.post('/api/alert_email', json=email_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == 'Alert email saved.'
    mock_cursor.execute.assert_any_call("DELETE FROM alert_emails")
    mock_cursor.execute.assert_any_call("INSERT INTO alert_emails (email) VALUES (%s)", ("new_email@example.com",))
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

def test_post_alertMail_missing_data(client, mocker):
    """
    Tests the POST endpoint /api/alert_email when email data is missing from the payload.
    """
    mocker.patch('api.alertMail.get_db_connection')

    response = client.post('/api/alert_email', json={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Mail is missing.'

def test_post_alertMail_database_error(client, mocker):
    """
    Tests the POST endpoint /api/alert_email in case of a database error.
    """
    mocker.patch('api.alertMail.get_db_connection', side_effect=psycopg2.Error("Database connection failed"))

    email_data = {"alert_email": "test@example.com"}
    response = client.post('/api/alert_email', json=email_data)
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Database connection failed' in json_data['message']
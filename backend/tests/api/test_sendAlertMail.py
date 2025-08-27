import pytest
from unittest.mock import MagicMock
import psycopg2
import smtplib

@pytest.fixture
def test_data():
    """Fixture to provide a standard set of test data."""
    return {
        "device": "Arduino01",
        "metric": "Temperatur",
        "value": 25,
        "thresholds": {
            "Temperatur": {
                "redLow": 5, "yellowLow": 10, "yellowHigh": 30, "redHigh": 35
            }
        }
    }

def test_post_send_alert_mail_missing_parameters(client, mocker):
    """Test with missing parameters -> 400 Bad Request."""
    mock_log_event = mocker.patch('api.sendAlertMail.log_event')
    response = client.post('/api/send_alert_mail', json={})
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Missing parameters'
    mock_log_event.assert_called_once()

def test_post_send_alert_mail_unknown_metric(client, mocker, test_data):
    """Test with unknown metric -> 400 Bad Request."""
    mock_log_event = mocker.patch('api.sendAlertMail.log_event')
    test_data['metric'] = 'UnbekannteMetrik'
    response = client.post('/api/send_alert_mail', json=test_data)
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Unknown metric'
    mock_log_event.assert_called_once()

def test_post_red_alert_triggered_sends_mail(client, mocker, test_data):
    """Test for a red alert: mail should be sent and cooldown set."""
    mock_send_mail = mocker.patch('api.sendAlertMail.send_mail')
    mocker.patch('api.sendAlertMail.get_alert_email', return_value="test@example.com")
    mocker.patch('api.sendAlertMail.is_alert_active', return_value=False)
    mock_set_alert_active = mocker.patch('api.sendAlertMail.set_alert_active')
    mock_reset_alert = mocker.patch('api.sendAlertMail.reset_alert')
    mock_log_event = mocker.patch('api.sendAlertMail.log_event')
    test_data['value'] = 40
    response = client.post('/api/send_alert_mail', json=test_data)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'hart-Mail sent'
    mock_send_mail.assert_called_once()
    mock_set_alert_active.assert_called_once_with("Arduino01", "Temperatur", "hart")
    mock_reset_alert.assert_not_called()
    mock_log_event.assert_called()

def test_post_red_alert_cooldown_active(client, mocker, test_data):
    """Test for a red alert when cooldown is already active: no mail should be sent."""
    mocker.patch('api.sendAlertMail.send_mail')
    mocker.patch('api.sendAlertMail.get_alert_email', return_value="test@example.com")
    mocker.patch('api.sendAlertMail.is_alert_active', return_value=True)
    mocker.patch('api.sendAlertMail.set_alert_active')
    mock_log_event = mocker.patch('api.sendAlertMail.log_event')
    test_data['value'] = 40
    response = client.post('/api/send_alert_mail', json=test_data)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'hart-Mail already active'
    mock_log_event.assert_called()

def test_post_yellow_alert_triggered_sends_mail(client, mocker, test_data):
    """Test for a yellow alert: mail should be sent and cooldown set."""
    mock_send_mail = mocker.patch('api.sendAlertMail.send_mail')
    mocker.patch('api.sendAlertMail.get_alert_email', return_value="test@example.com")
    mocker.patch('api.sendAlertMail.is_alert_active', return_value=False)
    mock_set_alert_active = mocker.patch('api.sendAlertMail.set_alert_active')
    mock_reset_alert = mocker.patch('api.sendAlertMail.reset_alert')
    mock_log_event = mocker.patch('api.sendAlertMail.log_event')
    test_data['value'] = 32
    response = client.post('/api/send_alert_mail', json=test_data)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'soft-Mail sent'
    mock_send_mail.assert_called_once()
    mock_set_alert_active.assert_called_once_with("Arduino01", "Temperatur", "soft")
    mock_reset_alert.assert_not_called()
    mock_log_event.assert_called()

def test_post_yellow_alert_cooldown_active(client, mocker, test_data):
    """Test for a yellow alert when cooldown is already active: no mail should be sent."""
    mocker.patch('api.sendAlertMail.send_mail')
    mocker.patch('api.sendAlertMail.get_alert_email', return_value="test@example.com")
    mocker.patch('api.sendAlertMail.is_alert_active', return_value=True)
    mocker.patch('api.sendAlertMail.set_alert_active')
    mock_log_event = mocker.patch('api.sendAlertMail.log_event')
    test_data['value'] = 32
    response = client.post('/api/send_alert_mail', json=test_data)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'soft-Mail already active'
    mock_log_event.assert_called()

def test_post_value_in_normal_range_resets_alert(client, mocker, test_data):
    """Test when the value is back in the normal range: alerts should be reset."""
    mocker.patch('api.sendAlertMail.send_mail')
    mock_reset_alert = mocker.patch('api.sendAlertMail.reset_alert')
    mock_set_alert_active = mocker.patch('api.sendAlertMail.set_alert_active')
    mock_log_event = mocker.patch('api.sendAlertMail.log_event')
    test_data['value'] = 20
    response = client.post('/api/send_alert_mail', json=test_data)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'No Threshold Exceeded'
    mock_reset_alert.assert_any_call("Arduino01", "Temperatur", "hart")
    mock_reset_alert.assert_any_call("Arduino01", "Temperatur", "soft")
    mock_set_alert_active.assert_not_called()
    mock_log_event.assert_called()

def test_post_database_error_on_get_email(client, mocker, test_data):
    """Test when a database error occurs during email retrieval."""
    mock_log_event = mocker.patch('api.sendAlertMail.log_event')
    mock_get_alert_email = mocker.patch('api.sendAlertMail.get_alert_email', side_effect=psycopg2.Error("DB Error"))
    mocker.patch('api.sendAlertMail.is_alert_active', return_value=False)
    
    test_data['value'] = 40
    response = client.post('/api/send_alert_mail', json=test_data)
    
    assert response.status_code == 500
    assert "DB Error" in response.get_json()['message']
    mock_get_alert_email.assert_called_once()
    mock_log_event.assert_called()

def test_post_send_mail_failure(client, mocker, test_data):
    """Test when the mail sending fails."""
    mocker.patch('api.sendAlertMail.get_alert_email', return_value="test@example.com")
    mocker.patch('api.sendAlertMail.is_alert_active', return_value=False)
    mocker.patch('api.sendAlertMail.set_alert_active')
    mock_send_mail = mocker.patch('api.sendAlertMail.send_mail', side_effect=smtplib.SMTPException("SMTP Failure"))
    mock_log_event = mocker.patch('api.sendAlertMail.log_event')
    test_data['value'] = 40
    response = client.post('/api/send_alert_mail', json=test_data)
    assert response.status_code == 500
    assert "SMTP Failure" in response.get_json()['message']
    mock_send_mail.assert_called_once()
    mock_log_event.assert_called()
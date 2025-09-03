import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from api.sendAlertMail import SendAlertMail

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.add_url_rule("/alert", view_func=SendAlertMail.as_view("send_alert_mail"))
    return app.test_client()


# ---- Success: hart alert ----
@patch("api.sendAlertMail.send_mail")
@patch("api.sendAlertMail.get_alert_email", return_value="test@example.com")
@patch("api.sendAlertMail.is_alert_active", return_value=False)
@patch("api.sendAlertMail.set_alert_active")


def test_hart_alert(mock_set_alert_active, mock_is_active, mock_get_email, mock_send_mail, client):
    payload = {
        "metric": "Temperatur",
        "value": 60,
        "device": "ABC123",
        "thresholds": {
            "Temperatur": {
                "redLow": -10,
                "redHigh": 50,
                "yellowLow": 0,
                "yellowHigh": 40
            }
        }
    }
    response = client.post("/alert", json=payload)
    assert response.status_code == 200
    assert b"hart-Mail sent" in response.data
    mock_send_mail.assert_called_once()
    mock_set_alert_active.assert_called_once()


# ---- Success: soft alert ----
@patch("api.sendAlertMail.send_mail")
@patch("api.sendAlertMail.get_alert_email", return_value="test@example.com")
@patch("api.sendAlertMail.is_alert_active", return_value=False)
@patch("api.sendAlertMail.set_alert_active")
def test_soft_alert(mock_set_alert_active, mock_is_active, mock_get_email, mock_send_mail, client):
    payload = {
        "metric": "Temperatur",
        "value": 45,
        "device": "ABC123",
        "thresholds": {
            "Temperatur": {
                "redLow": -10,
                "redHigh": 50,
                "yellowLow": 0,
                "yellowHigh": 40
            }
        }
    }
    response = client.post("/alert", json=payload)
    assert response.status_code == 200
    assert b"soft-Mail sent" in response.data


# ---- Already active alert ----
@patch("api.sendAlertMail.send_mail")
@patch("api.sendAlertMail.get_alert_email")
@patch("api.sendAlertMail.is_alert_active", return_value=True)
def test_alert_already_active(mock_is_active, mock_get_email, mock_send_mail, client):
    payload = {
        "metric": "Temperatur",
        "value": 60,
        "device": "ABC123",
        "thresholds": {
            "Temperatur": {
                "redLow": -10,
                "redHigh": 50,
                "yellowLow": 0,
                "yellowHigh": 40
            }
        }
    }
    response = client.post("/alert", json=payload)
    assert response.status_code == 200
    assert b"already active" in response.data
    mock_send_mail.assert_not_called()


# ---- Normal range -> reset alert ----
@patch("api.sendAlertMail.reset_alert")
def test_reset_alert_on_normal_value(mock_reset_alert, client):
    payload = {
        "metric": "Temperatur",
        "value": 25,
        "device": "ABC123",
        "thresholds": {
            "Temperatur": {
                "redLow": -10,
                "redHigh": 50,
                "yellowLow": 0,
                "yellowHigh": 40
            }
        }
    }
    response = client.post("/alert", json=payload)
    assert response.status_code == 200
    assert b"No Threshold Exceeded" in response.data
    assert mock_reset_alert.call_count == 2


# ---- Missing parameter ----
def test_missing_parameters(client):
    payload = {
        "value": 25,
        "device": "ABC123",
        "thresholds": {}
    }
    response = client.post("/alert", json=payload)
    assert response.status_code == 400
    assert b"Missing parameters" in response.data


# ---- Unknown metric ----
def test_unknown_metric(client):
    payload = {
        "metric": "Unbekannt",
        "value": 25,
        "device": "ABC123",
        "thresholds": {
            "Temperatur": {
                "redLow": -10,
                "redHigh": 50
            }
        }
    }
    response = client.post("/alert", json=payload)
    assert response.status_code == 400
    assert b"Unknown metric" in response.data

@patch("api.sendAlertMail.send_mail", side_effect=Exception("SMTP failed"))
@patch("api.sendAlertMail.get_alert_email", return_value="test@example.com")
@patch("api.sendAlertMail.is_alert_active", return_value=False)
def test_send_mail_exception(mock_is_active, mock_get_email, mock_send_mail, client):
    payload = {
        "metric": "Temperatur",
        "value": 60,
        "device": "ABC123",
        "thresholds": {
            "Temperatur": {
                "redLow": -10,
                "redHigh": 50,
                "yellowLow": 0,
                "yellowHigh": 40
            }
        }
    }
    response = client.post("/alert", json=payload)
    assert response.status_code == 500
    assert "SMTP failed" in response.json["message"]
    assert response.json["status"] == "error"


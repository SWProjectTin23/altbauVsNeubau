import pytest
from unittest.mock import patch

@pytest.fixture
def email_data():
    return {"alert_email": "test@example.com"}

@patch("api.alertMail.get_alert_email", return_value="test@example.com")
def test_get_alert_email_success(mock_get_email, client):
    response = client.get("/api/alert_email")
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["email"] == "test@example.com"
    mock_get_email.assert_called_once()

@patch("api.alertMail.get_alert_email", return_value=None)
def test_get_alert_email_not_found(mock_get_email, client):
    response = client.get("/api/alert_email")
    assert response.status_code == 404
    assert response.json["status"] == "error"
    assert response.json["message"] == "No mail found."
    mock_get_email.assert_called_once()

@patch("api.alertMail.get_alert_email", side_effect=Exception("DB error"))
def test_get_alert_email_exception(mock_get_email, client):
    response = client.get("/api/alert_email")
    assert response.status_code == 500
    assert response.json["status"] == "error"
    assert "DB error" in response.json["message"]

@patch("api.alertMail.set_alert_email", return_value="sometoken123")
@patch("api.alertMail.send_mail")
def test_post_alert_email_confirmation_sent(mock_send_mail, mock_set_email, client, email_data):
    response = client.post("/api/alert_email", json=email_data)
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["message"] == "Confirmation mail sent."
    mock_set_email.assert_called_once_with(email_data["alert_email"])
    mock_send_mail.assert_called_once()

def test_post_alert_email_missing(client):
    response = client.post("/api/alert_email", json={})
    assert response.status_code == 400
    assert response.json["status"] == "error"
    assert response.json["message"] == "Mail is missing."

@patch("api.alertMail.set_alert_email", side_effect=Exception("DB write error"))
def test_post_alert_email_exception(mock_set_email, client, email_data):
    response = client.post("/api/alert_email", json=email_data)
    assert response.status_code == 500
    assert response.json["status"] == "error"
    assert "DB write error" in response.json["message"]
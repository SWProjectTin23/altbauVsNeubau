import pytest
from unittest.mock import patch

@pytest.fixture
def client(app):
    return app.test_client()

@patch("api.confirm_mail.get_db_connection")
def test_confirm_email_success(mock_get_db, client):
    mock_conn = mock_get_db.return_value
    mock_cur = mock_conn.cursor.return_value
    mock_cur.fetchone.return_value = ("test@example.com",)
    response = client.post("/api/confirm_email", json={"token": "validtoken"})
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["email"] == "test@example.com"

@patch("api.confirm_mail.get_db_connection")
def test_confirm_email_invalid_token(mock_get_db, client):
    mock_conn = mock_get_db.return_value
    mock_cur = mock_conn.cursor.return_value
    mock_cur.fetchone.return_value = None
    response = client.post("/api/confirm_email", json={"token": "invalidtoken"})
    assert response.status_code == 400
    assert response.json["status"] == "error"
    assert "Invalid token" in response.json["message"]

def test_confirm_email_missing_token(client):
    response = client.post("/api/confirm_email", json={})
    assert response.status_code == 400
    assert response.json["status"] == "error"
    assert "Token missing" in response.json["message"]
import pytest
from app import create_app

@pytest.fixture
def client():
    """
    Create a test client for the Flask application.
    """
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
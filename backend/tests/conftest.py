import pytest
from api import create_app
import os
from unittest.mock import patch


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(autouse=True)
def set_test_environment():
    os.environ["TESTING"] = "True"



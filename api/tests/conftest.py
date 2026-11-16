import pytest
from fastapi.testclient import TestClient
from api.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

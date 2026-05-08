import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Fresh database before each test — no leftover data between tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_health():
    """Verify the smoke-test endpoint returns 200 and the correct body."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_faults_returns_list():
    response = client.get("/api/faults")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_tools_returns_list():
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
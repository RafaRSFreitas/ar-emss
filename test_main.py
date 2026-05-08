from fastapi.testclient import TestClient
from main import app
from database import Base, engine

# Recreate all tables before each test (this mimics "fresh database" from the lab)
def setup_module():
    Base.metadata.create_all(bind=engine)

def teardown_module():
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)


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
    assert len(data) == 0
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


#----------- Helpers -----------

TEST_USER = {"username": "testuser", "password": "secret123"}


def register_user():
    """Register TEST_USER via POST /register."""
    return client.post("/register", json=TEST_USER)


def login_get_token():
    """Login TEST_USER and return the Bearer token string."""
    resp = client.post("/login", json=TEST_USER)
    assert resp.status_code == 200, f"login failed: {resp.text}"
    return resp.json()["access_token"]


def auth_header(token: str) -> dict:
    """Shorthand for the Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}


#----------- Smoke test (existing, kept for TEST-2 continuity) -----------

def test_health():
    """Verify the smoke-test endpoint returns 200 and the correct body."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_faults_returns_list():
    """GET /api/faults returns an empty list when DB is clean."""
    response = client.get("/api/faults")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_tools_returns_list():
    """GET /api/tools returns an empty list when DB is clean."""
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


#----------- FAULT HAPPY PATH -----------

def test_fault_happy_path():
    """Full fault lifecycle: register → login → create → patch → get → filter."""
    # Arrange — user must exist before create_fault can assign user_id
    register_user()
    token = login_get_token()
    headers = auth_header(token)

    # Act — create a fault
    create_resp = client.post("/api/faults", json={
        "title": "Cracked panel",
        "location": "Bay 4",
        "severity": 2
    }, headers=headers)

    # Assert — 201 with id and expected fields
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["title"] == "Cracked panel"
    assert created["location"] == "Bay 4"
    assert created["severity"] == 2
    assert created["status"] == "open"
    assert "id" in created
    fault_id = created["id"]

    # Act — patch status to closed
    patch_resp = client.patch(f"/api/faults/{fault_id}", json={
        "status": "closed"
    })
    assert patch_resp.status_code == 200
    patched = patch_resp.json()
    assert patched["status"] == "closed"

    # Act — GET single fault shows updated status
    get_resp = client.get(f"/api/faults/{fault_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "closed"

    # Act — filter by status=closed returns the fault
    filter_resp = client.get("/api/faults?status=closed")
    assert filter_resp.status_code == 200
    filtered = filter_resp.json()
    assert len(filtered) == 1
    assert filtered[0]["id"] == fault_id

    # cleanup — filter by status=open returns empty
    open_resp = client.get("/api/faults?status=open")
    assert open_resp.status_code == 200
    assert len(open_resp.json()) == 0


#----------- TOOL HAPPY PATH -----------

def test_tool_happy_path():
    """Full tool lifecycle: create → patch → list."""
    # Act — create a tool (no auth required)
    create_resp = client.post("/api/tools", json={
        "name": "Impact wrench"
    })

    # Assert — 201 with id, name, checked_in status
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == "Impact wrench"
    assert created["status"] == "checked_in"
    assert "id" in created
    tool_id = created["id"]

    # Act — patch status to checked_out
    patch_resp = client.patch(f"/api/tools/{tool_id}", json={
        "status": "checked_out"
    })
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "checked_out"

    # Act — GET single tool shows updated
    get_resp = client.get(f"/api/tools/{tool_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "checked_out"

    # Act — list includes the tool
    list_resp = client.get("/api/tools")
    assert list_resp.status_code == 200
    ids = [t["id"] for t in list_resp.json()]
    assert tool_id in ids


#----------- NEGATIVE / ERROR CASES -----------

def test_fault_404_standard_error():
    """GET /api/faults/99999 returns 404 with REL-1 standard error shape."""
    resp = client.get("/api/faults/99999")

    assert resp.status_code == 404
    body = resp.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "http_error"
    assert "Fault not found" in body["error"]["message"]


def test_tool_404_standard_error():
    """GET /api/tools/99999 returns 404 with REL-1 standard error shape."""
    resp = client.get("/api/tools/99999")

    assert resp.status_code == 404
    body = resp.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "http_error"
    assert "Tool not found" in body["error"]["message"]


def test_fault_create_422_validation():
    """POST /api/faults with invalid payload returns 422 + details."""
    register_user()
    token = login_get_token()
    headers = auth_header(token)

    # title too short (< 3)
    resp = client.post("/api/faults", json={
        "title": "AB",
        "location": "Bay 1",
        "severity": 1
    }, headers=headers)

    assert resp.status_code == 422
    body = resp.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "validation_error"
    assert "details" in body["error"]


def test_fault_patch_422_invalid_status():
    """PATCH /api/faults/{id} with invalid status returns 422 + details."""
    # first create a fault (need user + token)
    register_user()
    token = login_get_token()
    create_resp = client.post("/api/faults", json={
        "title": "Leak",
        "location": "Pipe 2",
        "severity": 1
    }, headers=auth_header(token))
    fault_id = create_resp.json()["id"]

    # Act — patch with invalid status
    resp = client.patch(f"/api/faults/{fault_id}", json={
        "status": "broken"
    })

    assert resp.status_code == 422
    body = resp.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "validation_error"
    assert "details" in body["error"]


#----------- AUTH BOUNDARY TESTS -----------

def test_create_fault_without_token_returns_401():
    """POST /api/faults without Authorization → 401 + standard error shape."""
    resp = client.post("/api/faults", json={
        "title": "No auth test",
        "location": "Lab",
        "severity": 1
    })

    assert resp.status_code in (401, 403)
    body = resp.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "http_error"


def test_create_fault_with_token_succeeds():
    """POST /api/faults with valid token → 201."""
    register_user()
    token = login_get_token()

    resp = client.post("/api/faults", json={
        "title": "Auth success test",
        "location": "Workshop",
        "severity": 3
    }, headers=auth_header(token))

    assert resp.status_code == 201
    assert resp.json()["title"] == "Auth success test"

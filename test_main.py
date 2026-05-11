import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine
import time

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


def get_headers():
    """Register user + login + return auth headers (one-liner for tests)."""
    register_user()
    token = login_get_token()
    return auth_header(token)


#----------- Smoke test -----------

def test_health():
    """Verify the smoke-test endpoint returns 200 and the correct body."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_faults_returns_list():
    """GET /api/faults returns an empty list when DB is clean. (needs auth)"""
    headers = get_headers()
    response = client.get("/api/faults", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_tools_returns_list():
    """GET /api/tools returns an empty list when DB is clean. (needs auth)"""
    headers = get_headers()
    response = client.get("/api/tools", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


#----------- FAULT HAPPY PATH -----------

def test_fault_happy_path():
    """Full fault lifecycle: register → login → create → patch → get → filter."""
    headers = get_headers()

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
    }, headers=headers)
    assert patch_resp.status_code == 200
    patched = patch_resp.json()
    assert patched["status"] == "closed"

    # Act — GET single fault shows updated status
    get_resp = client.get(f"/api/faults/{fault_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "closed"

    # Act — filter by status=closed returns the fault
    filter_resp = client.get("/api/faults?status=closed", headers=headers)
    assert filter_resp.status_code == 200
    filtered = filter_resp.json()
    assert len(filtered) == 1
    assert filtered[0]["id"] == fault_id

    # cleanup — filter by status=open returns empty
    open_resp = client.get("/api/faults?status=open", headers=headers)
    assert open_resp.status_code == 200
    assert len(open_resp.json()) == 0


#----------- TOOL HAPPY PATH -----------

def test_tool_happy_path():
    """Full tool lifecycle: create → patch → list. (all calls need auth)"""
    headers = get_headers()

    # Act — create a tool
    create_resp = client.post("/api/tools", json={
        "name": "Impact wrench"
    }, headers=headers)

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
    }, headers=headers)
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "checked_out"

    # Act — GET single tool shows updated
    get_resp = client.get(f"/api/tools/{tool_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "checked_out"

    # Act — list includes the tool
    list_resp = client.get("/api/tools", headers=headers)
    assert list_resp.status_code == 200
    ids = [t["id"] for t in list_resp.json()]
    assert tool_id in ids


#----------- NEGATIVE / ERROR CASES -----------

def test_fault_404_standard_error():
    """GET /api/faults/99999 returns 404 with REL-1 standard error shape."""
    headers = get_headers()
    resp = client.get("/api/faults/99999", headers=headers)

    assert resp.status_code == 404
    body = resp.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "http_error"
    assert "Fault not found" in body["error"]["message"]


def test_tool_404_standard_error():
    """GET /api/tools/99999 returns 404 with REL-1 standard error shape."""
    headers = get_headers()
    resp = client.get("/api/tools/99999", headers=headers)

    assert resp.status_code == 404
    body = resp.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "http_error"
    assert "Tool not found" in body["error"]["message"]


def test_fault_create_422_validation():
    """POST /api/faults with invalid payload returns 422 + details."""
    headers = get_headers()

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
    headers = get_headers()

    # first create a valid fault
    create_resp = client.post("/api/faults", json={
        "title": "Leak",
        "location": "Pipe 2",
        "severity": 1
    }, headers=headers)
    fault_id = create_resp.json()["id"]

    # Act — patch with invalid status (needs auth since mainsecupdate)
    resp = client.patch(f"/api/faults/{fault_id}", json={
        "status": "broken"
    }, headers=headers)

    assert resp.status_code == 422
    body = resp.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "validation_error"
    assert "details" in body["error"]


#----------- AUTH BOUNDARY TESTS -----------

def test_endpoints_without_token_return_401():
    """Every protected endpoint returns 401 when no Authorization header."""
    endpoints = [
        ("GET", "/api/faults"),
        ("POST", "/api/faults", {"title": "Test", "location": "Lab", "severity": 1}),
        ("GET", "/api/faults/1"),
        ("PATCH", "/api/faults/1", {"status": "closed"}),
        ("GET", "/api/tools"),
        ("POST", "/api/tools", {"name": "Wrench"}),
        ("GET", "/api/tools/1"),
        ("PATCH", "/api/tools/1", {"status": "checked_out"}),
    ]

    for ep in endpoints:
        method = ep[0]
        path = ep[1]
        body = ep[2] if len(ep) > 2 else None

        if method == "GET":
            resp = client.get(path)
        elif method == "POST":
            resp = client.post(path, json=body)
        elif method == "PATCH":
            resp = client.patch(path, json=body)

        assert resp.status_code in (401, 403), (
            f"{method} {path} expected 401/403, got {resp.status_code}"
        )
        body_json = resp.json()
        assert body_json["ok"] is False
        assert body_json["error"]["type"] == "http_error"


def test_create_fault_with_token_succeeds():
    """POST /api/faults with valid token → 201."""
    headers = get_headers()

    resp = client.post("/api/faults", json={
        "title": "Auth success test",
        "location": "Workshop",
        "severity": 3
    }, headers=headers)

    assert resp.status_code == 201
    assert resp.json()["title"] == "Auth success test"


#----------- NEW TESTS (items 1, 3, 4) -----------

def test_delete_fault_success():
    """DELETE /api/faults/{id} removes a fault and returns 204, then 404."""
    headers = get_headers()

    # create a fault
    create_resp = client.post("/api/faults", json={
        "title": "Worn cable",
        "location": "Ceiling 2",
        "severity": 2
    }, headers=headers)
    assert create_resp.status_code == 201
    fault_id = create_resp.json()["id"]

    # delete it
    del_resp = client.delete(f"/api/faults/{fault_id}", headers=headers)
    assert del_resp.status_code == 204

    # verify it's gone
    get_resp = client.get(f"/api/faults/{fault_id}", headers=headers)
    assert get_resp.status_code == 404


def test_recent_activity_returns_ordered_faults():
    """GET /api/recent-activity returns faults ordered by most recent first."""
    headers = get_headers()

    # create first fault
    resp1 = client.post("/api/faults", json={
        "title": "First fault",
        "location": "Lab",
        "severity": 1
    }, headers=headers)
    assert resp1.status_code == 201
    id1 = resp1.json()["id"]

    # tiny delay so timestamps differ
    time.sleep(0.1)

    # create second fault (this is the newer one)
    resp2 = client.post("/api/faults", json={
        "title": "Second fault",
        "location": "Workshop",
        "severity": 3
    }, headers=headers)
    assert resp2.status_code == 201
    id2 = resp2.json()["id"]

    # fetch recent activity
    act_resp = client.get("/api/recent-activity", headers=headers)
    assert act_resp.status_code == 200
    activities = act_resp.json()
    assert isinstance(activities, list)
    assert len(activities) >= 2

    # the first item should be the most recent fault (id2)
    assert activities[0]["id"] == id2


def test_recent_activity_requires_auth():
    """GET /api/recent-activity without token returns 401/403."""
    resp = client.get("/api/recent-activity")
    assert resp.status_code in (401, 403)
    body = resp.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "http_error"


def test_dashboard_page_loads():
    """GET /dashboard returns 200 (public page, login handled by JS)."""
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert "Supervisor Dashboard" in resp.text
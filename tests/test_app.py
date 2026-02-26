"""Tests for the playground app.

Some of these tests INTENTIONALLY FAIL against the current code.
The agency's job is to fix the bugs so all tests pass.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ===================== Health Endpoint =====================


class TestHealth:
    def test_health_returns_200(self):
        """BUG #1: Currently returns 418 instead of 200."""
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_body(self):
        resp = client.get("/health")
        assert resp.json()["status"] == "ok"


# ===================== Create User =====================


class TestCreateUser:
    def test_create_user_with_valid_data(self):
        resp = client.post("/users", json={"name": "Dave", "email": "dave@test.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Dave"
        assert data["email"] == "dave@test.com"
        assert "id" in data

    def test_create_user_missing_email_returns_422(self):
        """BUG #2: Currently crashes with 500 instead of returning 422."""
        resp = client.post("/users", json={"name": "NoEmail"})
        assert resp.status_code == 422

    def test_create_user_missing_name_returns_422(self):
        """BUG #2: Currently crashes with 500 instead of returning 422."""
        resp = client.post("/users", json={"email": "no-name@test.com"})
        assert resp.status_code == 422

    def test_create_user_empty_body_returns_422(self):
        """BUG #2: Currently crashes with 500 instead of returning 422."""
        resp = client.post("/users", json={})
        assert resp.status_code == 422


# ===================== Get User =====================


class TestGetUser:
    def test_get_existing_user(self):
        """BUG #3: Off-by-one means GET /users/1 returns 404 instead of Alice."""
        resp = client.get("/users/1")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alice"

    def test_get_user_2_is_bob(self):
        """BUG #3: Off-by-one means GET /users/2 returns Alice instead of Bob."""
        resp = client.get("/users/2")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Bob"

    def test_get_nonexistent_user(self):
        resp = client.get("/users/9999")
        assert resp.status_code == 404


# ===================== Delete User =====================


class TestDeleteUser:
    def test_delete_existing_user(self):
        """FEATURE #1: DELETE endpoint exists."""
        # First create a user to delete
        create_resp = client.post(
            "/users", json={"name": "ToDelete", "email": "del@test.com"}
        )
        user_id = create_resp.json()["id"]

        resp = client.delete(f"/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["deleted"] is True
        assert resp.json()["id"] == user_id

    def test_delete_nonexistent_user(self):
        """FEATURE #1: DELETE endpoint exists."""
        resp = client.delete("/users/9999")
        assert resp.status_code == 404

    def test_delete_then_get_returns_404(self):
        """FEATURE #1: After deletion, GET should return 404."""
        create_resp = client.post(
            "/users", json={"name": "DeleteMe", "email": "dm@test.com"}
        )
        user_id = create_resp.json()["id"]

        client.delete(f"/users/{user_id}")
        get_resp = client.get(f"/users/{user_id}")
        assert get_resp.status_code == 404

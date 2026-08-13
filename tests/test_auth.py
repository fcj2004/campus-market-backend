"""Authentication endpoint tests."""


def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={"username": "carol", "password": "secret123", "nickname": "Carol"},
    )
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["username"] == "carol"
    assert "password_hash" not in data


def test_register_duplicate_username(client, auth_headers):
    response = client.post(
        "/api/auth/register",
        json={"username": "alice", "password": "secret123"},
    )
    assert response.status_code == 409
    assert response.get_json()["code"] == 409


def test_login_success(client, auth_headers):
    response = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["token"]
    assert data["user"]["username"] == "alice"


def test_login_wrong_password(client, auth_headers):
    response = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_admin_login_success(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["username"] == "admin"


def test_admin_login_invalid_password(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_auth_me_with_valid_token(client, admin_token):
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "admin"
    assert user_data["role"] == "admin"


def test_auth_me_missing_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_non_staff_forbidden_from_admin_actions(client):
    login_resp = client.post("/api/auth/login", json={"username": "student1", "password": "student123"})
    student_token = login_resp.json()["access_token"]

    response = client.post(
        "/api/menu",
        json={"name": "Unauthorized Item", "price": 50.0, "category": "Snacks"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403
    assert "staff privileges required" in response.json()["detail"].lower()

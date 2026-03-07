def test_login(client):
    response = client.post(
        "/api/auth/login/json",
        json={"email": "admin@intervux.ai", "password": "admin123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

from datetime import timedelta

from app.core.security import create_access_token, verify_password


def login(client, password="Clave-segura-123"):
    return client.post(
        "/auth/login",
        json={"email": "admin@refugio.com", "password": password},
    )


def test_login_redirects_to_protected_dashboard(client):
    response = login(client)

    assert response.status_code == 200
    assert response.json()["redirect_to"] == "/dashboard"
    assert "httponly" in response.headers["set-cookie"].lower()

    dashboard = client.get(response.json()["redirect_to"])
    assert dashboard.status_code == 200
    assert "admin@refugio.com" in dashboard.text


def test_new_login_invalidates_previous_token(client):
    first_token = login(client).json()["access_token"]
    second_token = login(client).json()["access_token"]

    old_session = client.get(
        "/dashboard",
        headers={"Authorization": f"Bearer {first_token}"},
    )
    new_session = client.get(
        "/dashboard",
        headers={"Authorization": f"Bearer {second_token}"},
    )

    assert old_session.status_code == 401
    assert new_session.status_code == 200


def test_logout_revokes_session_and_clears_cookie(client):
    assert login(client).status_code == 200

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert client.get("/dashboard").status_code == 401


def test_expired_token_is_rejected(client):
    expired_token = create_access_token(
        {
            "sub": "admin@refugio.com",
            "user_id": 1,
            "jti": "expired-session",
        },
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/dashboard",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401


def test_invalid_inputs_and_credentials_are_rejected(client):
    invalid_email = client.post(
        "/auth/login",
        json={"email": "' OR 1=1 --", "password": "anything"},
    )
    oversized_password = client.post(
        "/auth/login",
        json={"email": "admin@refugio.com", "password": "🙂" * 19},
    )
    invalid_password = login(client, password="incorrecta")

    assert invalid_email.status_code == 422
    assert "OR 1=1" not in invalid_email.text
    assert oversized_password.status_code == 422
    assert "🙂" not in oversized_password.text
    assert invalid_password.status_code == 401
    assert invalid_password.json()["detail"] == "Correo o contraseña incorrectos"


def test_corrupted_password_hash_is_treated_as_invalid_credentials():
    assert verify_password("any-password", "not-a-bcrypt-hash") is False
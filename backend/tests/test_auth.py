from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from app.auth.models import SesionActiva
from app.auth.router import require_cajero, require_mesero
from app.core.security import create_access_token, decode_access_token, verify_password
from app.usuarios.models import Usuario


def login(client, password="Clave-segura-123"):
    return client.post(
        "/auth/login",
        json={"identificacion": "0000000000", "password": password},
    )


def test_login_redirects_to_protected_dashboard(client):
    response = login(client)

    assert response.status_code == 200
    assert response.json()["redirect_to"] == "/dashboard"
    assert "httponly" in response.headers["set-cookie"].lower()

    current_user = client.get("/auth/me")
    assert current_user.status_code == 200
    assert current_user.json()["identificacion"] == "0000000000"


def test_admin_session_exposes_roles_and_all_sites_to_react(client):
    assert login(client).status_code == 200

    current_user = client.get("/auth/me")

    assert current_user.status_code == 200
    assert current_user.json()["is_admin"] is True
    assert set(current_user.json()["roles"]) == {"admin", "mesero", "cajero"}
    assert current_user.json()["sedes_ids"]


def test_admin_always_receives_mesero_and_cajero_jwt_roles(client, db_engine):
    testing_session = sessionmaker(autoflush=False, bind=db_engine)
    with testing_session() as db:
        admin = db.query(Usuario).filter_by(identificacion="0000000000").one()
        admin.es_mesero = False
        admin.es_cajero = False
        db.commit()
        assert require_mesero(admin) is admin
        assert require_cajero(admin) is admin

    response = login(client)
    roles = decode_access_token(response.json()["access_token"])["roles"]

    assert response.status_code == 200
    assert set(roles) == {"admin", "mesero", "cajero"}


def test_new_login_invalidates_previous_token(client):
    first_token = login(client).json()["access_token"]
    second_token = login(client).json()["access_token"]

    old_session = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {first_token}"},
    )
    new_session = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {second_token}"},
    )

    assert old_session.status_code == 401
    assert new_session.status_code == 200


def test_logout_revokes_session_and_clears_cookie(client):
    assert login(client).status_code == 200

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert client.get("/auth/me").status_code == 401


def test_expired_token_is_rejected(client):
    expired_token = create_access_token(
        {
            "sub": "0000000000",
            "user_id": 1,
            "jti": "expired-session",
        },
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401


def test_invalid_inputs_and_credentials_are_rejected(client):
    invalid_identification = client.post(
        "/auth/login",
        json={"identificacion": "' OR 1=1 --", "password": "anything"},
    )
    oversized_password = client.post(
        "/auth/login",
        json={"identificacion": "0000000000", "password": "🙂" * 19},
    )
    invalid_password = login(client, password="incorrecta")

    assert invalid_identification.status_code == 401
    assert "OR 1=1" not in invalid_identification.text
    assert oversized_password.status_code == 422
    assert "🙂" not in oversized_password.text
    assert invalid_password.status_code == 401
    assert invalid_password.json()["detail"] == "Identificación o contraseña incorrectas"
    assert invalid_identification.json()["detail"] == invalid_password.json()["detail"]


def test_corrupted_password_hash_is_treated_as_invalid_credentials():
    assert verify_password("any-password", "not-a-bcrypt-hash") is False


def test_activity_ping_succeeds_for_authenticated_session(client):
    assert login(client).status_code == 200

    response = client.post("/auth/ping")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_inactivity_expires_session_on_backend(client, db_engine):
    assert login(client).status_code == 200
    testing_session = sessionmaker(autoflush=False, bind=db_engine)
    with testing_session() as db:
        active_session = db.query(SesionActiva).one()
        active_session.ultima_actividad = datetime.now(timezone.utc) - timedelta(minutes=4)
        db.commit()

    response = client.post("/auth/ping")

    assert response.status_code == 401
    assert response.json()["detail"] == "Sesión cerrada por inactividad"


def test_maximum_session_duration_expires_despite_activity(client, db_engine):
    assert login(client).status_code == 200
    testing_session = sessionmaker(autoflush=False, bind=db_engine)
    with testing_session() as db:
        active_session = db.query(SesionActiva).one()
        active_session.creada_en = datetime.now(timezone.utc) - timedelta(minutes=31)
        active_session.ultima_actividad = datetime.now(timezone.utc)
        db.commit()

    response = client.post("/auth/ping")

    assert response.status_code == 401
    assert response.json()["detail"] == "Sesión expirada"
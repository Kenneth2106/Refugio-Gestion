"""
Tests HU-01 · HU-02 · HU-03 · HU-06 · HU-34 · HU-36 · HU-37
Autenticación: login, sesión única, inactividad, logout, JWT, seguridad.
"""
from datetime import timedelta

import pytest

from app.core.security import create_access_token, decode_access_token, verify_password
from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD, login_admin, auth_headers


# ──────────────────────────────────────────────────────────────────────────────
# HU-01 · Inicio de sesión
# ──────────────────────────────────────────────────────────────────────────────

def test_hu01_login_exitoso_redirige_a_dashboard(client):
    """HU-01: Login correcto devuelve token, cookie httponly y redirect_to=/dashboard."""
    resp = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["redirect_to"] == "/dashboard"
    assert "httponly" in resp.headers["set-cookie"].lower()


def test_hu01_dashboard_visible_tras_login(client):
    """HU-01: El dashboard es accesible una vez autenticado."""
    token = login_admin(client)["access_token"]
    resp = client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert ADMIN_EMAIL in resp.text


def test_hu01_credenciales_incorrectas_retornan_401(client):
    """HU-01: Credenciales incorrectas no permiten acceso."""
    resp = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": "contraseña-mal"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Correo o contraseña incorrectos"


def test_hu01_usuario_inactivo_no_puede_entrar(client, db_engine):
    """HU-01: Un usuario inactivo (estado=False) recibe 403."""
    from sqlalchemy.orm import sessionmaker
    from app.usuarios.models import Usuario

    Session = sessionmaker(bind=db_engine)
    with Session() as db:
        user = db.query(Usuario).filter_by(email=ADMIN_EMAIL).first()
        user.estado = False
        db.commit()

    resp = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Usuario inactivado"


# ──────────────────────────────────────────────────────────────────────────────
# HU-03 · Sesión única simultánea
# ──────────────────────────────────────────────────────────────────────────────

def test_hu03_nuevo_login_invalida_sesion_anterior(client):
    """HU-03: Al iniciar sesión de nuevo el token anterior queda inválido."""
    first_token = login_admin(client)["access_token"]
    second_token = login_admin(client)["access_token"]

    old = client.get("/dashboard", headers={"Authorization": f"Bearer {first_token}"})
    new = client.get("/dashboard", headers={"Authorization": f"Bearer {second_token}"})

    assert old.status_code == 401
    assert new.status_code == 200


# ──────────────────────────────────────────────────────────────────────────────
# HU-06 · Cierre manual de sesión
# ──────────────────────────────────────────────────────────────────────────────

def test_hu06_logout_revoca_sesion_y_limpia_cookie(client):
    """HU-06: El logout borra la sesión activa y el dashboard ya no es accesible."""
    login_admin(client)
    resp = client.post("/auth/logout")
    assert resp.status_code == 200
    assert client.get("/dashboard").status_code == 401


def test_hu06_logout_sin_sesion_retorna_401(client):
    """HU-06: Logout sin token activo devuelve 401."""
    resp = client.post("/auth/logout")
    assert resp.status_code == 401


# ──────────────────────────────────────────────────────────────────────────────
# HU-34 · JWT y autorización en backend
# ──────────────────────────────────────────────────────────────────────────────

def test_hu34_token_expirado_es_rechazado(client):
    """HU-34: Un token con exp en el pasado es rechazado."""
    login_admin(client)
    expired_token = create_access_token(
        {"sub": ADMIN_EMAIL, "user_id": 1, "jti": "expired-jti"},
        expires_delta=timedelta(seconds=-1),
    )
    resp = client.get("/dashboard", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401


def test_hu34_jwt_contiene_expiracion_en_pagina(client):
    """HU-34: El dashboard expone la expiración del JWT para el temporizador JS."""
    token = login_admin(client)["access_token"]
    expires_at = decode_access_token(token)["exp"]
    resp = client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert f"const sessionExpiresAt = {expires_at} * 1000;" in resp.text


def test_hu34_sin_token_dashboard_retorna_401(client):
    """HU-34: Sin autenticación el dashboard devuelve 401."""
    resp = client.get("/dashboard")
    assert resp.status_code == 401


# ──────────────────────────────────────────────────────────────────────────────
# HU-36 · Protección de credenciales y errores
# ──────────────────────────────────────────────────────────────────────────────

def test_hu36_hash_invalido_tratado_como_credencial_incorrecta():
    """HU-36: Un hash corrupto no causa error, devuelve False."""
    assert verify_password("cualquier-clave", "no-es-bcrypt") is False


def test_hu36_error_login_es_generico(client):
    """HU-36: El mensaje de error no revela si el email existe."""
    resp = client.post(
        "/auth/login",
        json={"email": "noexiste@refugio.com", "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Correo o contraseña incorrectos"


# ──────────────────────────────────────────────────────────────────────────────
# HU-37 · Validación de entradas e inyección
# ──────────────────────────────────────────────────────────────────────────────

def test_hu37_email_invalido_retorna_422(client):
    """HU-37: Un email con intento de inyección SQL es rechazado con 422."""
    resp = client.post(
        "/auth/login",
        json={"email": "' OR 1=1 --", "password": "anything"},
    )
    assert resp.status_code == 422
    assert "OR 1=1" not in resp.text


def test_hu37_password_demasiado_largo_retorna_422(client):
    """HU-37: Contraseña > 72 bytes (bcrypt límite) retorna 422 sin exponer la clave."""
    resp = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": "🙂" * 19},
    )
    assert resp.status_code == 422
    assert "🙂" not in resp.text


def test_hu37_campos_extra_son_rechazados(client):
    """HU-37: Campos no definidos en el schema son rechazados (extra='forbid')."""
    resp = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "hack": "extra"},
    )
    assert resp.status_code == 422


# ──────────────────────────────────────────────────────────────────────────────
# HU-02 · Cierre automático por inactividad (backend)
# ──────────────────────────────────────────────────────────────────────────────

def test_hu02_sesion_invalida_tras_inactividad(client, db_engine):
    """HU-02: Si ultima_actividad supera 3 min, el backend rechaza con 401."""
    from datetime import datetime, timezone
    from sqlalchemy.orm import sessionmaker
    from app.auth.models import SesionActiva

    login_admin(client)

    # Retroceder ultima_actividad artificialmente 4 minutos en la BD
    Session = sessionmaker(bind=db_engine)
    with Session() as db:
        sesion = db.query(SesionActiva).first()
        sesion.ultima_actividad = datetime.now(timezone.utc) - timedelta(minutes=4)
        db.commit()

    resp = client.get("/dashboard")
    assert resp.status_code == 401
    assert "inactividad" in resp.json()["detail"].lower()


def test_hu02_sesion_invalida_tras_maximo_30_min(client, db_engine):
    """HU-02: Si la sesión supera 30 min desde creada_en, el backend la invalida."""
    from datetime import datetime, timezone
    from sqlalchemy.orm import sessionmaker
    from app.auth.models import SesionActiva

    login_admin(client)

    Session = sessionmaker(bind=db_engine)
    with Session() as db:
        sesion = db.query(SesionActiva).first()
        sesion.creada_en = datetime.now(timezone.utc) - timedelta(minutes=31)
        sesion.ultima_actividad = datetime.now(timezone.utc)  # activo, pero sesión vieja
        db.commit()

    resp = client.get("/dashboard")
    assert resp.status_code == 401
    assert "expir" in resp.json()["detail"].lower()


def test_hu02_ping_renueva_ultima_actividad(client, db_engine):
    """HU-02: El endpoint /auth/ping renueva ultima_actividad mientras el usuario está activo."""
    from datetime import datetime, timezone, timedelta
    from sqlalchemy.orm import sessionmaker
    from app.auth.models import SesionActiva

    login_admin(client)

    Session = sessionmaker(bind=db_engine)
    with Session() as db:
        sesion = db.query(SesionActiva).first()
        antes = sesion.ultima_actividad

    resp = client.post("/auth/ping")
    assert resp.status_code == 200

    with Session() as db:
        sesion = db.query(SesionActiva).first()
        despues = sesion.ultima_actividad

    assert despues >= antes
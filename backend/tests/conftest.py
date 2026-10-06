import os

# Vars de entorno ANTES de importar cualquier módulo de la app
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-only-secret-key-with-at-least-32-bytes"
os.environ["SESSION_INACTIVITY_MINUTES"] = "3"
os.environ["SESSION_MAX_MINUTES"] = "30"
os.environ["COOKIE_SECURE"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.usuarios.models import Usuario, UsuarioSede
from app.sedes.models import Sede


ADMIN_EMAIL = "admin@refugio.com"
ADMIN_PASSWORD = "Clave-segura-123"


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(db_engine):
    testing_session = sessionmaker(autoflush=False, bind=db_engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with testing_session() as db:
        admin = Usuario(
            identificacion="0000000000",
            nombre="Administrador Sistema",
            nombre_usuario="admin",
            email=ADMIN_EMAIL,
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            estado=True,
            es_admin=True,
            es_mesero=True,
            es_cajero=True,
        )
        db.add(admin)
        db.flush()
        db.add(
            Sede(
                codigo="BASE",
                nombre="Base Test Site",
                direccion="1 Test Street",
                estado=True,
            )
        )
        db.commit()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def login_admin(client) -> dict:
    """Helper: autentica al admin y devuelve el JSON de respuesta."""
    resp = client.post(
        "/auth/login",
        json={"identificacion": "0000000000", "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def auth_headers(client) -> dict:
    """Devuelve cabecera Authorization con el token del admin."""
    return {"Authorization": f"Bearer {login_admin(client)['access_token']}"}
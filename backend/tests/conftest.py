import os
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema


BACKEND_DIR = Path(__file__).resolve().parents[1]
environment = dotenv_values(BACKEND_DIR / ".env")
configured_database_url = os.environ.get("TEST_DATABASE_URL") or environment.get(
    "DATABASE_URL"
)
if not configured_database_url:
    raise RuntimeError("Configura TEST_DATABASE_URL o DATABASE_URL para las pruebas")

base_url = make_url(configured_database_url)
if not base_url.drivername.startswith("postgresql"):
    raise RuntimeError("Las pruebas requieren una base de datos PostgreSQL")

os.environ["DATABASE_URL"] = configured_database_url
os.environ["SECRET_KEY"] = "test-only-secret-key-with-at-least-32-bytes"
os.environ["SESSION_INACTIVITY_MINUTES"] = "3"
os.environ["SESSION_MAX_MINUTES"] = "30"
os.environ["COOKIE_SECURE"] = "false"

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.security import get_password_hash
from app.main import app
from app.sedes.models import Sede
from app.usuarios.models import Usuario


ADMIN_EMAIL = "admin@refugio.com"
ADMIN_PASSWORD = "Clave-segura-123"


@pytest.fixture
def db_engine():
    schema = f"test_refugio_{uuid4().hex}"
    admin_engine = create_engine(base_url, pool_pre_ping=True)
    with admin_engine.begin() as connection:
        connection.execute(CreateSchema(schema))
    engine = None
    try:
        test_url = base_url.set(
            query={**base_url.query, "options": f"-csearch_path={schema}"}
        )
        engine = create_engine(test_url, pool_pre_ping=True)
        alembic_config = Config(str(BACKEND_DIR / "alembic.ini"))
        with engine.begin() as connection:
            alembic_config.attributes["connection"] = connection
            command.upgrade(alembic_config, "head")
        yield engine
    finally:
        if engine is not None:
            engine.dispose()
        with admin_engine.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        admin_engine.dispose()


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
    response = client.post(
        "/auth/login",
        json={"identificacion": "0000000000", "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return response.json()


def auth_headers(client) -> dict:
    return {"Authorization": f"Bearer {login_admin(client)['access_token']}"}

"""
Tests HU-05 · HU-10 · HU-35
Sedes y Mesas: registro, validación de campos, inactivación, parametrización.
"""
import pytest

from tests.conftest import login_admin, auth_headers


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def crear_sede(client, codigo="S001", nombre="Sede Norte"):
    return client.post(
        "/sedes/",
        json={"codigo": codigo, "nombre": nombre},
        headers=auth_headers(client),
    )


# ──────────────────────────────────────────────────────────────────────────────
# HU-10 · Registro de nueva sede
# ──────────────────────────────────────────────────────────────────────────────

def test_hu10_crear_sede_exitosa(client):
    """HU-10: El admin puede registrar una sede con código único."""
    resp = crear_sede(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["codigo"] == "S001"
    assert data["nombre"] == "Sede Norte"
    assert data["estado"] is True


def test_hu10_codigo_sede_duplicado_retorna_400(client):
    """HU-10: Dos sedes con el mismo código no están permitidas."""
    crear_sede(client, codigo="S001")
    resp = crear_sede(client, codigo="S001")
    assert resp.status_code == 400
    assert "código" in resp.json()["detail"].lower()


def test_hu10_listar_sedes_retorna_todas(client):
    """HU-10: El admin obtiene la lista completa de sedes."""
    crear_sede(client, codigo="S001")
    crear_sede(client, codigo="S002", nombre="Sede Sur")
    resp = client.get("/sedes/", headers=auth_headers(client))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_hu10_inactivar_sede(client):
    """HU-10: El admin puede inactivar una sede (estado=False)."""
    sede_id = crear_sede(client).json()["id"]
    resp = client.patch(
        f"/sedes/{sede_id}",
        json={"estado": False},
        headers=auth_headers(client),
    )
    assert resp.status_code == 200
    assert resp.json()["estado"] is False


def test_hu10_sede_no_existente_retorna_404(client):
    """HU-10: Actualizar una sede inexistente devuelve 404."""
    resp = client.patch(
        "/sedes/9999",
        json={"nombre": "X"},
        headers=auth_headers(client),
    )
    assert resp.status_code == 404


def test_hu10_sin_autenticacion_retorna_401(client):
    """HU-10: Crear sede sin token es rechazado."""
    resp = client.post("/sedes/", json={"codigo": "S001", "nombre": "N"})
    assert resp.status_code == 401


def test_hu10_sin_ser_admin_retorna_403(client, db_engine):
    """HU-10: Un usuario sin rol admin no puede crear sedes."""
    from sqlalchemy.orm import sessionmaker
    from app.usuarios.models import Usuario
    from app.core.security import get_password_hash

    Session = sessionmaker(bind=db_engine)
    with Session() as db:
        mesero = Usuario(
            identificacion="1111111111",
            nombre="Mesero Prueba",
            email="mesero@refugio.com",
            hashed_password=get_password_hash("Clave-segura-123"),
            estado=True,
            es_admin=False,
            es_mesero=True,
            es_cajero=False,
        )
        db.add(mesero)
        db.commit()

    token = client.post(
        "/auth/login",
        json={"email": "mesero@refugio.com", "password": "Clave-segura-123"},
    ).json()["access_token"]

    resp = client.post(
        "/sedes/",
        json={"codigo": "S001", "nombre": "Sede"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


# ──────────────────────────────────────────────────────────────────────────────
# HU-35 · Parametrización de mesas por sede
# ──────────────────────────────────────────────────────────────────────────────

def test_hu35_crear_mesa_en_sede(client):
    """HU-35: El admin puede registrar una mesa en una sede."""
    sede_id = crear_sede(client).json()["id"]
    resp = client.post(
        f"/sedes/{sede_id}/mesas",
        json={"numero": 1},
        headers=auth_headers(client),
    )
    assert resp.status_code == 201
    assert resp.json()["numero"] == 1
    assert resp.json()["sede_id"] == sede_id


def test_hu35_numero_mesa_duplicado_en_misma_sede_retorna_400(client):
    """HU-35: Dos mesas con el mismo número en la misma sede no están permitidas."""
    sede_id = crear_sede(client).json()["id"]
    client.post(f"/sedes/{sede_id}/mesas", json={"numero": 1}, headers=auth_headers(client))
    resp = client.post(f"/sedes/{sede_id}/mesas", json={"numero": 1}, headers=auth_headers(client))
    assert resp.status_code == 400


def test_hu35_mismo_numero_mesa_en_diferente_sede_es_valido(client):
    """HU-35: El mismo número de mesa en distintas sedes es válido."""
    s1 = crear_sede(client, codigo="S001").json()["id"]
    s2 = crear_sede(client, codigo="S002", nombre="Sede Sur").json()["id"]
    r1 = client.post(f"/sedes/{s1}/mesas", json={"numero": 1}, headers=auth_headers(client))
    r2 = client.post(f"/sedes/{s2}/mesas", json={"numero": 1}, headers=auth_headers(client))
    assert r1.status_code == 201
    assert r2.status_code == 201


def test_hu35_inactivar_mesa(client):
    """HU-35: El admin puede inactivar una mesa sin borrarla físicamente."""
    sede_id = crear_sede(client).json()["id"]
    mesa_id = client.post(
        f"/sedes/{sede_id}/mesas", json={"numero": 1}, headers=auth_headers(client)
    ).json()["id"]

    resp = client.patch(
        f"/sedes/mesas/{mesa_id}",
        json={"estado": False},
        headers=auth_headers(client),
    )
    assert resp.status_code == 200
    assert resp.json()["estado"] is False


def test_hu35_listar_mesas_de_sede(client):
    """HU-35: El admin puede listar las mesas de una sede."""
    sede_id = crear_sede(client).json()["id"]
    client.post(f"/sedes/{sede_id}/mesas", json={"numero": 1}, headers=auth_headers(client))
    client.post(f"/sedes/{sede_id}/mesas", json={"numero": 2}, headers=auth_headers(client))

    resp = client.get(f"/sedes/{sede_id}/mesas", headers=auth_headers(client))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_hu35_sede_inexistente_retorna_404(client):
    """HU-35: Crear mesa en sede inexistente devuelve 404."""
    resp = client.post(
        "/sedes/9999/mesas",
        json={"numero": 1},
        headers=auth_headers(client),
    )
    assert resp.status_code == 404


# ──────────────────────────────────────────────────────────────────────────────
# HU-05 · Validación de campos en sedes/mesas
# ──────────────────────────────────────────────────────────────────────────────

def test_hu05_sede_sin_codigo_retorna_422(client):
    """HU-05: Crear sede sin campo obligatorio 'codigo' devuelve 422."""
    resp = client.post("/sedes/", json={"nombre": "Sin código"}, headers=auth_headers(client))
    assert resp.status_code == 422


def test_hu05_sede_sin_nombre_retorna_422(client):
    """HU-05: Crear sede sin campo obligatorio 'nombre' devuelve 422."""
    resp = client.post("/sedes/", json={"codigo": "S001"}, headers=auth_headers(client))
    assert resp.status_code == 422


def test_hu05_mesa_sin_numero_retorna_422(client):
    """HU-05: Crear mesa sin campo obligatorio 'numero' devuelve 422."""
    sede_id = crear_sede(client).json()["id"]
    resp = client.post(f"/sedes/{sede_id}/mesas", json={}, headers=auth_headers(client))
    assert resp.status_code == 422


def test_hu05_mesa_numero_negativo_retorna_422(client):
    """HU-05: El número de mesa debe ser positivo (gt=0)."""
    sede_id = crear_sede(client).json()["id"]
    resp = client.post(f"/sedes/{sede_id}/mesas", json={"numero": -1}, headers=auth_headers(client))
    assert resp.status_code == 422

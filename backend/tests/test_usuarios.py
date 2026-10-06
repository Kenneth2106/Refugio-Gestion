"""
Tests HU-04 · HU-05 · HU-07 · HU-08 · HU-09
Usuarios: registro, roles, autorización por sede, edición, inactivación.
"""
import pytest

from tests.conftest import login_admin, auth_headers, ADMIN_EMAIL


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

NUEVO_USUARIO = {
    "identificacion": "9876543210",
    "nombre": "Operador Prueba",
    "nombre_usuario": "operador",
    "email": "operador@refugio.com",
    "password": "Clave-segura-123",
    "es_admin": False,
    "es_mesero": True,
    "es_cajero": False,
    "sedes_ids": [1],
}


def crear_usuario(client, payload=None, headers=None):
    return client.post(
        "/usuarios/",
        json=payload or NUEVO_USUARIO,
        headers=headers or auth_headers(client),
    )


def crear_sede(client, codigo="S001"):
    return client.post(
        "/sedes/",
        json={"codigo": codigo, "nombre": "Sede Prueba", "direccion": "Calle Prueba 1"},
        headers=auth_headers(client),
    ).json()


# ──────────────────────────────────────────────────────────────────────────────
# HU-07 · Registrar usuarios
# ──────────────────────────────────────────────────────────────────────────────

def test_hu07_crear_usuario_exitoso(client):
    """HU-07: El admin puede registrar un nuevo usuario."""
    resp = crear_usuario(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == NUEVO_USUARIO["email"]
    assert data["nombre_usuario"] == NUEVO_USUARIO["nombre_usuario"]
    assert data["estado"] is True
    assert "hashed_password" not in data


def test_hu07_email_duplicado_retorna_400(client):
    """HU-07: No se permiten dos usuarios con el mismo correo."""
    crear_usuario(client)
    resp = crear_usuario(client)
    assert resp.status_code == 400


def test_hu07_identificacion_duplicada_retorna_400(client):
    """HU-07: La identificación debe ser única."""
    crear_usuario(client)
    duplicado = {**NUEVO_USUARIO, "email": "otro@refugio.com"}
    resp = crear_usuario(client, payload=duplicado)
    assert resp.status_code == 400


def test_hu07_nombre_usuario_duplicado_no_distingue_mayusculas(client):
    crear_usuario(client)
    duplicado = {**NUEVO_USUARIO, "identificacion": "1234567890", "email": "otro@refugio.com", "nombre_usuario": "OPERADOR"}
    resp = crear_usuario(client, payload=duplicado)
    assert resp.status_code == 400


def test_hu07_sin_rol_retorna_422(client):
    """HU-07: Un usuario sin ningún rol asignado es rechazado."""
    payload = {**NUEVO_USUARIO, "es_admin": False, "es_mesero": False, "es_cajero": False}
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 422
    assert "rol" in resp.json()["detail"].lower()


def test_hu07_admin_puede_crearse_sin_sede(client):
    payload = {
        **NUEVO_USUARIO,
        "identificacion": "2222222222",
        "nombre_usuario": "admin-sin-sede",
        "email": "admin-sin-sede@example.com",
        "es_admin": True,
        "es_mesero": False,
        "es_cajero": False,
        "sedes_ids": [],
    }

    response = crear_usuario(client, payload=payload)

    assert response.status_code == 201
    assert response.json()["sedes_ids"] == []


def test_hu07_admin_con_sede_retorna_422(client):
    """HU-07: El administrador no debe tener sedes asignadas."""
    sede = crear_sede(client)
    payload = {
        **NUEVO_USUARIO,
        "identificacion": "3333333333",
        "nombre_usuario": "admin-con-sede",
        "email": "admin-con-sede@example.com",
        "es_admin": True,
        "sedes_ids": [sede["id"]],
    }
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 422
    assert "administrador no debe tener sedes asignadas" in resp.json()["detail"].lower()


def test_hu07_usuario_operativo_sin_sede_retorna_422(client):
    payload = {**NUEVO_USUARIO, "sedes_ids": []}

    response = crear_usuario(client, payload=payload)

    assert response.status_code == 422
    assert "sede" in response.json()["detail"].lower()


def test_hu07_con_sede_valida_asigna_sede(client):
    """HU-07: Crear usuario con sedes_ids válidas las asocia correctamente."""
    sede = crear_sede(client)
    payload = {**NUEVO_USUARIO, "sedes_ids": [sede["id"]]}
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 201
    assert sede["id"] in resp.json()["sedes_ids"]


def test_hu07_con_sede_inexistente_retorna_404(client):
    """HU-07: Asignar una sede que no existe retorna 404."""
    payload = {**NUEVO_USUARIO, "sedes_ids": [9999]}
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 404


def test_hu07_sin_ser_admin_retorna_403(client, db_engine):
    """HU-07: Un usuario no-admin no puede registrar usuarios."""
    from sqlalchemy.orm import sessionmaker
    from app.usuarios.models import Usuario, UsuarioSede
    from app.sedes.models import Sede
    from app.core.security import get_password_hash

    Session = sessionmaker(bind=db_engine)
    with Session() as db:
        mesero = Usuario(
            identificacion="1111111111",
            nombre="Mesero",
            nombre_usuario="mesero",
            email="mesero@refugio.com",
            hashed_password=get_password_hash("Clave-segura-123"),
            estado=True,
            es_admin=False,
            es_mesero=True,
            es_cajero=False,
        )
        db.add(mesero)
        db.flush()
        base_site = db.query(Sede).filter_by(codigo="BASE").one()
        db.add(UsuarioSede(usuario_id=mesero.id, sede_id=base_site.id))
        db.commit()

    token = client.post(
        "/auth/login",
        json={"identificacion": "1111111111", "password": "Clave-segura-123"},
    ).json()["access_token"]

    resp = crear_usuario(client, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


# ──────────────────────────────────────────────────────────────────────────────
# HU-08 · Editar e inactivar usuarios
# ──────────────────────────────────────────────────────────────────────────────

def test_hu08_editar_nombre_usuario(client):
    """HU-08: El admin puede actualizar el nombre de un usuario."""
    uid = crear_usuario(client).json()["id"]
    resp = client.patch(
        f"/usuarios/{uid}",
        json={"nombre": "Nuevo Nombre"},
        headers=auth_headers(client),
    )
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Nuevo Nombre"


def test_hu08_inactivar_usuario(client):
    """HU-08: El admin puede inactivar un usuario; queda en BD con estado=False."""
    uid = crear_usuario(client).json()["id"]
    resp = client.patch(f"/usuarios/{uid}/inactivar", headers=auth_headers(client))
    assert resp.status_code == 200
    assert resp.json()["estado"] is False


def test_hu08_reactivar_usuario(client):
    uid = crear_usuario(client).json()["id"]
    client.patch(f"/usuarios/{uid}/inactivar", headers=auth_headers(client))

    response = client.patch(
        f"/usuarios/{uid}",
        json={"estado": True},
        headers=auth_headers(client),
    )

    assert response.status_code == 200
    assert response.json()["estado"] is True


def test_hu08_usuario_inactivo_no_puede_autenticarse(client, db_engine):
    """HU-08: Un usuario inactivado no puede hacer login."""
    uid = crear_usuario(client).json()["id"]
    token = client.post(
        "/auth/login",
        json={"identificacion": NUEVO_USUARIO["identificacion"], "password": NUEVO_USUARIO["password"]},
    ).json()["access_token"]
    client.patch(f"/usuarios/{uid}/inactivar", headers=auth_headers(client))

    revoked = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert revoked.status_code == 403
    from sqlalchemy.orm import sessionmaker
    from app.auth.models import SesionActiva
    with sessionmaker(bind=db_engine)() as db:
        revoked_session = db.query(SesionActiva).filter_by(usuario_id=uid).one()
        assert revoked_session.activa is False
        assert revoked_session.revocada_en is not None

    resp = client.post(
        "/auth/login",
        json={"identificacion": NUEVO_USUARIO["identificacion"], "password": NUEVO_USUARIO["password"]},
    )
    assert resp.status_code == 403


def test_hu36_password_persisted_as_bcrypt_hash(client, db_engine):
    from sqlalchemy.orm import sessionmaker
    from app.core.security import verify_password
    from app.usuarios.models import Usuario

    created = crear_usuario(client)
    assert created.status_code == 201
    with sessionmaker(bind=db_engine)() as db:
        usuario = db.query(Usuario).filter_by(id=created.json()["id"]).one()
        assert usuario.hashed_password.startswith("$2")
        assert usuario.hashed_password != NUEVO_USUARIO["password"]
        assert verify_password(NUEVO_USUARIO["password"], usuario.hashed_password)


def test_hu08_role_and_site_edits_apply_on_existing_session(client):
    site_b = crear_sede(client, codigo="S002")
    user_payload = {
        **NUEVO_USUARIO,
        "identificacion": "1234432112",
        "nombre_usuario": "usuario-dinamico",
        "email": "usuario-dinamico@refugio.com",
        "sedes_ids": [1],
    }
    user = crear_usuario(client, payload=user_payload).json()
    token = client.post(
        "/auth/login",
        json={
            "identificacion": user_payload["identificacion"],
            "password": user_payload["password"],
        },
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    before = client.get("/sedes/1/mesas", headers=headers)
    changed = client.patch(
        f"/usuarios/{user['id']}",
        json={
            "sedes_ids": [site_b["id"]],
            "es_mesero": False,
            "es_cajero": True,
        },
        headers=auth_headers(client),
    )
    after = client.get("/sedes/1/mesas", headers=headers)

    assert before.status_code == 200
    assert changed.status_code == 200
    assert after.status_code == 403


def test_hu08_admin_no_puede_inactivarse_a_si_mismo(client, db_engine):
    """HU-08: El admin no puede inactivar su propia cuenta."""
    from sqlalchemy.orm import sessionmaker
    from app.usuarios.models import Usuario

    Session = sessionmaker(bind=db_engine)
    with Session() as db:
        admin = db.query(Usuario).filter_by(email=ADMIN_EMAIL).first()
        admin_id = admin.id

    resp = client.patch(f"/usuarios/{admin_id}/inactivar", headers=auth_headers(client))
    assert resp.status_code == 400


def test_hu08_usuario_inexistente_retorna_404(client):
    """HU-08: Editar un usuario que no existe devuelve 404."""
    resp = client.patch("/usuarios/9999", json={"nombre": "X"}, headers=auth_headers(client))
    assert resp.status_code == 404


def test_hu08_actualizar_admin_con_sedes_retorna_422(client):
    """HU-08: No se pueden asignar sedes a un administrador."""
    sede = crear_sede(client)
    payload = {
        **NUEVO_USUARIO,
        "identificacion": "4444444444",
        "nombre_usuario": "admin-update-test",
        "email": "admin-update@example.com",
        "es_admin": True,
        "sedes_ids": [],
    }
    uid = crear_usuario(client, payload=payload).json()["id"]
    resp = client.patch(
        f"/usuarios/{uid}",
        json={"sedes_ids": [sede["id"]]},
        headers=auth_headers(client),
    )
    assert resp.status_code == 422
    assert "administrador no debe tener sedes asignadas" in resp.json()["detail"].lower()


# ──────────────────────────────────────────────────────────────────────────────
# HU-09 · Roles adicionales
# ──────────────────────────────────────────────────────────────────────────────

def test_hu09_usuario_con_multiples_roles(client):
    """HU-09: El admin puede asignar combinación Admin+Mesero+Cajero."""
    payload = {**NUEVO_USUARIO, "es_admin": True, "es_mesero": True, "es_cajero": True, "sedes_ids": []}
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["es_admin"] is True
    assert data["es_mesero"] is True
    assert data["es_cajero"] is True


def test_hu09_roles_adicionales_son_solo_para_administrador(client):
    non_admin = crear_usuario(
        client,
        payload={
            **NUEVO_USUARIO,
            "identificacion": "9999911111",
            "nombre_usuario": "mesero-cajero",
            "email": "mesero-cajero@refugio.com",
            "es_mesero": True,
            "es_cajero": True,
            "sedes_ids": [1],
        },
    )
    admin = crear_usuario(
        client,
        payload={
            **NUEVO_USUARIO,
            "identificacion": "9999922222",
            "nombre_usuario": "admin-capacidades",
            "email": "admin-capacidades@refugio.com",
            "es_admin": True,
            "es_mesero": False,
            "es_cajero": False,
            "sedes_ids": [],
        },
    )

    assert non_admin.status_code == 422
    assert admin.status_code == 201
    assert admin.json()["es_mesero"] is True
    assert admin.json()["es_cajero"] is True


def test_hu09_cambiar_roles_usuario(client):
    """HU-09: El admin puede modificar los roles de un usuario existente."""
    uid = crear_usuario(client).json()["id"]  # mesero
    resp = client.patch(
        f"/usuarios/{uid}",
        json={"es_mesero": False, "es_cajero": True},
        headers=auth_headers(client),
    )
    assert resp.status_code == 200
    assert resp.json()["es_cajero"] is True
    assert resp.json()["es_mesero"] is False


def test_hu09_quitar_todos_los_roles_retorna_422(client):
    """HU-09: No se puede dejar a un usuario sin ningún rol."""
    uid = crear_usuario(client).json()["id"]  # mesero
    resp = client.patch(
        f"/usuarios/{uid}",
        json={"es_mesero": False},
        headers=auth_headers(client),
    )
    assert resp.status_code == 422


# ──────────────────────────────────────────────────────────────────────────────
# HU-04 · Autorización por sede
# ──────────────────────────────────────────────────────────────────────────────

def test_hu04_usuario_solo_ve_sedes_asignadas(client, db_engine):
    """HU-04: Un mesero solo puede ver las sedes a las que está asignado."""
    from sqlalchemy.orm import sessionmaker
    from app.usuarios.models import Usuario, UsuarioSede
    from app.sedes.models import Sede
    from app.core.security import get_password_hash

    headers = auth_headers(client)

    # Crear dos sedes
    s1 = client.post("/sedes/", json={"codigo": "S001", "nombre": "Norte", "direccion": "Calle Norte 1"}, headers=headers).json()
    s2 = client.post("/sedes/", json={"codigo": "S002", "nombre": "Sur", "direccion": "Calle Sur 1"}, headers=headers).json()

    # Crear mesero asignado solo a S1
    payload = {**NUEVO_USUARIO, "sedes_ids": [s1["id"]]}
    crear_usuario(client, payload=payload)

    token = client.post(
        "/auth/login",
        json={"identificacion": NUEVO_USUARIO["identificacion"], "password": NUEVO_USUARIO["password"]},
    ).json()["access_token"]
    mesero_headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/sedes/", headers=mesero_headers)
    assert resp.status_code == 200
    ids = [s["id"] for s in resp.json()]
    assert s1["id"] in ids
    assert s2["id"] not in ids


def test_hu04_mesero_no_accede_a_mesas_de_sede_no_asignada(client):
    """HU-04: Un mesero no puede listar mesas de una sede no autorizada."""
    headers = auth_headers(client)

    # Crear sede y mesa
    s1 = client.post("/sedes/", json={"codigo": "S001", "nombre": "Norte", "direccion": "Calle Norte 1"}, headers=headers).json()
    client.post(f"/sedes/{s1['id']}/mesas", json={"numero": 1}, headers=headers)

    # El mesero tiene la sede base, pero no la sede S001
    payload = {**NUEVO_USUARIO, "sedes_ids": [1]}
    crear_usuario(client, payload=payload)

    token = client.post(
        "/auth/login",
        json={"identificacion": NUEVO_USUARIO["identificacion"], "password": NUEVO_USUARIO["password"]},
    ).json()["access_token"]
    mesero_headers = {"Authorization": f"Bearer {token}"}

    resp = client.get(f"/sedes/{s1['id']}/mesas", headers=mesero_headers)
    assert resp.status_code == 403


# ──────────────────────────────────────────────────────────────────────────────
# HU-05 · Validación de campos en usuarios
# ──────────────────────────────────────────────────────────────────────────────

def test_hu07_usuario_sin_email_es_valido(client):
    """HU-07 no declara el correo como campo obligatorio."""
    payload = {k: v for k, v in NUEVO_USUARIO.items() if k != "email"}
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 201
    assert resp.json()["email"] is None


def test_hu05_usuario_email_invalido_retorna_422(client):
    """HU-05: Un email con formato incorrecto es rechazado."""
    payload = {**NUEVO_USUARIO, "email": "no-es-email"}
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 422


def test_hu05_password_menor_de_8_caracteres_retorna_422(client):
    """HU-05: La contraseña debe tener al menos 8 caracteres."""
    payload = {**NUEVO_USUARIO, "password": "corta"}
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 422


def test_hu05_identificacion_vacia_retorna_422(client):
    """HU-05: La identificación no puede estar vacía."""
    payload = {**NUEVO_USUARIO, "identificacion": ""}
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 422


def test_hu05_nombre_vacio_retorna_422(client):
    """HU-05: El nombre no puede estar vacío."""
    payload = {**NUEVO_USUARIO, "nombre": ""}
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 422


def test_hu05_campos_extra_en_usuario_retorna_422(client):
    """HU-05: Campos no definidos en el schema son rechazados."""
    payload = {**NUEVO_USUARIO, "campo_extra": "valor"}
    resp = crear_usuario(client, payload=payload)
    assert resp.status_code == 422

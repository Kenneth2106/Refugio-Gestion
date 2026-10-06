from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.inventario.models import Inventario
from app.ventas.models import LineaPedido, Pedido
from app.auth.models import SesionActiva
from tests.conftest import auth_headers


def preparar_operacion(client, *, stock=10, product_code="OP-01"):
    admin = auth_headers(client)
    provider = client.post(
        "/proveedores",
        json={"nombre": f"Proveedor {product_code}"},
        headers=admin,
    ).json()
    product = client.post(
        "/productos",
        json={
            "codigo": product_code,
            "nombre": f"Producto {product_code}",
            "precio_venta": "1200.50",
            "precio_compra": "600.25",
            "estado": True,
            "proveedor_id": provider["id"],
        },
        headers=admin,
    ).json()
    table = client.post(
        "/sedes/1/mesas",
        json={"numero": 1},
        headers=admin,
    ).json()
    client.post(
        "/sedes/1/inventario",
        json={"producto_id": product["id"], "cantidad": stock},
        headers=admin,
    )
    user = client.post(
        "/usuarios/",
        json={
            "identificacion": "8877665544",
            "nombre": "Mesero Operación",
            "nombre_usuario": "mesero-operacion",
            "email": "mesero-operacion@refugio.com",
            "password": "Clave-segura-123",
            "es_admin": False,
            "es_mesero": True,
            "es_cajero": False,
            "sedes_ids": [1],
        },
        headers=admin,
    )
    assert user.status_code == 201
    login = client.post(
        "/auth/login",
        json={
            "identificacion": "8877665544",
            "password": "Clave-segura-123",
        },
    )
    return admin, {"Authorization": f"Bearer {login.json()['access_token']}"}, product, table


def test_hu19_mesero_ve_solo_mesas_de_su_sede(client):
    admin, mesero, _, table_a = preparar_operacion(client)
    site_b = client.post(
        "/sedes/",
        json={"codigo": "SEDE-B", "nombre": "Sede B", "direccion": "Calle B"},
        headers=admin,
    ).json()
    table_b = client.post(
        f"/sedes/{site_b['id']}/mesas",
        json={"numero": 1},
        headers=admin,
    ).json()

    allowed = client.get("/sedes/1/mesas", headers=mesero)
    denied = client.get(f"/sedes/{site_b['id']}/mesas", headers=mesero)

    assert allowed.status_code == 200
    assert [row["id"] for row in allowed.json()] == [table_a["id"]]
    assert allowed.json()[0]["estado_operativo"] == "LIBRE"
    assert denied.status_code == 403
    assert table_b["id"] not in [row["id"] for row in allowed.json()]


def test_hu13_admin_elige_sede_y_se_guarda_en_la_sesion(client, db_engine):
    admin = auth_headers(client)
    site_b = client.post(
        "/sedes/",
        json={"codigo": "SEDE-B", "nombre": "Sede B", "direccion": "Calle B"},
        headers=admin,
    ).json()
    login = client.post(
        "/auth/login",
        json={
            "identificacion": "0000000000",
            "password": "Clave-segura-123",
        },
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    current = client.get("/auth/me", headers=headers)
    no_selection = client.get("/inventario", headers=headers)
    selected = client.post(
        "/auth/sede",
        json={"sede_id": site_b["id"]},
        headers=headers,
    )
    inventory = client.get("/inventario", headers=headers)

    assert current.json()["sede_seleccionada_id"] is None
    assert no_selection.status_code == 409
    assert selected.status_code == 200
    assert inventory.status_code == 200
    with sessionmaker(bind=db_engine)() as db:
        active = db.query(SesionActiva).filter_by(activa=True).one()
        assert active.sede_seleccionada_id == site_b["id"]


def test_hu13_una_sede_autorizada_seleccionada_automaticamente(client):
    admin = auth_headers(client)
    client.post(
        "/usuarios/",
        json={
            "identificacion": "autoselect-user",
            "nombre": "Mesero Autoselect",
            "nombre_usuario": "mesero-autoselect",
            "email": "mesero-autoselect@refugio.com",
            "password": "Clave-segura-123",
            "es_mesero": True,
            "sedes_ids": [1],
        },
        headers=admin,
    )
    login = client.post(
        "/auth/login",
        json={
            "identificacion": "autoselect-user",
            "password": "Clave-segura-123",
        },
    )

    current = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert current.status_code == 200
    assert current.json()["sede_seleccionada_id"] == 1


def test_hu20_mesa_ocupada_muestra_pedido_abierto_existente(client):
    _, mesero, product, table = preparar_operacion(client)
    created = client.post(
        "/pedidos",
        json={
            "mesa_id": table["id"],
            "productos": [{"producto_id": product["id"], "cantidad": 1}],
        },
        headers=mesero,
    )

    selected = client.get(
        f"/mesas/{table['id']}/pedido-abierto",
        headers=mesero,
    )

    assert created.status_code == 201
    assert selected.status_code == 200
    assert selected.json()["id"] == created.json()["id"]


def test_hu21_inventario_es_solo_de_sede_seleccionada(client):
    admin, mesero, product, _ = preparar_operacion(client, stock=6)
    site_b = client.post(
        "/sedes/",
        json={"codigo": "SEDE-B", "nombre": "Sede B", "direccion": "Calle B"},
        headers=admin,
    ).json()
    client.post(
        f"/sedes/{site_b['id']}/inventario",
        json={"producto_id": product["id"], "cantidad": 31},
        headers=admin,
    )

    response = client.get("/inventario", headers=mesero)
    product_row = next(
        row for row in response.json() if row["producto_id"] == product["id"]
    )

    assert response.status_code == 200
    assert product_row["sede_id"] == 1
    assert product_row["cantidad"] == 6
    assert all(row["sede_id"] != site_b["id"] for row in response.json())


def test_hu22_registro_abierto_descuenta_stock_y_guarda_precio_vigente(
    client,
    db_engine,
):
    admin, mesero, product, table = preparar_operacion(client, stock=5)
    order_response = client.post(
        "/pedidos",
        json={
            "mesa_id": table["id"],
            "productos": [{"producto_id": product["id"], "cantidad": 2}],
        },
        headers=mesero,
    )

    assert order_response.status_code == 201
    assert order_response.json()["estado"] == "ABIERTO"
    assert order_response.json()["usuario_id"] > 0
    assert order_response.json()["sede_id"] == 1
    assert order_response.json()["mesa_id"] == table["id"]
    assert order_response.json()["total"] == "2401.00"

    changed_price = client.patch(
        f"/productos/{product['id']}",
        json={"precio_venta": "9900.00"},
        headers=admin,
    )
    detail = client.get(
        f"/pedidos/{order_response.json()['id']}",
        headers=mesero,
    )
    inventory = client.get("/inventario", headers=mesero).json()

    assert changed_price.status_code == 200
    assert detail.json()["productos"][0]["precio_unitario"] == "1200.50"
    assert next(row for row in inventory if row["producto_id"] == product["id"])[
        "cantidad"
    ] == 3
    with sessionmaker(bind=db_engine)() as db:
        line = db.query(LineaPedido).filter_by(pedido_id=detail.json()["id"]).one()
        assert isinstance(line.precio_unitario, Decimal)
        assert line.precio_unitario == Decimal("1200.50")


def test_hu23_agregar_producto_solo_a_pedido_abierto(client, db_engine):
    _, mesero, product, table = preparar_operacion(client, stock=5)
    order = client.post(
        "/pedidos",
        json={
            "mesa_id": table["id"],
            "productos": [{"producto_id": product["id"], "cantidad": 1}],
        },
        headers=mesero,
    ).json()
    added = client.post(
        f"/pedidos/{order['id']}/productos",
        json={"producto_id": product["id"], "cantidad": 2},
        headers=mesero,
    )

    assert added.status_code == 200
    assert len(added.json()["productos"]) == 2
    assert sum(line["cantidad"] for line in added.json()["productos"]) == 3
    with sessionmaker(bind=db_engine)() as db:
        pedido = db.query(Pedido).filter_by(id=order["id"]).one()
        pedido.estado = "CERRADO"
        db.commit()

    rejected = client.post(
        f"/pedidos/{order['id']}/productos",
        json={"producto_id": product["id"], "cantidad": 1},
        headers=mesero,
    )
    assert rejected.status_code == 409


def test_hu24_mesa_esta_ocupada_mientras_pedido_abierto(client):
    _, mesero, product, table = preparar_operacion(client)
    client.post(
        "/pedidos",
        json={
            "mesa_id": table["id"],
            "productos": [{"producto_id": product["id"], "cantidad": 1}],
        },
        headers=mesero,
    )

    response = client.get("/sedes/1/mesas", headers=mesero)

    assert response.status_code == 200
    assert response.json()[0]["estado_operativo"] == "OCUPADA"


def test_hu25_consulta_detalle_total_y_restriccion_por_sede(client):
    admin, mesero, product, table = preparar_operacion(client)
    order = client.post(
        "/pedidos",
        json={
            "mesa_id": table["id"],
            "productos": [{"producto_id": product["id"], "cantidad": 3}],
        },
        headers=mesero,
    ).json()
    other_site = client.post(
        "/sedes/",
        json={"codigo": "SEDE-B", "nombre": "Sede B", "direccion": "Calle B"},
        headers=admin,
    ).json()
    second_user = client.post(
        "/usuarios/",
        json={
            "identificacion": "1122334455",
            "nombre": "Mesero B",
            "nombre_usuario": "mesero-b",
            "email": "mesero-b@refugio.com",
            "password": "Clave-segura-123",
            "es_mesero": True,
            "sedes_ids": [other_site["id"]],
        },
        headers=admin,
    )
    assert second_user.status_code == 201
    second_login = client.post(
        "/auth/login",
        json={
            "identificacion": "1122334455",
            "password": "Clave-segura-123",
        },
    ).json()

    detail = client.get(f"/pedidos/{order['id']}", headers=mesero)
    denied = client.get(
        f"/pedidos/{order['id']}",
        headers={"Authorization": f"Bearer {second_login['access_token']}"},
    )

    assert detail.status_code == 200
    assert detail.json()["estado"] == "ABIERTO"
    assert detail.json()["total"] == "3601.50"
    assert len(detail.json()["productos"]) == 1
    assert denied.status_code == 404


def test_hu22_producto_sin_unidades_no_crea_pedido_ni_stock_negativo(client):
    _, mesero, product, table = preparar_operacion(client, stock=1)
    response = client.post(
        "/pedidos",
        json={
            "mesa_id": table["id"],
            "productos": [{"producto_id": product["id"], "cantidad": 2}],
        },
        headers=mesero,
    )

    assert response.status_code == 409
    assert client.get("/pedidos", headers=mesero).json() == []
    inventory = client.get("/inventario", headers=mesero).json()
    assert next(row for row in inventory if row["producto_id"] == product["id"])[
        "cantidad"
    ] == 1


def test_hu22_hu33_concurrencia_stock_y_misma_mesa(client, db_engine):
    admin = auth_headers(client)
    provider = client.post(
        "/proveedores",
        json={"nombre": "Proveedor carrera"},
        headers=admin,
    ).json()
    products = []
    for code, price in (("RACE-1", "1000.00"), ("RACE-2", "2000.00")):
        products.append(
            client.post(
                "/productos",
                json={
                    "codigo": code,
                    "nombre": code,
                    "precio_venta": price,
                    "precio_compra": "500.00",
                    "estado": True,
                    "proveedor_id": provider["id"],
                },
                headers=admin,
            ).json()
        )
    tables = [
        client.post(
            "/sedes/1/mesas",
            json={"numero": number},
            headers=admin,
        ).json()
        for number in (1, 2, 3)
    ]
    for product, quantity in zip(products, (1, 2), strict=True):
        client.post(
            "/sedes/1/inventario",
            json={"producto_id": product["id"], "cantidad": quantity},
            headers=admin,
        )

    tokens = []
    for number in (1, 2):
        identification = f"race-user-{number}"
        created = client.post(
            "/usuarios/",
            json={
                "identificacion": f"race-ident-{number}",
                "nombre": f"Mesero carrera {number}",
                "nombre_usuario": identification,
                "email": f"{identification}@refugio.com",
                "password": "Clave-segura-123",
                "es_mesero": True,
                "sedes_ids": [1],
            },
            headers=admin,
        )
        assert created.status_code == 201
        logged_in = client.post(
            "/auth/login",
            json={
                "identificacion": f"race-ident-{number}",
                "password": "Clave-segura-123",
            },
        )
        tokens.append(logged_in.json()["access_token"])

    def simultaneous_create(
        token: str,
        mesa_id: int,
        product_id: int,
        barrier: Barrier,
    ):
        with TestClient(app) as concurrent_client:
            barrier.wait()
            return concurrent_client.post(
                "/pedidos",
                json={
                    "mesa_id": mesa_id,
                    "productos": [{"producto_id": product_id, "cantidad": 1}],
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    stock_race = Barrier(2)
    with ThreadPoolExecutor(max_workers=2) as executor:
        stock_results = list(
            executor.map(
                lambda arguments: simultaneous_create(
                    arguments[0],
                    arguments[1],
                    arguments[2],
                    stock_race,
                ),
                [
                    (tokens[0], tables[0]["id"], products[0]["id"]),
                    (tokens[1], tables[1]["id"], products[0]["id"]),
                ],
            )
        )
    assert sorted(result.status_code for result in stock_results) == [201, 409]

    table_race = Barrier(2)
    with ThreadPoolExecutor(max_workers=2) as executor:
        table_results = list(
            executor.map(
                lambda token: simultaneous_create(
                    token,
                    tables[2]["id"],
                    products[1]["id"],
                    table_race,
                ),
                tokens,
            )
        )
    assert sorted(result.status_code for result in table_results) == [201, 409]

    with sessionmaker(bind=db_engine)() as db:
        remaining = db.query(Inventario).filter_by(
            sede_id=1,
            producto_id=products[0]["id"],
        ).one()
        open_orders = db.query(Pedido).filter(
            Pedido.mesa_id == tables[2]["id"],
            Pedido.estado == "ABIERTO",
        )
        assert remaining.cantidad == 0
        assert remaining.cantidad >= 0
        assert open_orders.count() == 1

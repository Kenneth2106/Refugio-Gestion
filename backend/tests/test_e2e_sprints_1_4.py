from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.core.clock import get_utc_now
from app.main import app
from tests.conftest import auth_headers


PASSWORD = "Clave-segura-123"


def create_waiter(client, admin_headers, suffix, site_id):
    response = client.post(
        "/usuarios/",
        json={
            "identificacion": f"e2e-id-{suffix}",
            "nombre": f"Mesero E2E {suffix}",
            "nombre_usuario": f"e2e-user-{suffix}",
            "email": f"e2e-{suffix}@refugio.com",
            "password": PASSWORD,
            "es_mesero": True,
            "sedes_ids": [site_id],
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def login(client, identification):
    response = client.post(
        "/auth/login",
        json={"identificacion": identification, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def report_step(number, label, check):
    try:
        check()
    except Exception:
        print(f"PASO {number:02d} FAIL — {label}")
        raise
    print(f"PASO {number:02d} PASS — {label}")


def test_hu_e2e_sprints_1_4(client, db_engine, monkeypatch):
    initial_time = datetime.now(timezone.utc).replace(microsecond=0)
    now = [initial_time]
    monkeypatch.setitem(app.dependency_overrides, get_utc_now, lambda: now[0])

    admin_token = login(client, "0000000000")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    site_a = client.post(
        "/sedes/",
        json={"codigo": "E2E-A", "nombre": "Sede E2E A", "direccion": "Calle A"},
        headers=admin_headers,
    ).json()
    site_b = client.post(
        "/sedes/",
        json={"codigo": "E2E-B", "nombre": "Sede E2E B", "direccion": "Calle B"},
        headers=admin_headers,
    ).json()
    table_a = client.post(
        f"/sedes/{site_a['id']}/mesas",
        json={"numero": 1},
        headers=admin_headers,
    ).json()
    race_table_a = client.post(
        f"/sedes/{site_a['id']}/mesas",
        json={"numero": 2},
        headers=admin_headers,
    ).json()
    race_table_b = client.post(
        f"/sedes/{site_a['id']}/mesas",
        json={"numero": 3},
        headers=admin_headers,
    ).json()
    shared_race_table = client.post(
        f"/sedes/{site_a['id']}/mesas",
        json={"numero": 4},
        headers=admin_headers,
    ).json()
    table_b = client.post(
        f"/sedes/{site_b['id']}/mesas",
        json={"numero": 1},
        headers=admin_headers,
    ).json()
    supplier = client.post(
        "/proveedores",
        json={"nombre": "Proveedor E2E"},
        headers=admin_headers,
    ).json()
    product = client.post(
        "/productos",
        json={
            "codigo": "E2E-01",
            "nombre": "Producto E2E",
            "precio_venta": "1250.50",
            "precio_compra": "700.00",
            "estado": True,
            "proveedor_id": supplier["id"],
        },
        headers=admin_headers,
    ).json()
    report_step(
        1,
        "Admin autentica y crea sedes, mesas, proveedor y producto",
        lambda: assert_created(
            site_a,
            site_b,
            table_a,
            race_table_a,
            race_table_b,
            shared_race_table,
            table_b,
            supplier,
            product,
        ),
    )

    waiter_a = create_waiter(client, admin_headers, "a", site_a["id"])
    waiter_a2 = create_waiter(client, admin_headers, "a2", site_a["id"])
    waiter_b = create_waiter(client, admin_headers, "b", site_b["id"])
    report_step(
        2,
        "Admin crea meseros asignados a sus sedes",
        lambda: assert_created(waiter_a, waiter_a2, waiter_b),
    )

    for site_id, quantity in ((site_a["id"], 2), (site_b["id"], 7)):
        response = client.post(
            f"/sedes/{site_id}/inventario",
            json={"producto_id": product["id"], "cantidad": quantity},
            headers=admin_headers,
        )
        assert response.status_code == 200, response.text
    report_step(3, "Carga inicial mantiene inventario independiente por sede", lambda: None)

    with TestClient(app) as client_a, TestClient(app) as client_a2, TestClient(app) as client_b:
        token_a = login(client_a, waiter_a["identificacion"])
        token_a2 = login(client_a2, waiter_a2["identificacion"])
        token_b = login(client_b, waiter_b["identificacion"])
        order_a = client_a.post(
            "/pedidos",
            json={
                "mesa_id": table_a["id"],
                "productos": [{"producto_id": product["id"], "cantidad": 1}],
            },
        )
        tables_a = client_a.get(f"/sedes/{site_a['id']}/mesas").json()
        inventory_a = client_a.get("/inventario").json()
        inventory_b = client_b.get("/inventario").json()
        assert order_a.status_code == 201, order_a.text
        order_a_id = order_a.json()["id"]
        assert next(row for row in tables_a if row["id"] == table_a["id"])[
            "estado_operativo"
        ] == "OCUPADA"
        assert stock_for(inventory_a, product["id"]) == 1
        assert stock_for(inventory_b, product["id"]) == 7
        report_step(
            4,
            "Mesero A ve sus mesas, abre pedido y solo descuenta inventario A",
            lambda: None,
        )

        added = client_a.post(
            f"/pedidos/{order_a_id}/productos",
            json={"producto_id": product["id"], "cantidad": 1},
        )
        inventory_after_add = client_a.get("/inventario").json()
        assert added.status_code == 200, added.text
        assert stock_for(inventory_after_add, product["id"]) == 0
        report_step(5, "Añadir producto al pedido vuelve a descontar existencias", lambda: None)

        no_stock = client_a.post(
            f"/pedidos/{order_a_id}/productos",
            json={"producto_id": product["id"], "cantidad": 1},
        )
        assert no_stock.status_code == 409
        assert stock_for(client_a.get("/inventario").json(), product["id"]) == 0
        report_step(6, "Producto sin unidades no se puede añadir", lambda: None)

        order_b = client_b.post(
            "/pedidos",
            json={
                "mesa_id": table_b["id"],
                "productos": [{"producto_id": product["id"], "cantidad": 1}],
            },
        )
        assert order_b.status_code == 201, order_b.text
        denied_tables = client_a.get(f"/sedes/{site_b['id']}/mesas")
        denied_selection = client_a.post("/auth/sede", json={"sede_id": site_b["id"]})
        denied_order = client_a.get(f"/pedidos/{order_b.json()['id']}")
        assert denied_tables.status_code == 403
        assert denied_selection.status_code == 403
        assert denied_order.status_code == 404
        assert all(row["sede_id"] == site_a["id"] for row in client_a.get("/inventario").json())
        report_step(7, "Mesero A no puede consultar mesas, inventario ni pedidos de B", lambda: None)

        viewed_open_order = client_a2.get(
            f"/mesas/{table_a['id']}/pedido-abierto"
        )
        assert viewed_open_order.status_code == 200
        assert viewed_open_order.json()["id"] == order_a_id
        assert len(client_a2.get("/pedidos").json()) == 1
        report_step(8, "Segundo usuario autorizado ve el pedido abierto sin duplicarlo", lambda: None)

        login(client_a, waiter_a["identificacion"])
        now[0] += timedelta(minutes=2, seconds=59)
        assert client_a.get("/auth/me").status_code == 200
        now[0] += timedelta(minutes=3)
        inactive = client_a.post("/auth/ping")
        assert inactive.status_code == 401
        assert "inactividad" in inactive.json()["detail"].lower()

        login(client_a, waiter_a["identificacion"])
        for _ in range(14):
            now[0] += timedelta(minutes=2)
            assert client_a.post("/auth/ping").status_code == 200
        now[0] += timedelta(minutes=1)
        active_at_29 = client_a.post("/auth/ping")
        now[0] += timedelta(minutes=1)
        expired_at_30 = client_a.post("/auth/ping")
        assert active_at_29.status_code == 200
        assert expired_at_30.status_code == 401
        assert expired_at_30.json()["detail"] == "Sesión expirada"
        report_step(9, "Inactividad de 3 min y límite absoluto de 30 min invalidan sesiones", lambda: None)

        old_token = login(client_a, waiter_a["identificacion"])
        login(client_a, waiter_a["identificacion"])
        with TestClient(app) as old_session_client:
            old_session = old_session_client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {old_token}"},
            )
        current_session = client_a.get("/auth/me")
        assert old_session.status_code == 401
        assert current_session.status_code == 200
        report_step(10, "Segundo login invalida inmediatamente el token anterior", lambda: None)

        fresh_admin_token = login(client, "0000000000")
        fresh_admin_headers = {"Authorization": f"Bearer {fresh_admin_token}"}
        deactivated = client.patch(
            f"/usuarios/{waiter_a['id']}",
            json={"estado": False},
            headers=fresh_admin_headers,
        )
        next_request = client_a.get("/auth/me")
        assert deactivated.status_code == 200
        assert next_request.status_code == 403
        assert next_request.json()["detail"] == "Usuario inactivado"
        report_step(11, "Inactivar usuario bloquea su siguiente petición autenticada", lambda: None)

        selected_site = client.post(
            "/auth/sede",
            json={"sede_id": site_a["id"]},
            headers=fresh_admin_headers,
        )
        updated_product = client.patch(
            f"/productos/{product['id']}",
            json={"precio_venta": "9999.99"},
            headers=fresh_admin_headers,
        )
        preserved_order = client.get(
            f"/pedidos/{order_a_id}",
            headers=fresh_admin_headers,
        )
        assert selected_site.status_code == 200
        assert updated_product.status_code == 200
        assert preserved_order.status_code == 200
        assert preserved_order.json()["productos"][0]["precio_unitario"] == "1250.50"
        report_step(
            12,
            "Cambiar precio del catálogo no altera el precio histórico del pedido",
            lambda: None,
        )

        race_provider = client.post(
            "/proveedores",
            json={"nombre": "Proveedor E2E Carrera"},
            headers=fresh_admin_headers,
        ).json()
        race_products = []
        for code in ("E2E-RACE-1", "E2E-RACE-2"):
            created = client.post(
                "/productos",
                json={
                    "codigo": code,
                    "nombre": code,
                    "precio_venta": "100.00",
                    "precio_compra": "50.00",
                    "estado": True,
                    "proveedor_id": race_provider["id"],
                },
                headers=fresh_admin_headers,
            )
            assert created.status_code == 201, created.text
            race_products.append(created.json())
        for race_product, quantity in zip(race_products, (1, 2), strict=True):
            loaded = client.post(
                f"/sedes/{site_a['id']}/inventario",
                json={"producto_id": race_product["id"], "cantidad": quantity},
                headers=fresh_admin_headers,
            )
            assert loaded.status_code == 200, loaded.text
        race_users = [
            create_waiter(client, fresh_admin_headers, f"race-{suffix}", site_a["id"])
            for suffix in ("c", "d")
        ]
        race_tokens = []
        for race_user in race_users:
            with TestClient(app) as login_client:
                race_tokens.append(login(login_client, race_user["identificacion"]))

        def simultaneous_create(token, mesa_id, product_id, barrier):
            with TestClient(app) as request_client:
                barrier.wait()
                return request_client.post(
                    "/pedidos",
                    json={
                        "mesa_id": mesa_id,
                        "productos": [{"producto_id": product_id, "cantidad": 1}],
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )

        stock_barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as executor:
            stock_results = list(
                executor.map(
                    lambda args: simultaneous_create(
                        args[0], args[1], race_products[0]["id"], stock_barrier
                    ),
                    zip(race_tokens, (race_table_a["id"], race_table_b["id"]), strict=True),
                )
            )
        table_barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as executor:
            table_results = list(
                executor.map(
                    lambda token: simultaneous_create(
                        token,
                        shared_race_table["id"],
                        race_products[1]["id"],
                        table_barrier,
                    ),
                    race_tokens,
                )
            )
        assert sorted(response.status_code for response in stock_results) == [201, 409]
        assert sorted(response.status_code for response in table_results) == [201, 409]
        report_step(13, "Concurrencia: nunca stock negativo ni dos pedidos abiertos por mesa", lambda: None)

    migration = Config(
        str(Path(__file__).resolve().parents[1] / "alembic.ini")
    )
    with db_engine.begin() as connection:
        migration.attributes["connection"] = connection
        command.downgrade(migration, "base")
        assert "usuarios" not in inspect(connection).get_table_names()
        command.upgrade(migration, "head")
        table_names = set(inspect(connection).get_table_names())
        assert {"usuarios", "inventarios", "pedidos", "lineas_pedido"} <= table_names
    report_step(14, "Alembic migra desde esquema vacío y permite downgrade/re-upgrade", lambda: None)


def assert_created(*entities):
    assert all(entity and entity.get("id") for entity in entities)


def stock_for(rows, product_id):
    return next(row["cantidad"] for row in rows if row["producto_id"] == product_id)

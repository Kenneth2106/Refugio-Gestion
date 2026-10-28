from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from threading import Barrier
from time import perf_counter

from openpyxl import load_workbook
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.auditoria.models import EventoAuditoria
from app.main import app
from app.ventas.models import Pedido
from tests.conftest import auth_headers


def crear_pedido_caja(client, *, codigo="CAJA-01", precio_compra="20.00"):
    admin = auth_headers(client)
    provider = client.post(
        "/proveedores",
        json={"nombre": f"Proveedor {codigo}"},
        headers=admin,
    ).json()
    product = client.post(
        "/productos",
        json={
            "codigo": codigo,
            "nombre": f"Producto {codigo}",
            "precio_venta": "50.00",
            "precio_compra": precio_compra,
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
        json={"producto_id": product["id"], "cantidad": 5},
        headers=admin,
    )
    order = client.post(
        "/pedidos",
        json={
            "mesa_id": table["id"],
            "productos": [{"producto_id": product["id"], "cantidad": 2}],
        },
        headers=admin,
    )
    assert order.status_code == 201
    return admin, product, table, order.json()


def crear_cajero(client, admin):
    created = client.post(
        "/usuarios/",
        json={
            "identificacion": "cajero-001",
            "nombre": "Cajero Pruebas",
            "nombre_usuario": "cajero-pruebas",
            "email": "cajero-pruebas@refugio.com",
            "password": "Clave-segura-123",
            "es_cajero": True,
            "sedes_ids": [1],
        },
        headers=admin,
    )
    assert created.status_code == 201
    login = client.post(
        "/auth/login",
        json={
            "identificacion": "cajero-001",
            "password": "Clave-segura-123",
        },
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_hu26_hu27_hu28_hu29_hu30_cajero_cobra_cierra_y_consulta_factura(
    client,
    db_engine,
):
    admin, product, table, order = crear_pedido_caja(client)
    cashier = crear_cajero(client, admin)

    pending = client.get("/caja/pedidos-pendientes", headers=cashier)
    detail = client.get(f"/caja/pedidos/{order['id']}", headers=cashier)
    payment_started = perf_counter()
    invoice = client.post(
        f"/caja/pedidos/{order['id']}/pago",
        json={"medio_pago": "TARJETA"},
        headers=cashier,
    )
    payment_duration = perf_counter() - payment_started
    duplicate_payment = client.post(
        f"/caja/pedidos/{order['id']}/pago",
        json={"medio_pago": "EFECTIVO"},
        headers=cashier,
    )
    saved_invoice = client.get(
        f"/caja/pedidos/{order['id']}/factura",
        headers=cashier,
    )

    assert pending.status_code == 200
    assert pending.json()[0]["id"] == order["id"]
    assert pending.json()[0]["usuario_nombre"] == "Administrador Sistema"
    assert pending.json()[0]["total"] == "100.00"
    assert detail.status_code == 200
    assert detail.json()["productos"][0]["producto_id"] == product["id"]
    assert invoice.status_code == 200
    assert invoice.json()["medio_pago"] == "TARJETA"
    assert invoice.json()["cerrado_por"] > 0
    assert invoice.json()["total"] == "100.00"
    assert invoice.json()["productos"][0]["subtotal"] == "100.00"
    assert payment_duration < 2
    assert duplicate_payment.status_code == 409
    assert saved_invoice.status_code == 200
    assert client.get("/caja/pedidos-pendientes", headers=cashier).json() == []
    assert client.get("/sedes/1/mesas", headers=admin).json()[0][
        "estado_operativo"
    ] == "LIBRE"

    with sessionmaker(bind=db_engine)() as db:
        closed = db.query(Pedido).filter_by(id=order["id"]).one()
        assert closed.estado == "CERRADO"
        assert closed.medio_pago == "TARJETA"
        assert closed.cerrado_por > 0
        events = db.query(EventoAuditoria).filter_by(pedido_id=order["id"]).all()
        assert {event.accion for event in events} == {
            "PEDIDO_CREADO",
            "PEDIDO_CERRADO",
        }
        login_event = db.query(EventoAuditoria).filter_by(
            actor_id=closed.cerrado_por,
            accion="INICIO_SESION",
        ).first()
        assert login_event is not None


def test_hu27_cajero_sin_sede_asignada_no_puede_ver_pedidos(client):
    admin, _, _, _ = crear_pedido_caja(client)
    cashier = crear_cajero(client, admin)
    other_site = client.post(
        "/sedes/",
        json={"codigo": "SEDE-B", "nombre": "Sede B", "direccion": "Calle B"},
        headers=admin,
    ).json()

    response = client.get(
        f"/sedes/{other_site['id']}/mesas",
        headers=cashier,
    )

    assert response.status_code == 403


def test_hu17_hu31_hu32_reporte_filtrado_y_excel_conservan_datos_autorizados(
    client,
):
    admin, product, _, order = crear_pedido_caja(client, precio_compra="20.00")
    cashier = crear_cajero(client, admin)
    changed_catalog = client.patch(
        f"/productos/{product['id']}",
        json={
            "nombre": "Nombre actualizado",
            "precio_compra": "30.00",
            "precio_venta": "60.00",
        },
        headers=admin,
    )
    assert changed_catalog.status_code == 200
    open_orders_report = client.get(
        "/reportes/ventas",
        params={"estado": "ABIERTO"},
        headers=cashier,
    )
    assert open_orders_report.status_code == 200
    assert open_orders_report.json() == []
    paid = client.post(
        f"/caja/pedidos/{order['id']}/pago",
        json={"medio_pago": "EFECTIVO"},
        headers=cashier,
    )
    assert paid.status_code == 200
    assert paid.json()["cerrado_en"].endswith("-05:00")
    closing_date = paid.json()["cerrado_en"][:10]

    report = client.get(
        "/reportes/ventas",
        params={
            "medio_pago": "EFECTIVO",
            "sede_id": 1,
            "fecha_fin": closing_date,
        },
        headers=cashier,
    )
    export = client.get(
        "/reportes/ventas/excel",
        params={
            "medio_pago": "EFECTIVO",
            "sede_id": 1,
            "fecha_fin": closing_date,
        },
        headers=cashier,
    )
    previous_day_report = client.get(
        "/reportes/ventas",
        params={
            "medio_pago": "EFECTIVO",
            "sede_id": 1,
            "fecha_fin": (date.fromisoformat(closing_date) - timedelta(days=1)).isoformat(),
        },
        headers=cashier,
    )
    denied = client.get(
        "/reportes/ventas",
        params={"sede_id": 999},
        headers=cashier,
    )
    assert report.status_code == 200
    assert report.json() == [
        {
            "producto_id": product["id"],
            "codigo": "CAJA-01",
            "nombre": "Producto CAJA-01",
            "cantidad": 2,
            "valor_compra": "40.00",
            "precio_venta": "50.00",
            "valor_venta": "100.00",
            "ganancia": "60.00",
            "sede_id": 1,
            "sede": "Base Test Site",
        }
    ]
    assert export.status_code == 200
    assert "spreadsheetml.sheet" in export.headers["content-type"]
    workbook = load_workbook(BytesIO(export.content))
    sheet = workbook["Ventas"]
    assert list(sheet.values)[1][3:8] == (2, 40, 50, 100, 60)
    assert sheet["A1"].fill.fgColor.rgb.endswith("38291A")
    assert sheet["A1"].font.bold is True
    assert sheet["A1"].alignment.horizontal == "center"
    assert sheet["E2"].number_format == '"$"#,##0.00'
    assert sheet.freeze_panes == "A2"
    assert sheet.auto_filter.ref == "A1:J2"
    assert sheet.sheet_view.showGridLines is False
    assert previous_day_report.status_code == 200
    assert previous_day_report.json() == []
    assert denied.status_code == 403


def test_hu30_mesero_no_puede_cobrar(client):
    admin, _, _, order = crear_pedido_caja(client)
    waiter = client.post(
        "/usuarios/",
        json={
            "identificacion": "mesero-sin-caja",
            "nombre": "Mesero",
            "nombre_usuario": "mesero-sin-caja",
            "email": "mesero-sin-caja@refugio.com",
            "password": "Clave-segura-123",
            "es_mesero": True,
            "sedes_ids": [1],
        },
        headers=admin,
    )
    assert waiter.status_code == 201
    login = client.post(
        "/auth/login",
        json={
            "identificacion": "mesero-sin-caja",
            "password": "Clave-segura-123",
        },
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.post(
        f"/caja/pedidos/{order['id']}/pago",
        json={"medio_pago": "EFECTIVO"},
        headers=headers,
    )

    assert response.status_code == 403


def test_hu40_veinte_cajeros_consultan_pedidos_en_menos_de_dos_segundos(client):
    admin, _, _, _ = crear_pedido_caja(client)
    tokens = []
    for index in range(20):
        identity = f"cajero-carga-{index}"
        created = client.post(
            "/usuarios/",
            json={
                "identificacion": identity,
                "nombre": f"Cajero {index}",
                "nombre_usuario": identity,
                "email": f"{identity}@refugio.com",
                "password": "Clave-segura-123",
                "es_cajero": True,
                "sedes_ids": [1],
            },
            headers=admin,
        )
        assert created.status_code == 201
        logged_in = client.post(
            "/auth/login",
            json={
                "identificacion": identity,
                "password": "Clave-segura-123",
            },
        )
        assert logged_in.status_code == 200
        tokens.append(logged_in.json()["access_token"])

    barrier = Barrier(20)

    def consult_pending_orders(token):
        with TestClient(app) as concurrent_client:
            barrier.wait()
            started = perf_counter()
            response = concurrent_client.get(
                "/caja/pedidos-pendientes",
                headers={"Authorization": f"Bearer {token}"},
            )
            return response.status_code, perf_counter() - started

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(consult_pending_orders, tokens))

    assert [status_code for status_code, _ in results] == [200] * 20
    assert max(duration for _, duration in results) < 2

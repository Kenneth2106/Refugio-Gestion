from decimal import Decimal

from sqlalchemy.orm import sessionmaker

from app.catalogo.models import Producto, Proveedor
from tests.conftest import auth_headers


def crear_proveedor(client, headers, nombre="Proveedor Norte"):
    return client.post(
        "/proveedores",
        json={"nombre": nombre},
        headers=headers,
    )


def crear_producto(client, headers, proveedor_id, **overrides):
    payload = {
        "codigo": "PROD-01",
        "nombre": "Producto de prueba",
        "precio_venta": "12500.25",
        "precio_compra": "7000.10",
        "estado": True,
        "proveedor_id": proveedor_id,
    }
    payload.update(overrides)
    return client.post("/productos", json=payload, headers=headers)


def test_hu12_crear_proveedor_con_id_autogenerado(client):
    response = crear_proveedor(client, auth_headers(client))

    assert response.status_code == 201
    assert response.json()["id"] > 0
    assert response.json()["nombre"] == "Proveedor Norte"


def test_hu12_nombre_proveedor_duplicado_exacto_rechazado(client):
    headers = auth_headers(client)
    first = crear_proveedor(client, headers)
    duplicate = crear_proveedor(client, headers)

    assert first.status_code == 201
    assert duplicate.status_code == 409


def test_hu12_nombre_proveedor_difiere_por_mayusculas_es_valido(client):
    headers = auth_headers(client)
    first = crear_proveedor(client, headers, "Proveedor Norte")
    second = crear_proveedor(client, headers, "proveedor norte")

    assert first.status_code == 201
    assert second.status_code == 201


def test_hu11_producto_exige_todos_los_campos_incluido_proveedor(client):
    headers = auth_headers(client)
    response = client.post(
        "/productos",
        json={
            "codigo": "P-1",
            "nombre": "Producto",
            "precio_venta": "100",
            "precio_compra": "60",
            "estado": True,
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_hu11_cantidad_no_es_campo_del_producto(client):
    headers = auth_headers(client)
    provider = crear_proveedor(client, headers).json()

    response = crear_producto(
        client,
        headers,
        provider["id"],
        cantidad=50,
    )

    assert response.status_code == 422


def test_hu11_codigo_producto_unico(client):
    headers = auth_headers(client)
    provider = crear_proveedor(client, headers).json()
    first = crear_producto(client, headers, provider["id"])
    second = crear_producto(
        client,
        headers,
        provider["id"],
        nombre="Otro producto",
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_hu11_producto_usa_decimal_y_catalogo_es_central(client, db_engine):
    headers = auth_headers(client)
    provider = crear_proveedor(client, headers).json()
    product = crear_producto(client, headers, provider["id"])

    assert product.status_code == 201
    with sessionmaker(bind=db_engine)() as db:
        stored = db.query(Producto).filter_by(id=product.json()["id"]).one()
        assert isinstance(stored.precio_venta, Decimal)
        assert stored.precio_venta == Decimal("12500.25")
        assert stored.proveedor_id == provider["id"]

    listed = client.get("/productos", headers=headers)
    assert any(entry["codigo"] == "PROD-01" for entry in listed.json())


def test_hu12_producto_conserva_relacion_con_proveedor(client, db_engine):
    headers = auth_headers(client)
    provider = crear_proveedor(client, headers).json()
    product = crear_producto(client, headers, provider["id"]).json()

    with sessionmaker(bind=db_engine)() as db:
        stored_product = db.query(Producto).filter_by(id=product["id"]).one()
        stored_provider = db.query(Proveedor).filter_by(id=provider["id"]).one()
        assert stored_product.proveedor_id == stored_provider.id


def test_hu16_administrador_consulta_y_modifica_catalogo(client):
    headers = auth_headers(client)
    provider = crear_proveedor(client, headers).json()
    product = crear_producto(client, headers, provider["id"]).json()

    response = client.patch(
        f"/productos/{product['id']}",
        json={"precio_venta": "14000.00", "nombre": "Producto actualizado"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "Producto actualizado"
    assert response.json()["precio_venta"] == "14000.00"
    assert client.get("/productos", headers=headers).status_code == 200


def test_hu16_actualizacion_de_producto_rechaza_valores_nulos(client):
    headers = auth_headers(client)
    provider = crear_proveedor(client, headers).json()
    product = crear_producto(client, headers, provider["id"]).json()

    response = client.patch(
        f"/productos/{product['id']}",
        json={"proveedor_id": None},
        headers=headers,
    )

    assert response.status_code == 422


def test_hu18_informacion_general_autorizada(client):
    headers = auth_headers(client)
    provider = crear_proveedor(client, headers).json()
    product = crear_producto(client, headers, provider["id"]).json()

    response = client.get("/admin/informacion-general", headers=headers)
    body = response.json()

    assert response.status_code == 200
    assert any(item["id"] == product["id"] for item in body["productos"])
    assert any(item["id"] == provider["id"] for item in body["proveedores"])
    assert {"usuarios", "sedes", "inventario", "pedidos_abiertos", "mesas"} <= body.keys()

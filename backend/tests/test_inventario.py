from tests.conftest import auth_headers


def setup_inventory(client):
    headers = auth_headers(client)
    provider = client.post(
        "/proveedores",
        json={"nombre": "Proveedor inventario"},
        headers=headers,
    ).json()
    product = client.post(
        "/productos",
        json={
            "codigo": "INV-01",
            "nombre": "Producto inventario",
            "precio_venta": "5000.00",
            "precio_compra": "2500.00",
            "estado": True,
            "proveedor_id": provider["id"],
        },
        headers=headers,
    ).json()
    return headers, product


def test_hu21_inventario_lista_producto_y_unidades_completas(client):
    headers, product = setup_inventory(client)
    response = client.post(
        "/sedes/1/inventario",
        json={"producto_id": product["id"], "cantidad": 7},
        headers=headers,
    )

    assert response.status_code == 200
    listed = client.get("/inventario", headers=headers)
    entry = next(row for row in listed.json() if row["producto_id"] == product["id"])
    assert entry["cantidad"] == 7
    assert isinstance(entry["cantidad"], int)


def test_hu33_carga_inicial_y_suma_por_sede(client):
    headers, product = setup_inventory(client)
    initial = client.post(
        "/sedes/1/inventario",
        json={"producto_id": product["id"], "cantidad": 4},
        headers=headers,
    )
    added = client.post(
        "/sedes/1/inventario",
        json={"producto_id": product["id"], "cantidad": 3},
        headers=headers,
    )

    assert initial.json()["cantidad"] == 4
    assert added.json()["cantidad"] == 7


def test_hu33_rechaza_cantidades_fraccionarias_y_no_positivas(client):
    headers, product = setup_inventory(client)
    fractional = client.post(
        "/sedes/1/inventario",
        json={"producto_id": product["id"], "cantidad": 1.5},
        headers=headers,
    )
    zero = client.post(
        "/sedes/1/inventario",
        json={"producto_id": product["id"], "cantidad": 0},
        headers=headers,
    )

    assert fractional.status_code == 422
    assert zero.status_code == 422


def test_hu33_inventario_no_se_puede_cargar_en_sede_inexistente(client):
    headers, product = setup_inventory(client)
    response = client.post(
        "/sedes/9999/inventario",
        json={"producto_id": product["id"], "cantidad": 2},
        headers=headers,
    )

    assert response.status_code == 404

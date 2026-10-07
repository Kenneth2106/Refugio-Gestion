"""Endpoint de consulta agregada disponible únicamente para administradores."""

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload

from app.auth.router import require_admin
from app.catalogo.models import Producto, Proveedor
from app.core.database import get_db
from app.inventario.models import Inventario
from app.sedes.models import Mesa, Sede
from app.usuarios.models import Usuario
from app.ventas.models import LineaPedido, Pedido
from app.ventas.router import serialize_order

router = APIRouter(prefix="/admin", tags=["Administración"])


@router.get("/informacion-general")
def consultar_informacion_general(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict[str, object]:
    """Devuelve un resumen de usuarios, sedes, catálogo, inventario y operación."""
    users = db.query(Usuario).options(joinedload(Usuario.sedes)).order_by(Usuario.id).all()
    sites = db.query(Sede).order_by(Sede.id).all()
    products = db.query(Producto).order_by(Producto.id).all()
    suppliers = db.query(Proveedor).order_by(Proveedor.id).all()
    stocks = (
        db.query(Inventario, Producto)
        .join(Producto, Producto.id == Inventario.producto_id)
        .order_by(Inventario.sede_id, Producto.codigo)
        .all()
    )
    open_orders = (
        db.query(Pedido)
        .options(joinedload(Pedido.lineas).joinedload(LineaPedido.producto))
        .filter(Pedido.estado == "ABIERTO")
        .order_by(Pedido.id)
        .all()
    )
    tables = db.query(Mesa).order_by(Mesa.sede_id, Mesa.numero).all()
    order_ids_by_table = {
        table_id: order_id
        for table_id, order_id in db.query(Pedido.mesa_id, Pedido.id).filter(
            Pedido.estado == "ABIERTO"
        )
    }

    return jsonable_encoder({
        "usuarios": [
            {
                "id": user.id,
                "identificacion": user.identificacion,
                "nombre": user.nombre,
                "nombre_usuario": user.nombre_usuario,
                "email": user.email,
                "estado": user.estado,
                "roles": (
                    (["admin"] if user.es_admin else [])
                    + (["mesero"] if user.es_mesero or user.es_admin else [])
                    + (["cajero"] if user.es_cajero or user.es_admin else [])
                ),
                "sedes_ids": [assignment.sede_id for assignment in user.sedes],
            }
            for user in users
        ],
        "sedes": sites,
        "productos": products,
        "proveedores": suppliers,
        "inventario": [
            {
                "sede_id": stock.sede_id,
                "producto_id": product.id,
                "codigo": product.codigo,
                "nombre": product.nombre,
                "cantidad": stock.cantidad,
            }
            for stock, product in stocks
        ],
        "pedidos_abiertos": [
            serialize_order(order)
            for order in open_orders
        ],
        "mesas": [
            {
                "id": table.id,
                "sede_id": table.sede_id,
                "numero": table.numero,
                "activa": table.estado,
                "estado_operativo": (
                    "OCUPADA"
                    if table.id in order_ids_by_table
                    else "LIBRE"
                ),
                "pedido_abierto_id": order_ids_by_table.get(table.id),
            }
            for table in tables
        ],
    })

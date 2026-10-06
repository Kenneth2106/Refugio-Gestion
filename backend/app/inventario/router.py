from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.auth.router import require_admin, require_mesero, require_selected_site
from app.catalogo.models import Producto
from app.core.database import get_db
from app.inventario.models import Inventario
from app.inventario.schemas import InventarioIncrement, InventarioOut
from app.sedes.models import Sede
from app.usuarios.models import Usuario

router = APIRouter(tags=["Inventario"])


@router.get("/inventario", response_model=list[InventarioOut])
def consultar_inventario(
    sede: Sede = Depends(require_selected_site),
    _: Usuario = Depends(require_mesero),
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    rows = (
        db.query(Inventario, Producto)
        .join(Producto, Producto.id == Inventario.producto_id)
        .filter(
            Inventario.sede_id == sede.id,
            Producto.estado.is_(True),
        )
        .order_by(Producto.codigo)
        .all()
    )
    return [
        {
            "sede_id": stock.sede_id,
            "producto_id": product.id,
            "codigo": product.codigo,
            "nombre": product.nombre,
            "cantidad": stock.cantidad,
        }
        for stock, product in rows
    ]


@router.post(
    "/sedes/{sede_id}/inventario",
    response_model=InventarioOut,
    status_code=status.HTTP_200_OK,
)
def sumar_inventario(
    sede_id: int,
    entry: InventarioIncrement,
    _: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    sede = (
        db.query(Sede)
        .filter(Sede.id == sede_id, Sede.estado.is_(True))
        .first()
    )
    if sede is None:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    producto = (
        db.query(Producto)
        .filter(Producto.id == entry.producto_id, Producto.estado.is_(True))
        .first()
    )
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    statement = insert(Inventario).values(
        sede_id=sede.id,
        producto_id=producto.id,
        cantidad=entry.cantidad,
    )
    statement = statement.on_conflict_do_update(
        index_elements=[Inventario.sede_id, Inventario.producto_id],
        set_={"cantidad": Inventario.cantidad + statement.excluded.cantidad},
    ).returning(Inventario.cantidad)
    quantity = db.execute(statement).scalar_one()
    db.commit()
    return {
        "sede_id": sede.id,
        "producto_id": producto.id,
        "codigo": producto.codigo,
        "nombre": producto.nombre,
        "cantidad": quantity,
    }

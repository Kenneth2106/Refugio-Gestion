from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.auth.router import (
    SesionAutenticada,
    get_current_session,
    require_mesero,
    require_selected_site,
)
from app.catalogo.models import Producto
from app.core.clock import get_utc_now
from app.core.database import get_db
from app.inventario.models import Inventario
from app.sedes.models import Mesa, Sede
from app.usuarios.models import Usuario
from app.ventas.models import LineaPedido, Pedido
from app.ventas.schemas import (
    LineaPedidoOut,
    PedidoCreate,
    PedidoOut,
    PedidoProductoAdd,
)

router = APIRouter(tags=["Pedidos"])


def serialize_order(pedido: Pedido) -> PedidoOut:
    lines = [
        LineaPedidoOut(
            id=line.id,
            producto_id=line.producto_id,
            codigo=line.producto.codigo,
            nombre=line.producto.nombre,
            cantidad=line.cantidad,
            precio_unitario=line.precio_unitario,
            usuario_id=line.usuario_id,
            creado_en=line.creado_en,
        )
        for line in pedido.lineas
    ]
    total = sum(
        (line.precio_unitario * line.cantidad for line in pedido.lineas),
        start=Decimal("0.00"),
    )
    return PedidoOut(
        id=pedido.id,
        usuario_id=pedido.usuario_id,
        sede_id=pedido.sede_id,
        mesa_id=pedido.mesa_id,
        estado=pedido.estado,
        creado_en=pedido.creado_en,
        productos=lines,
        total=total,
    )


def lock_inventory(
    db: Session,
    site_id: int,
    product_ids: list[int],
) -> dict[int, Inventario]:
    # El orden estable de bloqueo evita ciclos cuando dos pedidos contienen varios productos.
    stocks = (
        db.query(Inventario)
        .filter(
            Inventario.sede_id == site_id,
            Inventario.producto_id.in_(product_ids),
        )
        .order_by(Inventario.producto_id)
        .with_for_update()
        .all()
    )
    return {stock.producto_id: stock for stock in stocks}


def aggregate_items(items: list[tuple[int, int]]) -> dict[int, int]:
    aggregated: dict[int, int] = {}
    for product_id, quantity in items:
        aggregated[product_id] = aggregated.get(product_id, 0) + quantity
    return aggregated


def add_order_lines(
    db: Session,
    pedido: Pedido,
    usuario: Usuario,
    product_quantities: dict[int, int],
    products: dict[int, Producto],
    stocks: dict[int, Inventario],
    now: datetime,
) -> None:
    # Stock, precio histórico y línea se guardan en la transacción del endpoint.
    missing_stock = [
        product_id
        for product_id, quantity in product_quantities.items()
        if product_id not in stocks or stocks[product_id].cantidad < quantity
    ]
    if missing_stock:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Inventario insuficiente para uno o más productos",
        )

    for product_id in sorted(product_quantities):
        quantity = product_quantities[product_id]
        stock = stocks[product_id]
        stock.cantidad -= quantity
        db.add(
            LineaPedido(
                pedido=pedido,
                producto_id=product_id,
                cantidad=quantity,
                precio_unitario=products[product_id].precio_venta,
                usuario_id=usuario.id,
                creado_en=now,
            )
        )


@router.get("/mesas/{mesa_id}/pedido-abierto", response_model=PedidoOut | None)
def obtener_pedido_abierto_de_mesa(
    mesa_id: int,
    sede: Sede = Depends(require_selected_site),
    _: Usuario = Depends(require_mesero),
    db: Session = Depends(get_db),
) -> PedidoOut | None:
    mesa = (
        db.query(Mesa)
        .filter(
            Mesa.id == mesa_id,
            Mesa.sede_id == sede.id,
            Mesa.estado.is_(True),
        )
        .first()
    )
    if mesa is None:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    pedido = (
        db.query(Pedido)
        .options(joinedload(Pedido.lineas).joinedload(LineaPedido.producto))
        .filter(Pedido.mesa_id == mesa.id, Pedido.estado == "ABIERTO")
        .first()
    )
    return serialize_order(pedido) if pedido is not None else None


@router.post(
    "/pedidos",
    response_model=PedidoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_pedido(
    pedido_in: PedidoCreate,
    sede: Sede = Depends(require_selected_site),
    session: SesionAutenticada = Depends(get_current_session),
    _: Usuario = Depends(require_mesero),
    db: Session = Depends(get_db),
    now: datetime = Depends(get_utc_now),
) -> PedidoOut:
    # Los bloqueos y el índice único parcial evitan pedidos abiertos duplicados.
    mesa = (
        db.query(Mesa)
        .filter(
            Mesa.id == pedido_in.mesa_id,
            Mesa.sede_id == sede.id,
            Mesa.estado.is_(True),
        )
        .with_for_update()
        .first()
    )
    if mesa is None:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")

    open_order = (
        db.query(Pedido)
        .filter(Pedido.mesa_id == mesa.id, Pedido.estado == "ABIERTO")
        .first()
    )
    if open_order is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La mesa ya tiene un pedido abierto",
        )

    quantities = aggregate_items(
        [(item.producto_id, item.cantidad) for item in pedido_in.productos]
    )
    products = (
        db.query(Producto)
        .filter(
            Producto.id.in_(sorted(quantities)),
            Producto.estado.is_(True),
        )
        .order_by(Producto.id)
        .all()
    )
    products_by_id = {product.id: product for product in products}
    if len(products_by_id) != len(quantities):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    stocks = lock_inventory(db, sede.id, sorted(quantities))

    pedido = Pedido(
        usuario_id=session.usuario.id,
        sede_id=sede.id,
        mesa_id=mesa.id,
        estado="ABIERTO",
        creado_en=now,
    )
    db.add(pedido)
    add_order_lines(
        db,
        pedido,
        session.usuario,
        quantities,
        products_by_id,
        stocks,
        now,
    )
    db.commit()
    db.refresh(pedido)
    return serialize_order(pedido)


@router.post(
    "/pedidos/{pedido_id}/productos",
    response_model=PedidoOut,
)
def agregar_producto(
    pedido_id: int,
    item: PedidoProductoAdd,
    sede: Sede = Depends(require_selected_site),
    session: SesionAutenticada = Depends(get_current_session),
    _: Usuario = Depends(require_mesero),
    db: Session = Depends(get_db),
    now: datetime = Depends(get_utc_now),
) -> PedidoOut:
    # Serializa cambios al pedido abierto antes de validar stock y guardar la nueva línea.
    pedido = (
        db.query(Pedido)
        .filter(
            Pedido.id == pedido_id,
            Pedido.sede_id == sede.id,
        )
        .with_for_update()
        .first()
    )
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado != "ABIERTO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se pueden modificar pedidos abiertos",
        )
    producto = (
        db.query(Producto)
        .filter(Producto.id == item.producto_id, Producto.estado.is_(True))
        .first()
    )
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    stocks = lock_inventory(db, sede.id, [producto.id])
    add_order_lines(
        db,
        pedido,
        session.usuario,
        {producto.id: item.cantidad},
        {producto.id: producto},
        stocks,
        now,
    )
    db.commit()
    db.refresh(pedido)
    return serialize_order(pedido)


@router.get("/pedidos", response_model=list[PedidoOut])
def listar_pedidos_de_sede(
    sede: Sede = Depends(require_selected_site),
    _: Usuario = Depends(require_mesero),
    db: Session = Depends(get_db),
) -> list[PedidoOut]:
    pedidos = (
        db.query(Pedido)
        .options(joinedload(Pedido.lineas).joinedload(LineaPedido.producto))
        .filter(Pedido.sede_id == sede.id)
        .order_by(Pedido.id)
        .all()
    )
    return [serialize_order(pedido) for pedido in pedidos]


@router.get("/pedidos/{pedido_id}", response_model=PedidoOut)
def consultar_pedido(
    pedido_id: int,
    sede: Sede = Depends(require_selected_site),
    _: Usuario = Depends(require_mesero),
    db: Session = Depends(get_db),
) -> PedidoOut:
    pedido = (
        db.query(Pedido)
        .options(joinedload(Pedido.lineas).joinedload(LineaPedido.producto))
        .filter(
            Pedido.id == pedido_id,
            Pedido.sede_id == sede.id,
        )
        .first()
    )
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return serialize_order(pedido)

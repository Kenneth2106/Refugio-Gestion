"""Rutas de administración de sedes y mesas y consulta operativa por sede."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.router import (
    require_admin,
    require_mesero,
    require_site_access,
    get_current_user,
)
from app.core.database import get_db
from app.sedes.models import Mesa, Sede
from app.sedes.schemas import (
    MesaCreate,
    MesaOut,
    MesaUpdate,
    SedeCreate,
    SedeOut,
    SedeUpdate,
)
from app.usuarios.models import Usuario, UsuarioSede
from app.ventas.models import Pedido

router = APIRouter(prefix="/sedes", tags=["Sedes y Mesas"])


@router.post("/", response_model=SedeOut, status_code=status.HTTP_201_CREATED)
def crear_sede(
    sede_in: SedeCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Sede:
    """Crea sede con código único; solo un administrador puede hacerlo."""
    sede = Sede(**sede_in.model_dump())
    db.add(sede)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de sede ya existe",
        ) from None
    db.refresh(sede)
    return sede


@router.get("/", response_model=list[SedeOut])
def listar_sedes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[Sede]:
    """Lista sedes activas globales al admin o asignadas al usuario."""
    query = db.query(Sede).filter(Sede.estado.is_(True))
    if not current_user.es_admin:
        query = query.join(
            UsuarioSede,
            UsuarioSede.sede_id == Sede.id,
        ).filter(UsuarioSede.usuario_id == current_user.id)
    return query.order_by(Sede.id).all()


@router.patch("/{sede_id}", response_model=SedeOut)
def actualizar_sede(
    sede_id: int,
    sede_in: SedeUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Sede:
    """Modifica datos o estado de una sede sin borrarla."""
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if sede is None:
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    values = sede_in.model_dump(exclude_unset=True)
    if any(value is None for value in values.values()):
        raise HTTPException(status_code=422, detail="Los campos no pueden ser nulos")
    for field, value in values.items():
        setattr(sede, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El código de sede ya existe",
        ) from None
    db.refresh(sede)
    return sede


@router.post(
    "/{sede_id}/mesas",
    response_model=MesaOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_mesa(
    sede_id: int,
    mesa_in: MesaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Mesa:
    """Registra una mesa con número único dentro de la sede indicada."""
    sede = (
        db.query(Sede)
        .filter(Sede.id == sede_id, Sede.estado.is_(True))
        .first()
    )
    if sede is None:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    mesa = Mesa(sede_id=sede.id, **mesa_in.model_dump())
    db.add(mesa)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de mesa ya existe en esta sede",
        ) from None
    db.refresh(mesa)
    return mesa


@router.get("/{sede_id}/mesas", response_model=list[MesaOut])
def listar_mesas_sede(
    sede: Sede = Depends(require_site_access),
    _: Usuario = Depends(require_mesero),
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    """Lista mesas autorizadas y deriva su estado de pedidos abiertos."""
    mesas = (
        db.query(Mesa)
        .filter(
            Mesa.sede_id == sede.id,
            Mesa.estado.is_(True),
        )
        .order_by(Mesa.numero)
        .all()
    )
    open_orders = (
        db.query(Pedido.mesa_id, Pedido.id)
        .filter(
            Pedido.sede_id == sede.id,
            Pedido.estado == "ABIERTO",
            Pedido.mesa_id.in_([mesa.id for mesa in mesas]),
        )
        .all()
        if mesas
        else []
    )
    orders_by_table = {table_id: order_id for table_id, order_id in open_orders}
    return [
        {
            "id": mesa.id,
            "sede_id": mesa.sede_id,
            "numero": mesa.numero,
            "estado": mesa.estado,
            "estado_operativo": (
                "OCUPADA" if mesa.id in orders_by_table else "LIBRE"
            ),
            "pedido_abierto_id": orders_by_table.get(mesa.id),
        }
        for mesa in mesas
    ]


@router.patch("/mesas/{mesa_id}", response_model=MesaOut)
def actualizar_mesa(
    mesa_id: int,
    mesa_in: MesaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Mesa:
    """Actualiza número o estado de mesa, conservando sus referencias."""
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if mesa is None:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    values = mesa_in.model_dump(exclude_unset=True)
    if any(value is None for value in values.values()):
        raise HTTPException(status_code=422, detail="Los campos no pueden ser nulos")
    for field, value in values.items():
        setattr(mesa, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de mesa ya existe en esta sede",
        ) from None
    db.refresh(mesa)
    return mesa

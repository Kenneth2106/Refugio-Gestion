"""Rutas administrativas para alta/consulta/edición de proveedores y productos."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.router import require_admin
from app.catalogo.models import Producto, Proveedor
from app.catalogo.schemas import (
    ProductoCreate,
    ProductoOut,
    ProductoUpdate,
    ProveedorCreate,
    ProveedorOut,
)
from app.core.database import get_db
from app.usuarios.models import Usuario

router = APIRouter(tags=["Catálogo"])


@router.post(
    "/proveedores",
    response_model=ProveedorOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_proveedor(
    proveedor_in: ProveedorCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Proveedor:
    """Registra proveedor; convierte duplicidad del nombre en conflicto HTTP."""
    proveedor = Proveedor(**proveedor_in.model_dump())
    db.add(proveedor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un proveedor con ese nombre",
        ) from None
    db.refresh(proveedor)
    return proveedor


@router.get("/proveedores", response_model=list[ProveedorOut])
def listar_proveedores(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[Proveedor]:
    """Lista el catálogo de proveedores para el administrador."""
    return db.query(Proveedor).order_by(Proveedor.id).all()


@router.post(
    "/productos",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_producto(
    producto_in: ProductoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Producto:
    """Crea producto central después de comprobar el proveedor."""
    if db.query(Proveedor.id).filter(Proveedor.id == producto_in.proveedor_id).first() is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    producto = Producto(**producto_in.model_dump())
    db.add(producto)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El código de producto ya está registrado",
        ) from None
    db.refresh(producto)
    return producto


@router.get("/productos", response_model=list[ProductoOut])
def listar_productos(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[Producto]:
    """Lista productos activos e inactivos para gestión administrativa."""
    return db.query(Producto).order_by(Producto.id).all()


@router.get("/productos/{producto_id}", response_model=ProductoOut)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Producto:
    """Obtiene el detalle de un producto por su identificador."""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.patch("/productos/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    producto_in: ProductoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Producto:
    """Actualiza datos permitidos; estado=false sirve para inactivar sin borrar."""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    values = producto_in.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=422, detail="Indica al menos un campo")
    if any(value is None for value in values.values()):
        raise HTTPException(status_code=422, detail="Los campos no pueden ser nulos")
    proveedor_id = values.get("proveedor_id")
    if proveedor_id is not None and (
        db.query(Proveedor.id).filter(Proveedor.id == proveedor_id).first() is None
    ):
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    for field, value in values.items():
        setattr(producto, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El código de producto ya está registrado",
        ) from None
    db.refresh(producto)
    return producto

"""Contratos de creación y consulta de pedidos y líneas de pedido."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PedidoLineaCreate(BaseModel):
    """Producto y cantidad entera de una línea inicial del pedido."""
    model_config = ConfigDict(extra="forbid")

    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0, strict=True)


class PedidoCreate(BaseModel):
    """Mesa y lista no vacía de productos para registrar un pedido."""
    model_config = ConfigDict(extra="forbid")

    mesa_id: int = Field(gt=0)
    productos: list[PedidoLineaCreate] = Field(min_length=1)


class PedidoProductoAdd(BaseModel):
    """Producto y cantidad para añadir a un pedido abierto."""
    model_config = ConfigDict(extra="forbid")

    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0, strict=True)


class LineaPedidoOut(BaseModel):
    """Detalle de pedido con precio aplicado y autor/fecha de la adición."""
    id: int
    producto_id: int
    codigo: str
    nombre: str
    cantidad: int
    precio_unitario: Decimal
    usuario_id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class PedidoOut(BaseModel):
    """Pedido y total calculado a partir de sus líneas."""
    id: int
    usuario_id: int
    sede_id: int
    mesa_id: int
    estado: str
    creado_en: datetime
    productos: list[LineaPedidoOut]
    total: Decimal

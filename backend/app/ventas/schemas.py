"""Contratos de creación y consulta de pedidos y líneas de pedido."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

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


class PagoCreate(BaseModel):
    """Medio de pago permitido para cerrar un pedido sin editar su valor."""
    model_config = ConfigDict(extra="forbid")

    medio_pago: Literal["EFECTIVO", "TARJETA"]


class PedidoPendienteOut(BaseModel):
    """Resumen de pedido abierto visible al cajero de la sede."""
    id: int
    usuario_id: int
    usuario_nombre: str
    sede_id: int
    mesa_id: int
    creado_en: datetime
    total: Decimal


class FacturaLineaOut(BaseModel):
    producto_id: int
    codigo: str
    nombre: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class FacturaOut(BaseModel):
    """Comprobante calculado a partir del pedido cerrado."""
    pedido_id: int
    sede_id: int
    mesa_id: int
    creado_en: datetime
    cerrado_en: datetime
    cerrado_por: int
    medio_pago: Literal["EFECTIVO", "TARJETA"]
    productos: list[FacturaLineaOut]
    total: Decimal


class ReporteVentaOut(BaseModel):
    """Agregado de venta por producto y sede con precios históricos."""
    producto_id: int
    codigo: str
    nombre: str
    cantidad: int
    valor_compra: Decimal
    precio_venta: Decimal
    valor_venta: Decimal
    ganancia: Decimal
    sede_id: int
    sede: str

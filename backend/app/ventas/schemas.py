from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PedidoLineaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0, strict=True)


class PedidoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mesa_id: int = Field(gt=0)
    productos: list[PedidoLineaCreate] = Field(min_length=1)


class PedidoProductoAdd(BaseModel):
    model_config = ConfigDict(extra="forbid")

    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0, strict=True)


class LineaPedidoOut(BaseModel):
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
    id: int
    usuario_id: int
    sede_id: int
    mesa_id: int
    estado: str
    creado_en: datetime
    productos: list[LineaPedidoOut]
    total: Decimal

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProveedorCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120)


class ProveedorOut(BaseModel):
    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class ProductoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: str = Field(min_length=1, max_length=40)
    nombre: str = Field(min_length=1, max_length=120)
    precio_venta: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    precio_compra: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    estado: bool
    proveedor_id: int = Field(gt=0)


class ProductoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: str | None = Field(None, min_length=1, max_length=40)
    nombre: str | None = Field(None, min_length=1, max_length=120)
    precio_venta: Decimal | None = Field(
        None, ge=0, max_digits=12, decimal_places=2
    )
    precio_compra: Decimal | None = Field(
        None, ge=0, max_digits=12, decimal_places=2
    )
    estado: bool | None = None
    proveedor_id: int | None = Field(None, gt=0)


class ProductoOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    precio_venta: Decimal
    precio_compra: Decimal
    estado: bool
    proveedor_id: int
    model_config = ConfigDict(from_attributes=True)

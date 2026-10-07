"""Contratos Pydantic de carga incremental y consulta de inventario."""

from pydantic import BaseModel, ConfigDict, Field


class InventarioIncrement(BaseModel):
    """Cantidad entera positiva que el administrador suma a una sede."""
    model_config = ConfigDict(extra="forbid")

    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0, strict=True)


class InventarioOut(BaseModel):
    """Existencia de un producto en una sede, con datos útiles de catálogo."""
    sede_id: int
    producto_id: int
    codigo: str
    nombre: str
    cantidad: int

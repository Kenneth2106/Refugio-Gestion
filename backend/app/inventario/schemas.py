from pydantic import BaseModel, ConfigDict, Field


class InventarioIncrement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0, strict=True)


class InventarioOut(BaseModel):
    sede_id: int
    producto_id: int
    codigo: str
    nombre: str
    cantidad: int

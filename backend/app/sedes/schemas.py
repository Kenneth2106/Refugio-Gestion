from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class MesaBase(BaseModel):
    numero: int = Field(gt=0)
    estado: bool = True

class MesaCreate(MesaBase):
    pass

class MesaUpdate(BaseModel):
    numero: int | None = Field(None, gt=0)
    estado: bool | None = None

class MesaOut(MesaBase):
    id: int
    sede_id: int
    estado_operativo: Literal["LIBRE", "OCUPADA"] = "LIBRE"
    pedido_abierto_id: int | None = None
    model_config = ConfigDict(from_attributes=True)

class SedeBase(BaseModel):
    codigo: str = Field(min_length=1, max_length=20)
    nombre: str = Field(min_length=1, max_length=100)
    direccion: str = Field(min_length=1, max_length=200)
    estado: bool = True

class SedeCreate(SedeBase):
    pass

class SedeUpdate(BaseModel):
    codigo: str | None = Field(None, min_length=1, max_length=20)
    nombre: str | None = Field(None, min_length=1, max_length=100)
    direccion: str | None = Field(None, min_length=1, max_length=200)
    estado: bool | None = None

class SedeOut(SedeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

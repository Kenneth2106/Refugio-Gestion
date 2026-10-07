"""Contratos Pydantic de sedes y mesas para la API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class MesaBase(BaseModel):
    """Campos compartidos de una mesa."""
    numero: int = Field(gt=0)
    estado: bool = True

class MesaCreate(MesaBase):
    """Datos de alta de mesa; la sede procede de la ruta."""
    pass

class MesaUpdate(BaseModel):
    """Campos opcionales para modificar o inactivar una mesa."""
    numero: int | None = Field(None, gt=0)
    estado: bool | None = None

class MesaOut(MesaBase):
    """Mesa con sede e indicador operativo LIBRE/OCUPADA calculado."""
    id: int
    sede_id: int
    estado_operativo: Literal["LIBRE", "OCUPADA"] = "LIBRE"
    pedido_abierto_id: int | None = None
    model_config = ConfigDict(from_attributes=True)

class SedeBase(BaseModel):
    """Datos compartidos de sede y sus validaciones."""
    codigo: str = Field(min_length=1, max_length=20)
    nombre: str = Field(min_length=1, max_length=100)
    direccion: str = Field(min_length=1, max_length=200)
    estado: bool = True

class SedeCreate(SedeBase):
    """Datos obligatorios para crear una sede."""
    pass

class SedeUpdate(BaseModel):
    """Campos opcionales de actualización de sede."""
    codigo: str | None = Field(None, min_length=1, max_length=20)
    nombre: str | None = Field(None, min_length=1, max_length=100)
    direccion: str | None = Field(None, min_length=1, max_length=200)
    estado: bool | None = None

class SedeOut(SedeBase):
    """Representación de una sede con su identificador."""
    id: int
    model_config = ConfigDict(from_attributes=True)

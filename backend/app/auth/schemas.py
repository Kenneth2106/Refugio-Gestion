"""Contratos de entrada y salida para autenticación y selección de sede."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


class LoginSchema(BaseModel):
    """Credenciales aceptadas por el endpoint de inicio de sesión."""
    model_config = ConfigDict(extra="forbid")

    identificacion: str = Field(min_length=1, max_length=30)
    password: SecretStr = Field(min_length=1, max_length=72)

    @field_validator("identificacion", mode="before")
    @classmethod
    def normalize_identification(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def validate_bcrypt_length(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().encode("utf-8")) > 72:
            raise ValueError("La contraseña supera el máximo permitido")
        return value


class TokenSchema(BaseModel):
    """Respuesta del login con token, tipo y destino inicial."""
    access_token: str
    token_type: str
    redirect_to: str


class CurrentUserSchema(BaseModel):
    """Perfil derivado de los datos vigentes del usuario y su sesión."""
    id: int
    identificacion: str
    nombre: str
    nombre_usuario: str
    email: EmailStr | None
    roles: list[str]
    sedes_ids: list[int]
    is_admin: bool
    expires_at: int
    sede_seleccionada_id: int | None = None


class SiteSelectionSchema(BaseModel):
    """Identificador de la sede que el usuario solicita seleccionar."""
    model_config = ConfigDict(extra="forbid")

    sede_id: int = Field(gt=0)
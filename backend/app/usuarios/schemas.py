from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


class UsuarioCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identificacion: str = Field(min_length=1, max_length=30)
    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=72)
    es_admin: bool = False
    es_mesero: bool = False
    es_cajero: bool = False
    sedes_ids: list[int] = Field(default_factory=list)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def validate_bcrypt_length(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().encode("utf-8")) > 72:
            raise ValueError("La contraseña supera el máximo permitido")
        return value


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    password: SecretStr | None = Field(None, min_length=8, max_length=72)
    es_admin: bool | None = None
    es_mesero: bool | None = None
    es_cajero: bool | None = None
    sedes_ids: list[int] | None = None
    estado: bool | None = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class UsuarioOut(BaseModel):
    id: int
    identificacion: str
    nombre: str
    email: str
    estado: bool
    es_admin: bool
    es_mesero: bool
    es_cajero: bool
    sedes_ids: list[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


class LoginSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: SecretStr = Field(min_length=1, max_length=72)

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


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    redirect_to: str
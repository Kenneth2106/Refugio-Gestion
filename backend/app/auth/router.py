import secrets
from dataclasses import dataclass
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.models import SesionActiva
from app.auth.schemas import LoginSchema, TokenSchema
from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token, verify_password
from app.core.settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    AUTH_COOKIE_NAME,
    COOKIE_SECURE,
)
from app.usuarios.models import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])
bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticación requerida o sesión vencida",
        headers={"WWW-Authenticate": "Bearer"},
    )


@dataclass(frozen=True)
class SesionAutenticada:
    usuario: Usuario
    jti: str


def get_current_session(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> SesionAutenticada:
    token = (
        credentials.credentials
        if credentials is not None
        else request.cookies.get(AUTH_COOKIE_NAME)
    )
    if not token:
        raise unauthorized()

    try:
        payload = decode_access_token(token)
    except JWTError:
        raise unauthorized() from None

    user_id = payload.get("user_id")
    subject = payload.get("sub")
    jti = payload.get("jti")
    if type(user_id) is not int or not isinstance(subject, str) or not isinstance(jti, str):
        raise unauthorized()

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if usuario is None or usuario.email != subject:
        raise unauthorized()
    if not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivado",
        )

    sesion = (
        db.query(SesionActiva)
        .filter(SesionActiva.usuario_id == usuario.id)
        .first()
    )
    if sesion is None or not secrets.compare_digest(sesion.jti, jti):
        raise unauthorized()

    return SesionAutenticada(usuario=usuario, jti=jti)


def get_current_user(
    session: SesionAutenticada = Depends(get_current_session),
) -> Usuario:
    return session.usuario


@router.post("/login", response_model=TokenSchema)
def login(
    credentials: LoginSchema,
    response: Response,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == str(credentials.email))
        .with_for_update()
        .first()
    )

    if usuario is None or not verify_password(
        credentials.password.get_secret_value(), usuario.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivado",
        )

    jti = secrets.token_urlsafe(32)
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.email, "user_id": usuario.id, "jti": jti},
        expires_delta=expires_delta,
    )

    sesion = db.query(SesionActiva).filter_by(usuario_id=usuario.id).first()
    if sesion is None:
        db.add(SesionActiva(usuario_id=usuario.id, jti=jti))
    else:
        sesion.jti = jti
    db.commit()

    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=access_token,
        max_age=int(expires_delta.total_seconds()),
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "redirect_to": "/dashboard",
    }


@router.post("/logout")
def logout(
    response: Response,
    session: SesionAutenticada = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    db.query(SesionActiva).filter(
        SesionActiva.usuario_id == session.usuario.id,
        SesionActiva.jti == session.jti,
    ).delete(synchronize_session=False)
    db.commit()
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return {"message": "Sesión cerrada correctamente"}
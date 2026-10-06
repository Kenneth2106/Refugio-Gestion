import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.models import SesionActiva
from app.auth.schemas import CurrentUserSchema, LoginSchema, TokenSchema
from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token, verify_password
from app.core.settings import (
    SESSION_INACTIVITY_MINUTES,
    SESSION_MAX_MINUTES,
    AUTH_COOKIE_NAME,
    COOKIE_SECURE,
)
from app.usuarios.models import Usuario, UsuarioSede
from app.sedes.models import Sede

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
    expires_at: int


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def has_active_site(db: Session, usuario_id: int) -> bool:
    return (
        db.query(UsuarioSede.usuario_id)
        .join(Sede, Sede.id == UsuarioSede.sede_id)
        .filter(UsuarioSede.usuario_id == usuario_id, Sede.estado.is_(True))
        .first()
        is not None
    )


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
    expires_at = payload.get("exp")
    if (
        type(user_id) is not int
        or not isinstance(subject, str)
        or not isinstance(jti, str)
        or type(expires_at) is not int
    ):
        raise unauthorized()

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if usuario is None or usuario.identificacion != subject:
        raise unauthorized()
    if not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivado",
        )
    if not usuario.es_admin and not has_active_site(db, usuario.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una sede activa asignada",
        )

    sesion = (
        db.query(SesionActiva)
        .filter(SesionActiva.usuario_id == usuario.id)
        .first()
    )
    if sesion is None or not secrets.compare_digest(sesion.jti, jti):
        raise unauthorized()

    now = datetime.now(timezone.utc)
    if now - as_utc(sesion.ultima_actividad) >= timedelta(minutes=SESSION_INACTIVITY_MINUTES):
        db.delete(sesion)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión cerrada por inactividad",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if now - as_utc(sesion.creada_en) >= timedelta(minutes=SESSION_MAX_MINUTES):
        db.delete(sesion)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sesion.ultima_actividad = now
    db.commit()
    return SesionAutenticada(usuario=usuario, jti=jti, expires_at=expires_at)


def get_current_user(
    session: SesionAutenticada = Depends(get_current_session),
) -> Usuario:
    return session.usuario


def require_admin(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    if not usuario.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador",
        )
    return usuario


def require_mesero(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    if not (usuario.es_admin or usuario.es_mesero):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de mesero",
        )
    return usuario


def require_cajero(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    if not (usuario.es_admin or usuario.es_cajero):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de cajero",
        )
    return usuario


@router.post("/login", response_model=TokenSchema)
def login(
    credentials: LoginSchema,
    response: Response,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    usuario = (
        db.query(Usuario)
        .filter(Usuario.identificacion == credentials.identificacion)
        .with_for_update()
        .first()
    )

    if usuario is None or not verify_password(
        credentials.password.get_secret_value(), usuario.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificación o contraseña incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivado",
        )
    if not usuario.es_admin and not has_active_site(db, usuario.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una sede activa asignada",
        )

    jti = secrets.token_urlsafe(32)
    expires_delta = timedelta(minutes=SESSION_MAX_MINUTES)
    roles = ["admin"] if usuario.es_admin else []
    if usuario.es_admin or usuario.es_mesero:
        roles.append("mesero")
    if usuario.es_admin or usuario.es_cajero:
        roles.append("cajero")
    if usuario.es_admin:
        sedes_ids = [row[0] for row in db.query(Sede.id).filter(Sede.estado.is_(True)).all()]
    else:
        sedes_ids = [assignment.sede_id for assignment in usuario.sedes]
    access_token = create_access_token(
        data={
            "sub": usuario.identificacion,
            "user_id": usuario.id,
            "jti": jti,
            "roles": roles,
            "sedes_ids": sedes_ids,
        },
        expires_delta=expires_delta,
    )

    sesion = db.query(SesionActiva).filter_by(usuario_id=usuario.id).first()
    now = datetime.now(timezone.utc)
    if sesion is None:
        db.add(
            SesionActiva(
                usuario_id=usuario.id,
                jti=jti,
                creada_en=now,
                ultima_actividad=now,
            )
        )
    else:
        sesion.jti = jti
        sesion.creada_en = now
        sesion.ultima_actividad = now
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


@router.get("/me", response_model=CurrentUserSchema)
def current_user(
    session: SesionAutenticada = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    usuario = session.usuario
    roles = ["admin"] if usuario.es_admin else []
    if usuario.es_admin or usuario.es_mesero:
        roles.append("mesero")
    if usuario.es_admin or usuario.es_cajero:
        roles.append("cajero")
    if usuario.es_admin:
        sedes_ids = [row[0] for row in db.query(Sede.id).filter(Sede.estado.is_(True)).all()]
    else:
        sedes_ids = [assignment.sede_id for assignment in usuario.sedes]
    return {
        "id": usuario.id,
        "identificacion": usuario.identificacion,
        "nombre": usuario.nombre,
        "nombre_usuario": usuario.nombre_usuario,
        "email": usuario.email,
        "roles": roles,
        "sedes_ids": sedes_ids,
        "is_admin": usuario.es_admin,
        "expires_at": session.expires_at,
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


@router.post("/ping")
def ping(
    session: SesionAutenticada = Depends(get_current_session),
) -> dict[str, str]:
    return {"message": "pong"}
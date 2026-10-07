"""Rutas de autenticación y dependencias reutilizables de rol/sede/sesión."""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.models import SesionActiva
from app.auth.schemas import (
    CurrentUserSchema,
    LoginSchema,
    SiteSelectionSchema,
    TokenSchema,
)
from app.core.clock import get_utc_now
from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token, verify_password
from app.core.settings import (
    AUTH_COOKIE_NAME,
    COOKIE_SECURE,
    SESSION_INACTIVITY_MINUTES,
    SESSION_MAX_MINUTES,
)
from app.sedes.models import Sede
from app.usuarios.models import Usuario, UsuarioSede

router = APIRouter(prefix="/auth", tags=["Autenticación"])
bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized(detail: str = "Autenticación requerida o sesión vencida") -> HTTPException:
    """Construye una respuesta uniforme para credenciales o sesiones inválidas."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


@dataclass(frozen=True)
class SesionAutenticada:
    """Contexto validado que una petición autenticada comparte con sus endpoints."""

    usuario: Usuario
    jti: str
    expires_at: int
    sede_seleccionada_id: int | None


def as_utc(value: datetime) -> datetime:
    """Normaliza una fecha con o sin tzinfo a UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def user_roles(usuario: Usuario) -> list[str]:
    """Deriva roles operativos desde los roles actuales guardados en base."""
    roles = ["admin"] if usuario.es_admin else []
    if usuario.es_admin or usuario.es_mesero:
        roles.append("mesero")
    if usuario.es_admin or usuario.es_cajero:
        roles.append("cajero")
    return roles


def authorized_site_ids(db: Session, usuario: Usuario) -> list[int]:
    """Lista sedes activas del usuario; el administrador tiene alcance global."""
    query = db.query(Sede.id).filter(Sede.estado.is_(True))
    if not usuario.es_admin:
        query = (
            query.join(UsuarioSede, UsuarioSede.sede_id == Sede.id)
            .filter(UsuarioSede.usuario_id == usuario.id)
        )
    return [site_id for (site_id,) in query.order_by(Sede.id).all()]


def site_is_authorized(db: Session, usuario: Usuario, sede_id: int) -> bool:
    """Comprueba el acceso vigente a una sede concreta."""
    query = db.query(Sede.id).filter(
        Sede.id == sede_id,
        Sede.estado.is_(True),
    )
    if not usuario.es_admin:
        query = query.join(
            UsuarioSede,
            UsuarioSede.sede_id == Sede.id,
        ).filter(UsuarioSede.usuario_id == usuario.id)
    return query.first() is not None


# Esta dependencia valida sesión, estado del usuario, roles/sedes actuales y ventanas de expiración.
def get_current_session(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    now: datetime = Depends(get_utc_now),
) -> SesionAutenticada:
    """Valida JWT, jti, usuario, inactividad y límite absoluto en cada petición."""
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
    if (
        type(user_id) is not int
        or not isinstance(subject, str)
        or not isinstance(jti, str)
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

    sesion = (
        db.query(SesionActiva)
        .filter(
            SesionActiva.usuario_id == usuario.id,
            SesionActiva.jti == jti,
            SesionActiva.activa.is_(True),
        )
        .with_for_update()
        .first()
    )
    if sesion is None:
        raise unauthorized()

    now = as_utc(now)
    login_at = as_utc(sesion.creada_en)
    last_activity = as_utc(sesion.ultima_actividad)
    if now - last_activity >= timedelta(minutes=SESSION_INACTIVITY_MINUTES):
        sesion.activa = False
        sesion.revocada_en = now
        db.commit()
        raise unauthorized("Sesión cerrada por inactividad")
    if now - login_at >= timedelta(minutes=SESSION_MAX_MINUTES):
        sesion.activa = False
        sesion.revocada_en = now
        db.commit()
        raise unauthorized("Sesión expirada")

    site_ids = authorized_site_ids(db, usuario)
    if not usuario.es_admin and not site_ids:
        sesion.activa = False
        sesion.revocada_en = now
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una sede activa asignada",
        )
    selected_site_id = sesion.sede_seleccionada_id
    if selected_site_id is not None and (
        selected_site_id not in site_ids
        or not site_is_authorized(db, usuario, selected_site_id)
    ):
        sesion.sede_seleccionada_id = None
        selected_site_id = None

    remaining = timedelta(minutes=SESSION_MAX_MINUTES) - (now - login_at)
    token_lifetime = min(
        timedelta(minutes=SESSION_INACTIVITY_MINUTES),
        remaining,
    )
    refreshed_token = create_access_token(
        data={
            "sub": usuario.identificacion,
            "user_id": usuario.id,
            "jti": jti,
            "roles": user_roles(usuario),
            "sedes_ids": site_ids,
        },
        expires_delta=token_lifetime,
        issued_at=now,
    )
    refreshed_exp = int((now + token_lifetime).timestamp())
    sesion.ultima_actividad = now
    db.commit()

    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=refreshed_token,
        max_age=max(1, int(token_lifetime.total_seconds())),
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    if credentials is not None:
        response.headers["X-Access-Token"] = refreshed_token

    return SesionAutenticada(
        usuario=usuario,
        jti=jti,
        expires_at=refreshed_exp,
        sede_seleccionada_id=selected_site_id,
    )


def get_current_user(
    session: SesionAutenticada = Depends(get_current_session),
) -> Usuario:
    """Extrae el usuario de la sesión que ya fue validada."""
    return session.usuario


def require_admin(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    """Permite continuar solo a cuentas administradoras."""
    if not usuario.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador",
        )
    return usuario


# Cada ruta reutiliza dependencias de rol para autorizar solicitudes en servidor.
def require_mesero(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    """Exige capacidad de mesero, incluida la concedida al administrador."""
    if not (usuario.es_admin or usuario.es_mesero):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de mesero",
        )
    return usuario


def require_cajero(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    """Exige capacidad de cajero, incluida la concedida al administrador."""
    if not (usuario.es_admin or usuario.es_cajero):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de cajero",
        )
    return usuario


def require_site_access(
    sede_id: int,
    session: SesionAutenticada = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> Sede:
    """Valida acceso a la sede de la ruta y la persiste como sede activa."""
    if not site_is_authorized(db, session.usuario, sede_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta sede",
        )
    if session.sede_seleccionada_id != sede_id:
        active_session = (
            db.query(SesionActiva)
            .filter(
                SesionActiva.usuario_id == session.usuario.id,
                SesionActiva.jti == session.jti,
                SesionActiva.activa.is_(True),
            )
            .one()
        )
        active_session.sede_seleccionada_id = sede_id
        db.commit()
    return db.query(Sede).filter(Sede.id == sede_id).one()


def require_selected_site(
    session: SesionAutenticada = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> Sede:
    """Exige una sede seleccionada y comprueba que siga autorizada."""
    selected_site_id = session.sede_seleccionada_id
    if selected_site_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Selecciona una sede para continuar",
        )
    return require_site_access(
        selected_site_id,
        session=session,
        db=db,
    )


@router.post("/login", response_model=TokenSchema)
def login(
    credentials: LoginSchema,
    response: Response,
    db: Session = Depends(get_db),
    now: datetime = Depends(get_utc_now),
) -> dict[str, str]:
    """Autentica, revoca sesiones anteriores y crea la nueva sesión/JWT."""
    # El login sustituye las sesiones activas previas y registra el nuevo jti en la base.
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

    site_ids = authorized_site_ids(db, usuario)
    if not usuario.es_admin and not site_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una sede activa asignada",
        )

    now = as_utc(now)
    db.query(SesionActiva).filter(
        SesionActiva.usuario_id == usuario.id,
        SesionActiva.activa.is_(True),
    ).update(
        {
            SesionActiva.activa: False,
            SesionActiva.revocada_en: now,
        },
        synchronize_session=False,
    )
    selected_site_id = site_ids[0] if len(site_ids) == 1 else None
    jti = secrets.token_urlsafe(32)
    lifetime = timedelta(
        minutes=min(SESSION_INACTIVITY_MINUTES, SESSION_MAX_MINUTES)
    )
    access_token = create_access_token(
        data={
            "sub": usuario.identificacion,
            "user_id": usuario.id,
            "jti": jti,
            "roles": user_roles(usuario),
            "sedes_ids": site_ids,
        },
        expires_delta=lifetime,
        issued_at=now,
    )
    db.add(
        SesionActiva(
            usuario_id=usuario.id,
            jti=jti,
            creada_en=now,
            ultima_actividad=now,
            activa=True,
            sede_seleccionada_id=selected_site_id,
        )
    )
    db.commit()

    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=access_token,
        max_age=int(lifetime.total_seconds()),
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"
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
    """Expone perfil, roles y sedes consultados desde la base de datos."""
    # El perfil se construye con datos actuales de base, no con los roles/sedes del JWT únicamente.
    usuario = session.usuario
    return {
        "id": usuario.id,
        "identificacion": usuario.identificacion,
        "nombre": usuario.nombre,
        "nombre_usuario": usuario.nombre_usuario,
        "email": usuario.email,
        "roles": user_roles(usuario),
        "sedes_ids": authorized_site_ids(db, usuario),
        "is_admin": usuario.es_admin,
        "expires_at": session.expires_at,
        "sede_seleccionada_id": session.sede_seleccionada_id,
    }


@router.post("/sede")
def select_site(
    selection: SiteSelectionSchema,
    session: SesionAutenticada = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    """Guarda en la sesión activa la sede de trabajo elegida."""
    # La sede elegida queda asociada a la sesión persistida y se revalida en las siguientes peticiones.
    if not site_is_authorized(db, session.usuario, selection.sede_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta sede",
        )
    active_session = (
        db.query(SesionActiva)
        .filter(
            SesionActiva.usuario_id == session.usuario.id,
            SesionActiva.jti == session.jti,
            SesionActiva.activa.is_(True),
        )
        .one()
    )
    active_session.sede_seleccionada_id = selection.sede_id
    db.commit()
    return {"sede_seleccionada_id": selection.sede_id}


@router.post("/logout")
def logout(
    response: Response,
    session: SesionAutenticada = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Revoca la fila de sesión y borra la cookie del navegador."""
    active_session = (
        db.query(SesionActiva)
        .filter(
            SesionActiva.usuario_id == session.usuario.id,
            SesionActiva.jti == session.jti,
            SesionActiva.activa.is_(True),
        )
        .first()
    )
    if active_session is not None:
        active_session.activa = False
        active_session.revocada_en = get_utc_now()
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
    _session: SesionAutenticada = Depends(get_current_session),
) -> dict[str, str]:
    """Verifica conectividad autenticada aplicando el control de sesión habitual."""
    return {"message": "pong"}

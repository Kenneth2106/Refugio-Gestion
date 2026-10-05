from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import get_password_hash
from app.auth.router import require_admin
from app.usuarios.models import Usuario, UsuarioSede
from app.sedes.models import Sede
from app.usuarios.schemas import UsuarioCreate, UsuarioUpdate, UsuarioOut

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def _build_out(usuario: Usuario) -> UsuarioOut:
    return UsuarioOut(
        id=usuario.id,
        identificacion=usuario.identificacion,
        nombre=usuario.nombre,
        email=usuario.email,
        estado=usuario.estado,
        es_admin=usuario.es_admin,
        es_mesero=usuario.es_mesero,
        es_cajero=usuario.es_cajero,
        sedes_ids=[us.sede_id for us in usuario.sedes],
    )


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    usuario_in: UsuarioCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    # Validar que al menos un rol esté activo
    if not any([usuario_in.es_admin, usuario_in.es_mesero, usuario_in.es_cajero]):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El usuario debe tener al menos un rol asignado",
        )

    # Validar existencia de sedes
    for sede_id in usuario_in.sedes_ids:
        sede = db.query(Sede).filter(Sede.id == sede_id, Sede.estado == True).first()
        if not sede:
            raise HTTPException(status_code=404, detail=f"Sede {sede_id} no encontrada o inactiva")

    nuevo = Usuario(
        identificacion=usuario_in.identificacion,
        nombre=usuario_in.nombre,
        email=str(usuario_in.email),
        hashed_password=get_password_hash(usuario_in.password.get_secret_value()),
        estado=True,
        es_admin=usuario_in.es_admin,
        es_mesero=usuario_in.es_mesero,
        es_cajero=usuario_in.es_cajero,
    )
    db.add(nuevo)
    try:
        db.flush()  # Para obtener el id antes de commit
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo o la identificación ya están registrados",
        )

    for sede_id in usuario_in.sedes_ids:
        db.add(UsuarioSede(usuario_id=nuevo.id, sede_id=sede_id))

    try:
        db.commit()
        db.refresh(nuevo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al guardar el usuario")

    return _build_out(nuevo)


@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    usuarios = db.query(Usuario).options(joinedload(Usuario.sedes)).all()
    return [_build_out(u) for u in usuarios]


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    usuario = db.query(Usuario).options(joinedload(Usuario.sedes)).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return _build_out(usuario)


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: int,
    usuario_in: UsuarioUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    usuario = db.query(Usuario).options(joinedload(Usuario.sedes)).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = usuario_in.model_dump(exclude_unset=True)
    sedes_ids = update_data.pop("sedes_ids", None)
    password = update_data.pop("password", None)

    if password is not None:
        usuario.hashed_password = get_password_hash(password.get_secret_value())

    for field, value in update_data.items():
        setattr(usuario, field, value)

    # Validar que quede al menos un rol
    if not any([usuario.es_admin, usuario.es_mesero, usuario.es_cajero]):
        raise HTTPException(
            status_code=422,
            detail="El usuario debe tener al menos un rol asignado",
        )

    if sedes_ids is not None:
        # Validar sedes
        for sede_id in sedes_ids:
            sede = db.query(Sede).filter(Sede.id == sede_id, Sede.estado == True).first()
            if not sede:
                raise HTTPException(status_code=404, detail=f"Sede {sede_id} no encontrada o inactiva")
        # Reemplazar asignaciones
        db.query(UsuarioSede).filter(UsuarioSede.usuario_id == usuario_id).delete()
        for sede_id in sedes_ids:
            db.add(UsuarioSede(usuario_id=usuario_id, sede_id=sede_id))

    try:
        db.commit()
        db.refresh(usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    return _build_out(usuario)


@router.patch("/{usuario_id}/inactivar", response_model=UsuarioOut)
def inactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    if usuario_id == admin.id:
        raise HTTPException(status_code=400, detail="No puedes inactivarte a ti mismo")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.estado = False
    db.commit()
    db.refresh(usuario)
    return _build_out(usuario)

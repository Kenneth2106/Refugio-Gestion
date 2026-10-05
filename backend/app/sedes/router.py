from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.auth.router import require_admin, get_current_user
from app.usuarios.models import Usuario
from app.sedes.models import Sede, Mesa
from app.sedes.schemas import SedeCreate, SedeUpdate, SedeOut, MesaCreate, MesaUpdate, MesaOut

router = APIRouter(prefix="/sedes", tags=["Sedes y Mesas"])


@router.post("/", response_model=SedeOut, status_code=status.HTTP_201_CREATED)
def crear_sede(
    sede_in: SedeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    sede = Sede(**sede_in.model_dump())
    db.add(sede)
    try:
        db.commit()
        db.refresh(sede)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El código de sede ya existe")
    return sede


@router.get("/", response_model=list[SedeOut])
def listar_sedes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    # Si es admin, ve todas. Si no, solo las que tiene asignadas.
    if current_user.es_admin:
        return db.query(Sede).all()
    else:
        # Se obtienen las sedes asignadas al usuario operativo
        return [us.sede for us in current_user.sedes]


@router.patch("/{sede_id}", response_model=SedeOut)
def actualizar_sede(
    sede_id: int,
    sede_in: SedeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    
    update_data = sede_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sede, field, value)
        
    try:
        db.commit()
        db.refresh(sede)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El código de sede ya existe")
    return sede


@router.post("/{sede_id}/mesas", response_model=MesaOut, status_code=status.HTTP_201_CREATED)
def crear_mesa(
    sede_id: int,
    mesa_in: MesaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
        
    # Verificar que el número de mesa no exista en la sede
    mesa_existente = db.query(Mesa).filter(Mesa.sede_id == sede_id, Mesa.numero == mesa_in.numero).first()
    if mesa_existente:
        raise HTTPException(status_code=400, detail="El número de mesa ya existe en esta sede")
        
    mesa = Mesa(sede_id=sede.id, **mesa_in.model_dump())
    db.add(mesa)
    db.commit()
    db.refresh(mesa)
    return mesa


@router.get("/{sede_id}/mesas", response_model=list[MesaOut])
def listar_mesas_sede(
    sede_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    # Validar acceso a la sede
    if not current_user.es_admin:
        if not any(us.sede_id == sede_id for us in current_user.sedes):
            raise HTTPException(status_code=403, detail="No tienes acceso a esta sede")
            
    return db.query(Mesa).filter(Mesa.sede_id == sede_id).all()


@router.patch("/mesas/{mesa_id}", response_model=MesaOut)
def actualizar_mesa(
    mesa_id: int,
    mesa_in: MesaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
        
    if mesa_in.numero is not None and mesa_in.numero != mesa.numero:
        mesa_existente = db.query(Mesa).filter(Mesa.sede_id == mesa.sede_id, Mesa.numero == mesa_in.numero).first()
        if mesa_existente:
            raise HTTPException(status_code=400, detail="El número de mesa ya existe en esta sede")

    update_data = mesa_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mesa, field, value)
        
    db.commit()
    db.refresh(mesa)
    return mesa

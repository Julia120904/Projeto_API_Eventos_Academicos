from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.v1.dependencies import get_current_user
from app.models import Event, Registration, User
from app.schemas import RegistrationCreate, RegistrationOut

router = APIRouter(prefix="/inscricoes", tags=["Inscrições"])

@router.post("", response_model=RegistrationOut, status_code=status.HTTP_201_CREATED)
def create_registration(
    data: RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin" and (
        current_user.role != "participante" or data.participant_id != current_user.id
    ):
        raise HTTPException(403, "Você só pode realizar inscrições em seu próprio nome.")
    participant = db.get(User, data.participant_id)
    event = db.get(Event, data.event_id)
    if not participant:
        raise HTTPException(404, "Participante não encontrado.")
    if participant.role != "participante":
        raise HTTPException(400, "Somente participantes podem realizar inscrições.")
    if not participant.active:
        raise HTTPException(400, "Usuário inativo não pode se inscrever.")
    if not event:
        raise HTTPException(404, "Evento não encontrado.")
    if event.status != "ativo":
        raise HTTPException(400, "Não é possível se inscrever em evento indisponível.")
    if db.query(Registration).filter(
        Registration.participant_id == data.participant_id,
        Registration.event_id == data.event_id,
        Registration.status == "ativa"
    ).first():
        raise HTTPException(400, "Usuário já está inscrito neste evento.")
    active_count = db.query(Registration).filter(
        Registration.event_id == data.event_id,
        Registration.status == "ativa"
    ).count()
    if active_count >= event.capacity:
        raise HTTPException(400, "A capacidade máxima do evento foi atingida.")
    reg = Registration(**data.model_dump())
    db.add(reg); db.commit(); db.refresh(reg)
    return reg

@router.get("", response_model=list[RegistrationOut])
def list_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("admin", "organizador"):
        raise HTTPException(403, "Somente administradores e organizadores podem consultar todas as inscrições.")
    return db.query(Registration).all()

@router.get("/{registration_id}", response_model=RegistrationOut)
def get_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reg = db.get(Registration, registration_id)
    if not reg:
        raise HTTPException(404, "Inscrição não encontrada.")
    if current_user.role not in ("admin", "organizador") and reg.participant_id != current_user.id:
        raise HTTPException(403, "Você não tem permissão para consultar esta inscrição.")
    return reg

@router.put("/{registration_id}/cancelar", response_model=RegistrationOut)
def cancel_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reg = db.get(Registration, registration_id)
    if not reg:
        raise HTTPException(404, "Inscrição não encontrada.")
    if current_user.role != "admin" and reg.participant_id != current_user.id:
        raise HTTPException(403, "Você não tem permissão para cancelar esta inscrição.")
    if reg.status == "cancelada":
        raise HTTPException(400, "A inscrição já está cancelada.")
    reg.status = "cancelada"
    db.commit(); db.refresh(reg)
    return reg

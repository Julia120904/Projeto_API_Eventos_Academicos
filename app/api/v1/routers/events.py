from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.v1.dependencies import get_current_user
from app.models import Category, Event, User
from app.schemas import EventCreate, EventOut

router = APIRouter(prefix="/eventos", tags=["Eventos"])

@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.event_date <= datetime.now():
        raise HTTPException(400, "A data do evento deve ser futura.")
    if current_user.role not in ("admin", "organizador"):
        raise HTTPException(403, "Somente organizadores ou administradores podem criar eventos.")
    if current_user.role == "organizador" and data.organizer_id != current_user.id:
        raise HTTPException(403, "Você só pode criar eventos em seu próprio nome.")
    organizer = db.get(User, data.organizer_id)
    category = db.get(Category, data.category_id)
    if not organizer:
        raise HTTPException(404, "Organizador não encontrado.")
    if organizer.role not in ("admin", "organizador"):
        raise HTTPException(400, "O usuário informado não possui perfil de organizador.")
    if not category:
        raise HTTPException(404, "Categoria não encontrada.")
    event = Event(**data.model_dump())
    db.add(event); db.commit(); db.refresh(event)
    return event

@router.get("", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).all()

@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Evento não encontrado.")
    return event

@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Evento não encontrado.")
    if current_user.role != "admin" and not (
        current_user.role == "organizador"
        and event.organizer_id == current_user.id
        and data.organizer_id == current_user.id
    ):
        raise HTTPException(403, "Você não tem permissão para alterar este evento.")
    if data.event_date <= datetime.now():
        raise HTTPException(400, "A data do evento deve ser futura.")
    for key, value in data.model_dump().items():
        setattr(event, key, value)
    db.commit(); db.refresh(event)
    return event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Evento não encontrado.")
    if current_user.role != "admin" and not (
        current_user.role == "organizador" and event.organizer_id == current_user.id
    ):
        raise HTTPException(403, "Você não tem permissão para excluir este evento.")
    db.delete(event); db.commit()

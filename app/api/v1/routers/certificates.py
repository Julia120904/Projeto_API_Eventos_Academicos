import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.v1.dependencies import get_current_user, require_roles
from app.models import Certificate, Event, Registration, User
from app.schemas import CertificateCreate, CertificateOut

router = APIRouter(prefix="/certificados", tags=["Certificados"])

@router.post("", response_model=CertificateOut, status_code=status.HTTP_201_CREATED)
def create_certificate(
    data: CertificateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "organizador")),
):
    participant = db.get(User, data.participant_id)
    event = db.get(Event, data.event_id)
    if not participant or participant.role != "participante":
        raise HTTPException(404, "Participante não encontrado.")
    if not event:
        raise HTTPException(404, "Evento não encontrado.")
    registration = db.query(Registration).filter(
        Registration.participant_id == data.participant_id,
        Registration.event_id == data.event_id,
        Registration.status == "ativa"
    ).first()
    if not registration:
        raise HTTPException(400, "Certificado só pode ser emitido para participante inscrito.")
    cert = Certificate(
        participant_id=data.participant_id,
        event_id=data.event_id,
        code=f"CERT-{uuid.uuid4().hex[:12].upper()}"
    )
    db.add(cert); db.commit(); db.refresh(cert)
    return cert

@router.get("", response_model=list[CertificateOut])
def list_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "organizador")),
):
    return db.query(Certificate).all()

@router.get("/{certificate_id}", response_model=CertificateOut)
def get_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cert = db.get(Certificate, certificate_id)
    if not cert:
        raise HTTPException(404, "Certificado não encontrado.")
    if current_user.role not in ("admin", "organizador") and cert.participant_id != current_user.id:
        raise HTTPException(403, "Você não tem permissão para consultar este certificado.")
    return cert

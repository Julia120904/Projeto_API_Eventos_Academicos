from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    role: str = Field(default="participante", pattern="^(admin|organizador|participante)$")
    active: bool = True

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str | None = None

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EventBase(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str | None = None
    event_date: datetime
    capacity: int = Field(gt=0)
    status: str = Field(default="ativo", pattern="^(ativo|cancelado|encerrado)$")
    organizer_id: int = Field(gt=0)
    category_id: int = Field(gt=0)

class EventCreate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class RegistrationCreate(BaseModel):
    participant_id: int = Field(gt=0)
    event_id: int = Field(gt=0)

class RegistrationOut(RegistrationCreate):
    id: int
    status: str
    registered_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CertificateCreate(BaseModel):
    participant_id: int = Field(gt=0)
    event_id: int = Field(gt=0)

class CertificateOut(CertificateCreate):
    id: int
    code: str
    issued_at: datetime
    model_config = ConfigDict(from_attributes=True)

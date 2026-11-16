from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.database.session import get_db
from app.models import User
from app.schemas import LoginInput, Token, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registrar", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(data: UserRegister, db: Session = Depends(get_db)):
    """Cadastra uma nova conta com perfil de participante."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    user = User(
        name=data.name,
        email=data.email,
        role="participante",
        active=True,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: LoginInput, db: Session = Depends(get_db)):
    """Autentica com e-mail e senha e retorna um JWT."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.active or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(str(user.id))
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserOut)
def authenticated_user(current_user: User = Depends(get_current_user)):
    """Retorna os dados do usuário identificado pelo token."""
    return current_user

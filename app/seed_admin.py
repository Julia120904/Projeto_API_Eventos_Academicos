"""Cria o primeiro administrador usando as variáveis ADMIN_* do arquivo .env."""
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models import User


def main():
    name = settings.admin_name
    email = settings.admin_email
    password = settings.admin_password

    if not email or not password:
        raise SystemExit(
            "Defina ADMIN_EMAIL e ADMIN_PASSWORD no arquivo .env antes de executar."
        )
    if len(password) < 8:
        raise SystemExit("ADMIN_PASSWORD deve ter pelo menos 8 caracteres.")

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.name = name
            user.role = "admin"
            user.active = True
            user.password_hash = hash_password(password)
            print(f"Administrador atualizado: {email}")
        else:
            user = User(
                name=name,
                email=email,
                role="admin",
                active=True,
                password_hash=hash_password(password),
            )
            db.add(user)
            print(f"Administrador criado: {email}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()

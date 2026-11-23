
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.session import Base, get_db
from app.core.security import hash_password
from app.models import User, Category, Event, Registration


# Banco temporário exclusivo para os testes
engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine_test,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def ambiente():
    Base.metadata.create_all(bind=engine_test)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestingSessionLocal() as db:
        admin = User(
            name="Administrador Teste",
            email="admin_teste@email.com",
            role="admin",
            active=True,
            password_hash=hash_password("Senha123!"),
        )

        organizador = User(
            name="Organizador Teste",
            email="organizador_teste@email.com",
            role="organizador",
            active=True,
            password_hash=hash_password("Senha123!"),
        )

        participante = User(
            name="Participante Teste",
            email="participante_teste@email.com",
            role="participante",
            active=True,
            password_hash=hash_password("Senha123!"),
        )

        outro_participante = User(
            name="Outro Participante",
            email="outro_teste@email.com",
            role="participante",
            active=True,
            password_hash=hash_password("Senha123!"),
        )

        db.add_all([
            admin,
            organizador,
            participante,
            outro_participante,
        ])
        db.commit()

        db.refresh(admin)
        db.refresh(organizador)
        db.refresh(participante)
        db.refresh(outro_participante)

        categoria = Category(
            name="Categoria Teste",
            description="Categoria criada para testes",
        )
        db.add(categoria)
        db.commit()
        db.refresh(categoria)

        evento = Event(
            title="Evento Teste",
            description="Evento criado para testes",
            event_date=datetime.now() + timedelta(days=10),
            capacity=20,
            status="ativo",
            organizer_id=organizador.id,
            category_id=categoria.id,
        )

        outro_evento = Event(
            title="Segundo Evento Teste",
            description="Evento para testar inscrição",
            event_date=datetime.now() + timedelta(days=15),
            capacity=20,
            status="ativo",
            organizer_id=organizador.id,
            category_id=categoria.id,
        )

        db.add_all([evento, outro_evento])
        db.commit()

        db.refresh(evento)
        db.refresh(outro_evento)

        inscricao = Registration(
            participant_id=participante.id,
            event_id=evento.id,
            status="ativa",
        )
        db.add(inscricao)
        db.commit()
        db.refresh(inscricao)

        dados = {
            "admin_id": admin.id,
            "organizador_id": organizador.id,
            "participante_id": participante.id,
            "outro_participante_id": outro_participante.id,
            "categoria_id": categoria.id,
            "evento_id": evento.id,
            "outro_evento_id": outro_evento.id,
            "inscricao_id": inscricao.id,
        }

    with TestClient(app) as client:
        yield {"client": client, **dados}

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_test)


def obter_token(client, email):
    resposta = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Senha123!",
        },
    )
    assert resposta.status_code == 200
    return resposta.json()["access_token"]


def cabecalho(token):
    return {"Authorization": f"Bearer {token}"}


def test_login_admin_sucesso(ambiente):
    resposta = ambiente["client"].post(
        "/api/v1/auth/login",
        json={
            "email": "admin_teste@email.com",
            "password": "Senha123!",
        },
    )
    assert resposta.status_code == 200
    assert "access_token" in resposta.json()


def test_login_senha_incorreta(ambiente):
    resposta = ambiente["client"].post(
        "/api/v1/auth/login",
        json={
            "email": "admin_teste@email.com",
            "password": "senha_errada",
        },
    )
    assert resposta.status_code == 401


def test_me_sem_token_retorna_401(ambiente):
    resposta = ambiente["client"].get("/api/v1/auth/me")
    assert resposta.status_code == 401


def test_admin_cria_categoria(ambiente):
    token = obter_token(
        ambiente["client"],
        "admin_teste@email.com",
    )
    resposta = ambiente["client"].post(
        "/api/v1/categorias",
        json={
            "name": "Nova Categoria",
            "description": "Criada pelo administrador",
        },
        headers=cabecalho(token),
    )
    assert resposta.status_code == 201


def test_participante_nao_cria_categoria(ambiente):
    token = obter_token(
        ambiente["client"],
        "participante_teste@email.com",
    )
    resposta = ambiente["client"].post(
        "/api/v1/categorias",
        json={"name": "Categoria Proibida"},
        headers=cabecalho(token),
    )
    assert resposta.status_code == 403


def test_organizador_cria_evento_proprio(ambiente):
    token = obter_token(
        ambiente["client"],
        "organizador_teste@email.com",
    )
    resposta = ambiente["client"].post(
        "/api/v1/eventos",
        json={
            "title": "Evento Novo",
            "description": "Evento de teste",
            "event_date": (
                datetime.now() + timedelta(days=20)
            ).isoformat(),
            "capacity": 30,
            "status": "ativo",
            "organizer_id": ambiente["organizador_id"],
            "category_id": ambiente["categoria_id"],
        },
        headers=cabecalho(token),
    )
    assert resposta.status_code == 201


def test_participante_nao_cria_evento(ambiente):
    token = obter_token(
        ambiente["client"],
        "participante_teste@email.com",
    )
    resposta = ambiente["client"].post(
        "/api/v1/eventos",
        json={
            "title": "Evento Proibido",
            "event_date": (
                datetime.now() + timedelta(days=20)
            ).isoformat(),
            "capacity": 10,
            "status": "ativo",
            "organizer_id": ambiente["organizador_id"],
            "category_id": ambiente["categoria_id"],
        },
        headers=cabecalho(token),
    )
    assert resposta.status_code == 403


def test_participante_nao_se_inscreve_por_outro(ambiente):
    token = obter_token(
        ambiente["client"],
        "participante_teste@email.com",
    )
    resposta = ambiente["client"].post(
        "/api/v1/inscricoes",
        json={
            "participant_id": ambiente["outro_participante_id"],
            "event_id": ambiente["outro_evento_id"],
        },
        headers=cabecalho(token),
    )
    assert resposta.status_code == 403


def test_participante_nao_lista_todas_inscricoes(ambiente):
    token = obter_token(
        ambiente["client"],
        "participante_teste@email.com",
    )
    resposta = ambiente["client"].get(
        "/api/v1/inscricoes",
        headers=cabecalho(token),
    )
    assert resposta.status_code == 403


def test_participante_consulta_propria_inscricao(ambiente):
    token = obter_token(
        ambiente["client"],
        "participante_teste@email.com",
    )
    resposta = ambiente["client"].get(
        f"/api/v1/inscricoes/{ambiente['inscricao_id']}",
        headers=cabecalho(token),
    )
    assert resposta.status_code == 200


def test_eventos_publicos_sem_token(ambiente):
    resposta = ambiente["client"].get("/api/v1/eventos")
    assert resposta.status_code == 200

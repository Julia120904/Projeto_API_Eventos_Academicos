# API de Gestão de Eventos Acadêmicos

MVP da Primeira Entrega da disciplina.

## Stack
FastAPI, PostgreSQL, SQLAlchemy, Alembic e Pydantic.

## Como executar
1. Instale Python 3.11+.
2. Crie um ambiente virtual: `python -m venv .venv`
3. Ative o ambiente.
4. Instale: `pip install -r requirements.txt`
5. Copie `.env.example` para `.env`.
6. Inicie o PostgreSQL com `docker compose up -d`.
7. Execute a migration: `alembic upgrade head`
8. Inicie a API: `uvicorn app.main:app --reload`
9. Abra `http://127.0.0.1:8000/docs`.

## Rotas principais
- `/api/v1/usuarios`
- `/api/v1/categorias`
- `/api/v1/eventos`
- `/api/v1/inscricoes`
- `/api/v1/certificados`

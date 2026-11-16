from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description=(
        "API de gerenciamento de eventos acadêmicos com CRUDs, autenticação JWT, "
        "hash seguro de senhas e controle de acesso por perfil."
    ),
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["Saúde"])
def root():
    return {
        "message": "API de Gestão de Eventos Acadêmicos funcionando.",
        "version": "2.0.0",
    }

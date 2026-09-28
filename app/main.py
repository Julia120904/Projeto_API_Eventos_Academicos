from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="MVP da API para gerenciamento de eventos acadêmicos, inscrições e certificados."
)

app.include_router(api_router, prefix=settings.api_prefix)

@app.get("/", tags=["Saúde"])
def root():
    return {"message": "API de Gestão de Eventos Acadêmicos funcionando."}

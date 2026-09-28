from fastapi import APIRouter
from app.api.v1.routers import users, categories, events, registrations, certificates

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(events.router)
api_router.include_router(registrations.router)
api_router.include_router(certificates.router)

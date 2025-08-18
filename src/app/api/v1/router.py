from app.api.v1.endpoints import notes
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(notes.router)

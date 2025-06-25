from fastapi import APIRouter
from app.api.routers.chat import router as chat_router

api_router = APIRouter(prefix="/chat")
api_router.include_router(chat_router, tags=["chat"])

from fastapi import APIRouter

from .controller.auth_controller import router as auth_router
from .controller.message_controller import router as message_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(message_router, prefix="/chat", tags=["Chat"])



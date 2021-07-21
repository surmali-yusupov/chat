from .user.views import router as user_router
from .chat.views import router as chat_router
from fastapi import APIRouter

router = APIRouter(prefix='/api', tags=['api'])

router.include_router(user_router)
router.include_router(chat_router)

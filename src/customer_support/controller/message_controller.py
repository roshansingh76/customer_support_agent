
from fastapi import APIRouter,status 
from ..models.message_model import Chat
router =APIRouter()


@router.post("/message",status_code=status.HTTP_200_OK)
async def message(data:Chat):

    return {}
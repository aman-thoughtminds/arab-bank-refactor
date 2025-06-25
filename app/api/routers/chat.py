import uuid
from fastapi import APIRouter
from app.agent.interface import generate_chat_response
from app.schemas.chat_response import MessagesResponse

router = APIRouter()


@router.post("/", response_model=MessagesResponse)
async def chat(query: str):
    """ """
    chat_response = await generate_chat_response(
        user_query=query, thread_id=str(uuid.uuid4())
    )
    return chat_response

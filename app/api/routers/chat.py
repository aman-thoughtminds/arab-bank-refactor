import uuid
from fastapi import APIRouter
from app.agent.service import generate_chat_response
from app.schemas.chat_response import MessagesResponse, ChatRequest


router = APIRouter()


@router.post("/", response_model=MessagesResponse)
async def chat(request: ChatRequest) -> MessagesResponse:
    """ """
    chat_response = await generate_chat_response(
        user_query=request.query, thread_id=str(uuid.uuid4())
    )
    return chat_response

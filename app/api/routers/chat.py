import uuid
from fastapi import APIRouter
from app.agent.service import generate_chat_response, generate_assit_agent_response
from app.schemas.chat_response import MessagesResponse, ChatRequest


router = APIRouter()


@router.post("/", response_model=MessagesResponse)
async def chat(request: ChatRequest) -> MessagesResponse:
    """ """
    chat_response = await generate_chat_response(
        user_query=request.query, thread_id=str(uuid.uuid4())
    )
    return chat_response


@router.post("/assit_agent_mail", response_model=MessagesResponse)
async def mail_assit(request: ChatRequest) -> MessagesResponse:
    """"""
    chat_response = await generate_assit_agent_response(
        user_query=request.query, thread_id=str(uuid.uuid4())
    )
    return chat_response
